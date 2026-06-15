#!/usr/bin/env python3
"""Static site generator for dariohug.ch.

Turns plain Markdown (content/) and folders of files (documents/) into a static
website in _site/, using the HTML templates in templates/ and the stylesheet in
static/. There is no framework and no magic: read this file top to bottom and
you know everything the site does.

Usage:
    pip install -r requirements.txt
    python build.py                      # writes the site into _site/
    python -m http.server -d _site 8000  # preview at http://localhost:8000

Add content by committing files:
  * a blog post   -> content/blog/YYYY-MM-DD-title.md
  * a document    -> documents/<school>/<course>/<file>
  * a carbonara   -> carbomap/restaurants/<name>.md (+ photo in carbomap/images/)
  * a new page    -> content/pages/<name>.md
Then push; the GitHub Action rebuilds and deploys.

The Google Maps key is read from the GOOGLE_MAPS_API_KEY environment variable
at build time (set as a GitHub Actions secret); it is never stored in the repo.
Without it the build still works — the Carbomap list view and filters function,
only the map itself is disabled.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
from email.utils import format_datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_for_filename
from pygments.util import ClassNotFound

# --------------------------------------------------------------------------- #
# Paths & configuration
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DOCUMENTS = ROOT / "documents"
CARBOMAP = ROOT / "carbomap"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUTPUT = ROOT / "_site"

# Files that describe a folder / keep it in git but should not be listed.
IGNORE_NAMES = {".gitkeep", "README.md", ".DS_Store"}

# Extensions we render inline with syntax highlighting (besides PDFs/images).
CODE_EXTS = {
    ".py", ".js", ".mjs", ".ts", ".jsx", ".tsx", ".c", ".h", ".cpp", ".hpp",
    ".cc", ".java", ".rs", ".go", ".rb", ".php", ".sh", ".bash", ".zsh",
    ".sql", ".html", ".css", ".scss", ".json", ".yml", ".yaml", ".toml",
    ".ini", ".cfg", ".txt", ".md", ".tex", ".m", ".r", ".jl", ".kt", ".swift",
    ".cs", ".pl", ".lua", ".vhd", ".vhdl", ".v", ".asm", ".csv", ".xml",
}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
MAX_INLINE_BYTES = 512 * 1024  # don't try to syntax-highlight huge files


def load_config() -> dict:
    with open(ROOT / "site.yml", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# --------------------------------------------------------------------------- #
# Markdown & front matter
# --------------------------------------------------------------------------- #

_md = markdown.Markdown(
    extensions=[
        "fenced_code", "codehilite", "tables", "toc", "sane_lists", "attr_list",
    ],
    extension_configs={
        "codehilite": {"guess_lang": False, "css_class": "highlight"},
        "toc": {"permalink": False},
    },
)


def render_markdown(text: str) -> str:
    _md.reset()
    return _md.convert(text)


def parse_front_matter(text: str):
    """Split a leading `--- ... ---` YAML block from the Markdown body."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            return meta, parts[2].lstrip("\n")
    return {}, text


def read_doc(path: Path):
    """Read a Markdown file, returning (meta, rendered_html, raw_body)."""
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(raw)
    return meta, render_markdown(body), body


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def prettify(name: str) -> str:
    """Turn a folder/file slug into a human label, keeping ACRONYMS intact."""
    words = re.split(r"[-_\s]+", name.strip())
    out = []
    for w in words:
        if not w:
            continue
        out.append(w if (w.isupper() or any(c.isdigit() for c in w)) else w.capitalize())
    return " ".join(out) or name


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"[^a-z0-9-]", "", value)
    return re.sub(r"-{2,}", "-", value).strip("-") or "item"


def human_size(num: int) -> str:
    size = float(num)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def to_date(value) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if value:
        return dt.date.fromisoformat(str(value)[:10])
    return dt.date.today()


def youtube_id(value) -> str:
    """Accept a full YouTube URL or a bare 11-char id; return the id."""
    value = str(value).strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/|/v/)([A-Za-z0-9_-]{11})", value)
    return m.group(1) if m else ""


def first_paragraph(html_text: str) -> str:
    m = re.search(r"<p>(.*?)</p>", html_text, re.S)
    if not m:
        return ""
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()


# --------------------------------------------------------------------------- #
# Output helpers
# --------------------------------------------------------------------------- #

class Builder:
    def __init__(self, config: dict):
        self.config = config
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.globals["site"] = config
        self.env.globals["now_year"] = dt.date.today().year
        self.env.globals["is_active"] = self._is_active

    @staticmethod
    def _is_active(nav_path: str, current_path: str) -> bool:
        if nav_path == "/":
            return current_path == "/"
        return current_path == nav_path or current_path.startswith(nav_path)

    def render(self, out_relpath, template, **ctx):
        ctx.setdefault("current_path", "/")
        html_out = self.env.get_template(template).render(**ctx)
        dest = OUTPUT / out_relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")

    # ----- static assets ------------------------------------------------- #
    def copy_static(self):
        if STATIC.exists():
            shutil.copytree(STATIC, OUTPUT, dirs_exist_ok=True)
        css_dir = OUTPUT / "css"
        css_dir.mkdir(parents=True, exist_ok=True)
        pygments_css = HtmlFormatter(style="default").get_style_defs(".highlight")
        (css_dir / "pygments.css").write_text(pygments_css, encoding="utf-8")
        # Custom-domain binding + disable Jekyll on the deployed artifact.
        if (ROOT / "CNAME").exists():
            shutil.copy2(ROOT / "CNAME", OUTPUT / "CNAME")
        (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")

    # ----- simple pages --------------------------------------------------- #
    def build_pages(self):
        pages_dir = CONTENT / "pages"
        if not pages_dir.exists():
            return
        for md_file in sorted(pages_dir.glob("*.md")):
            meta, body_html, _ = read_doc(md_file)
            title = meta.get("title", prettify(md_file.stem))
            if md_file.stem == "index":
                self.render(
                    "index.html", "home.html",
                    page={"title": title}, content=body_html,
                    posts=self.recent_posts, current_path="/",
                )
            else:
                self.render(
                    f"{md_file.stem}/index.html", "page.html",
                    page={"title": title}, content=body_html,
                    current_path=f"/{md_file.stem}/",
                )

    # ----- blog ----------------------------------------------------------- #
    def collect_posts(self):
        blog_dir = CONTENT / "blog"
        posts = []
        if not blog_dir.exists():
            self.posts = []
            self.recent_posts = []
            return
        for md_file in sorted(blog_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            meta, body_html, _ = read_doc(md_file)
            if meta.get("draft"):
                continue
            stem = md_file.stem
            m = re.match(r"(\d{4}-\d{2}-\d{2})[-_]?(.*)", stem)
            name_date, rest = (m.group(1), m.group(2)) if m else (None, stem)
            date = to_date(meta.get("date") or name_date)
            slug = slugify(meta.get("slug") or rest or stem)
            summary = meta.get("summary") or first_paragraph(body_html)
            posts.append({
                "title": meta.get("title", prettify(slug)),
                "date": date,
                "date_iso": date.isoformat(),
                "tags": meta.get("tags") or [],
                "url": f"/blog/{slug}/",
                "slug": slug,
                "html": body_html,
                "summary": summary,
            })
        posts.sort(key=lambda p: p["date"], reverse=True)
        self.posts = posts
        self.recent_posts = posts[:6]

    def build_blog(self):
        for post in self.posts:
            self.render(
                f"blog/{post['slug']}/index.html", "post.html",
                page={"title": post["title"]}, post=post,
                current_path="/blog/",
            )
        self.render(
            "blog/index.html", "blog_index.html",
            page={"title": "Blog"}, posts=self.posts, current_path="/blog/",
        )
        self.build_feed()

    def build_feed(self):
        base = self.config.get("url", "").rstrip("/")
        items = []
        for post in self.posts[:20]:
            pub = format_datetime(
                dt.datetime.combine(post["date"], dt.time(12, 0), dt.timezone.utc)
            )
            items.append({
                "title": post["title"],
                "link": base + post["url"],
                "guid": base + post["url"],
                "pub_date": pub,
                "description": post["summary"] or post["title"],
            })
        self.render("feed.xml", "feed.xml", items=items, base=base)

    # ----- theater -------------------------------------------------------- #
    def build_theater(self):
        src = CONTENT / "theater.md"
        if not src.exists():
            return
        meta, body_html, _ = read_doc(src)
        videos = []
        for v in meta.get("videos") or []:
            vid = youtube_id(v.get("url") or v.get("id") or "")
            if not vid:
                continue
            videos.append({
                "id": vid,
                "title": v.get("title", ""),
                "description": v.get("description", ""),
            })
        self.render(
            "theater/index.html", "theater.html",
            page={"title": meta.get("title", "Theater")},
            content=body_html, videos=videos, current_path="/theater/",
        )

    # ----- carbomap ------------------------------------------------------- #
    def build_carbomap(self):
        """Compile carbomap/restaurants/*.md into data.json + the map page."""
        rest_dir = CARBOMAP / "restaurants"
        restaurants = []
        if rest_dir.exists():
            for md_file in sorted(rest_dir.glob("*.md")):
                if md_file.name.startswith("_") or md_file.name == "README.md":
                    continue
                meta, note_html, _ = read_doc(md_file)
                if meta.get("draft"):
                    continue
                lat, lng = meta.get("lat"), meta.get("lng")
                if lat is None or lng is None:
                    print(f"  ! skipping {md_file.name}: missing lat/lng")
                    continue
                image_url = None
                image = meta.get("image")
                if image and (CARBOMAP / "images" / image).exists():
                    image_url = "/carbomap/images/" + image
                restaurants.append({
                    "slug": slugify(meta.get("name", md_file.stem)),
                    "name": meta.get("name", prettify(md_file.stem)),
                    "lat": float(lat),
                    "lng": float(lng),
                    "city": meta.get("city", ""),
                    "country": meta.get("country", ""),
                    "rating": float(meta.get("rating", 0) or 0),
                    "price": meta.get("price"),
                    "currency": meta.get("currency", ""),
                    "guanciale": bool(meta.get("guanciale", False)),
                    "cream": bool(meta.get("cream", False)),
                    "image": image_url,
                    "date": str(meta.get("date")) if meta.get("date") else "",
                    "note": note_html,
                })
        restaurants.sort(key=lambda r: (-r["rating"], r["name"].lower()))

        # Copy the photos, write the data file the page fetches, render the page.
        if (CARBOMAP / "images").exists():
            shutil.copytree(CARBOMAP / "images", OUTPUT / "carbomap" / "images",
                            dirs_exist_ok=True)
        data_path = OUTPUT / "carbomap" / "data.json"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(
            json.dumps(restaurants, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self.carbomap_count = len(restaurants)
        self.render(
            "carbomap/index.html", "carbomap.html",
            page={"title": "Carbomap"}, count=len(restaurants),
            maps_api_key=os.environ.get("GOOGLE_MAPS_API_KEY", ""),
            current_path="/carbomap/",
        )

    # ----- documents ------------------------------------------------------ #
    def folder_meta(self, directory: Path):
        readme = directory / "README.md"
        if readme.exists():
            meta, body_html, _ = read_doc(readme)
            return meta.get("title"), body_html
        return None, ""

    def build_documents(self):
        if not DOCUMENTS.exists():
            return
        self._build_dir(DOCUMENTS, Path("documents"), is_root=True)

    def _build_dir(self, src_dir: Path, rel: Path, is_root: bool):
        entries = sorted(src_dir.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        subdirs = [p for p in entries if p.is_dir() and not p.name.startswith(".")]
        files = [p for p in entries
                 if p.is_file() and p.name not in IGNORE_NAMES and not p.name.startswith(".")]

        title, desc_html = self.folder_meta(src_dir)
        page_title = "Notes & Documents" if is_root else (title or prettify(src_dir.name))

        folders = []
        for d in subdirs:
            child_rel = rel / d.name
            child_title, _ = self.folder_meta(d)
            n_sub = sum(1 for p in d.iterdir() if p.is_dir() and not p.name.startswith("."))
            n_file = sum(1 for p in d.iterdir()
                         if p.is_file() and p.name not in IGNORE_NAMES and not p.name.startswith("."))
            folders.append({
                "name": child_title or prettify(d.name),
                "url": "/" + str(child_rel).replace("\\", "/") + "/",
                "n_sub": n_sub,
                "n_file": n_file,
            })
            self._build_dir(d, child_rel, is_root=False)

        file_entries = [self._build_file(f, rel) for f in files]

        self.render(
            str(rel / "index.html").replace("\\", "/"), "docs_dir.html",
            page={"title": page_title}, description=desc_html,
            folders=folders, files=file_entries, is_root=is_root,
            breadcrumbs=self._breadcrumbs(rel), current_path="/documents/",
        )

    def _build_file(self, src: Path, rel: Path):
        """Copy a document into _site and, where useful, make a viewer page."""
        dest_dir = OUTPUT / rel
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest_dir / src.name)

        ext = src.suffix.lower()
        size = src.stat().st_size
        raw_url = "/" + str(rel / src.name).replace("\\", "/")
        entry = {
            "name": src.name,
            "size": human_size(size),
            "ext": ext.lstrip(".").upper() or "FILE",
            "download_url": raw_url,
            "view_url": None,
        }

        if ext == ".pdf":
            view_rel = rel / (src.name + ".html")
            self.render(
                str(view_rel).replace("\\", "/"), "file_view.html",
                page={"title": src.name}, kind="pdf", raw_url=raw_url,
                filename=src.name, code_html=None,
                breadcrumbs=self._breadcrumbs(rel), current_path="/documents/",
            )
            entry["view_url"] = "/" + str(view_rel).replace("\\", "/")
        elif ext in IMAGE_EXTS:
            entry["view_url"] = raw_url
        elif ext in CODE_EXTS and size <= MAX_INLINE_BYTES:
            code_html = self._highlight(src)
            if code_html is not None:
                view_rel = rel / (src.name + ".html")
                self.render(
                    str(view_rel).replace("\\", "/"), "file_view.html",
                    page={"title": src.name}, kind="code", raw_url=raw_url,
                    filename=src.name, code_html=code_html,
                    breadcrumbs=self._breadcrumbs(rel), current_path="/documents/",
                )
                entry["view_url"] = "/" + str(view_rel).replace("\\", "/")
        return entry

    @staticmethod
    def _highlight(src: Path):
        try:
            text = src.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None
        try:
            lexer = get_lexer_for_filename(src.name, text)
        except ClassNotFound:
            lexer = TextLexer()
        from pygments import highlight
        return highlight(text, lexer, HtmlFormatter(cssclass="highlight"))

    @staticmethod
    def _breadcrumbs(rel: Path):
        parts = rel.parts  # ('documents', 'school', 'course')
        crumbs = []
        acc = ""
        for i, part in enumerate(parts):
            acc += "/" + part
            label = "Notes" if i == 0 else prettify(part)
            crumbs.append({"label": label, "url": acc + "/"})
        return crumbs


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def main():
    config = load_config()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    builder = Builder(config)
    builder.copy_static()
    builder.collect_posts()   # must run before build_pages (home shows posts)
    builder.build_pages()
    builder.build_blog()
    builder.build_theater()
    builder.build_carbomap()
    builder.build_documents()

    print(
        f"Built site into {OUTPUT}/ "
        f"({len(builder.posts)} blog post(s), "
        f"{builder.carbomap_count} restaurant(s))."
    )


if __name__ == "__main__":
    main()
