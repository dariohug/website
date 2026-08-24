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
  * a new page    -> content/pages/<name>.md  (published at /<name>/)
  * a document    -> documents/<school>/<course>/<file>
  * a carbonara   -> carbomap/restaurants/<name>.md (+ photo in carbomap/images/)
  * a performance -> a video entry in content/theater.md
Then push; the GitHub Action rebuilds and deploys.

PDFs, code files and Jupyter notebooks in documents/ get a viewer page of their
own. A folder README.md can put one of its files at the top of the folder page
with `featured: <filename>` (plus optional `featured_title` / `featured_note`)
in its front matter — see documents/university/simulations_natural_sciences_I.

The Google Maps key is read from the GOOGLE_MAPS_API_KEY environment variable
at build time (set as a GitHub Actions secret); it is never stored in the repo.
Without it the build still works — the Carbomap list view and filters function,
only the map itself is disabled.
"""

from __future__ import annotations

import base64
import datetime as dt
import html
import json
import os
import re
import shutil
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
    ".cs", ".pl", ".lua", ".vhd", ".vhdl", ".v", ".asm", ".csv", ".dat", ".xml",
}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
VIDEO_EXTS = {".mp4", ".webm", ".ogv"}
MAX_INLINE_BYTES = 512 * 1024  # don't try to syntax-highlight huge files

# Jupyter output that is longer than this many lines is shown head-and-tail
# only; a few notebooks print megabytes of arrays while debugging.
MAX_OUTPUT_LINES = 40


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


def youtube_start(value) -> int:
    """Seconds to start a YouTube embed at, from a `t=90s`/`t=90`/`start=90` URL."""
    m = re.search(r"[?&](?:t|start)=(\d+)h?(\d+)?m?(\d+)?s?", str(value))
    if not m:
        return 0
    if m.group(2) or m.group(3):  # h/m/s form, e.g. t=1h2m3s
        h, mi, sec = (int(g or 0) for g in m.groups())
        return h * 3600 + mi * 60 + sec
    return int(m.group(1))


def youtube_id(value) -> str:
    """Accept a full YouTube URL or a bare 11-char id; return the id."""
    value = str(value).strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/|/v/)([A-Za-z0-9_-]{11})", value)
    return m.group(1) if m else ""


def folder_videos(meta: dict):
    """`videos:` in a folder README — YouTube results that belong to a course."""
    out = []
    for v in meta.get("videos") or []:
        vid = youtube_id(v.get("url") or v.get("id") or "")
        if vid:
            out.append({
                "id": vid,
                "title": v.get("title", ""),
                "description": v.get("description", ""),
                "start": v.get("start") or youtube_start(v.get("url") or ""),
            })
    return out


# --------------------------------------------------------------------------- #
# Jupyter notebooks
# --------------------------------------------------------------------------- #
#
# Notebooks are rendered here directly from their JSON rather than with
# nbconvert, so the build keeps its four small dependencies: markdown cells go
# through the same Markdown renderer as the rest of the site, code cells
# through Pygments, and stored outputs (images, text, HTML tables) are inlined.
# TeX between $...$ / $$...$$ is pulled out before the Markdown pass — Markdown
# would otherwise eat the underscores — and put back for MathJax, which is
# loaded from a CDN on notebook pages only. Plots are written out as real image
# files next to the notebook instead of base64 blobs, so that a page showing a
# notebook twice (the folder page and the notebook page) downloads them once.

# $$...$$ or $...$; an inline formula may wrap over several lines (the cases
# environments in these notebooks do) but never across a blank line.
_MATH_RE = re.compile(r"\$\$(.+?)\$\$|\$((?:[^$\n]|\n(?!\s*\n))+?)\$", re.DOTALL)


def _protect_math(text: str):
    """Replace TeX spans with placeholders Markdown will not touch."""
    spans = []

    def stash(m):
        display = m.group(1) is not None
        body = html.escape((m.group(1) or m.group(2)).strip())
        spans.append(f"\\[{body}\\]" if display else f"\\({body}\\)")
        return f"mathspan{len(spans) - 1}xend"

    return _MATH_RE.sub(stash, text), spans


def render_markdown_with_math(text: str) -> str:
    text, spans = _protect_math(text)
    out = render_markdown(text)
    for i, span in enumerate(spans):
        out = out.replace(f"mathspan{i}xend", span)
    return out


def _clip(text: str) -> str:
    """Shorten runaway cell output to a readable head and tail."""
    lines = text.splitlines()
    if len(lines) <= MAX_OUTPUT_LINES:
        return text
    head, tail = lines[:MAX_OUTPUT_LINES - 10], lines[-10:]
    hidden = len(lines) - len(head) - len(tail)
    return "\n".join(head + [f"... [{hidden} lines hidden] ...", ""] + tail)


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _output_html(out: dict, save_image) -> str:
    """One stored cell output as HTML: image, HTML table or plain text."""
    kind = out.get("output_type")
    if kind == "stream":
        text = _clip("".join(out.get("text", [])))
        return f'<pre class="nb-stream">{html.escape(text)}</pre>'
    if kind == "error":
        text = _ANSI_RE.sub("", "\n".join(out.get("traceback", [])))
        return f'<pre class="nb-error">{html.escape(_clip(text))}</pre>'

    data = out.get("data") or {}
    for mime in ("image/png", "image/jpeg", "image/gif"):
        if mime in data:
            url = save_image(mime, "".join(data[mime]))
            return f'<img class="nb-image" src="{url}" alt="" loading="lazy">'
    if "image/svg+xml" in data:
        return f'<div class="nb-image">{"".join(data["image/svg+xml"])}</div>'
    if "text/html" in data:
        return f'<div class="nb-html">{"".join(data["text/html"])}</div>'
    if "text/plain" in data:
        text = _clip("".join(data["text/plain"]))
        return f'<pre class="nb-text">{html.escape(text)}</pre>'
    return ""


def render_notebook(path: Path, out_dir: Path, url_prefix: str):
    """Render a .ipynb to HTML (plots land in out_dir), or None if unreadable."""
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, OSError, json.JSONDecodeError):
        return None
    language = (
        nb.get("metadata", {}).get("language_info", {}).get("name") or "python"
    )
    try:
        from pygments.lexers import get_lexer_by_name
        lexer = get_lexer_by_name(language)
    except ClassNotFound:
        lexer = TextLexer()

    images = []

    def save_image(mime: str, payload: str, stem: str = "output") -> str:
        """Write one plot or attachment to disk and return its URL."""
        ext = "." + {"jpeg": "jpg", "svg+xml": "svg"}.get(
            mime.split("/")[-1], mime.split("/")[-1]
        )
        name = f"{stem}-{len(images) + 1:02d}{ext}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / name).write_bytes(base64.b64decode(payload))
        images.append(name)
        return f"{url_prefix}/{name}"

    from pygments import highlight as pygments_highlight
    parts = []
    for cell in nb.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            for name, bundle in (cell.get("attachments") or {}).items():
                for mime, payload in bundle.items():
                    if mime.startswith("image/"):
                        url = save_image(mime, "".join(payload), "attachment")
                        source = source.replace(f"attachment:{name}", url)
                        break
            if source.strip():
                parts.append(
                    f'<div class="nb-md">{render_markdown_with_math(source)}</div>'
                )
        elif cell.get("cell_type") == "code":
            if source.strip():
                code = pygments_highlight(
                    source, lexer, HtmlFormatter(cssclass="highlight")
                )
                parts.append(f'<div class="nb-in">{code}</div>')
            outputs = "".join(
                _output_html(o, save_image) for o in cell.get("outputs", [])
            )
            if outputs.strip():
                parts.append(f'<div class="nb-out">{outputs}</div>')
    return '<div class="notebook">' + "\n".join(parts) + "</div>"


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
        self.env.globals["is_group_active"] = self._is_group_active

    @staticmethod
    def _is_active(nav_path: str, current_path: str) -> bool:
        if nav_path == "/":
            return current_path == "/"
        return current_path == nav_path or current_path.startswith(nav_path)

    @classmethod
    def _is_group_active(cls, item: dict, current_path: str) -> bool:
        """A dropdown is highlighted when the page is the section or any child."""
        paths = [item.get("path")] + [c.get("path") for c in item.get("children") or []]
        return any(p and cls._is_active(p, current_path) for p in paths)

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
                    current_path="/",
                )
            else:
                self.render(
                    f"{md_file.stem}/index.html", "page.html",
                    page={"title": title}, content=body_html,
                    needs_math=("\\(" in body_html or "\\[" in body_html),
                    current_path=f"/{md_file.stem}/",
                )

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
                "start": v.get("start") or youtube_start(v.get("url") or ""),
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
        """Front matter and rendered body of a folder's README.md, if any."""
        readme = directory / "README.md"
        if readme.exists():
            meta, body_html, _ = read_doc(readme)
            return meta, body_html
        return {}, ""

    @staticmethod
    def _count_files_recursive(directory: Path) -> int:
        """Count files (excluding IGNORE_NAMES and dotfiles) anywhere below directory."""
        total = 0
        for entry in directory.iterdir():
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                total += Builder._count_files_recursive(entry)
            elif entry.is_file() and entry.name not in IGNORE_NAMES:
                total += 1
        return total

    def build_documents(self):
        if not DOCUMENTS.exists():
            return
        self._build_dir(DOCUMENTS, Path("documents"), is_root=True)

    def _build_dir(self, src_dir: Path, rel: Path, is_root: bool):
        entries = sorted(src_dir.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        subdirs = [p for p in entries if p.is_dir() and not p.name.startswith(".")]
        files = [p for p in entries
                 if p.is_file() and p.name not in IGNORE_NAMES and not p.name.startswith(".")]

        meta, desc_html = self.folder_meta(src_dir)
        title = meta.get("title")
        page_title = "Notes & Documents" if is_root else (title or prettify(src_dir.name))

        folders = []
        for d in subdirs:
            child_rel = rel / d.name
            child_title = self.folder_meta(d)[0].get("title")
            n_sub = sum(1 for p in d.iterdir() if p.is_dir() and not p.name.startswith("."))
            n_file_total = self._count_files_recursive(d)
            folders.append({
                "name": child_title or prettify(d.name),
                "url": "/" + str(child_rel).replace("\\", "/") + "/",
                "n_sub": n_sub,
                "n_file_total": n_file_total,
            })
            self._build_dir(d, child_rel, is_root=False)

        file_entries = [self._build_file(f, rel) for f in files]
        featured = self._featured(meta, file_entries)

        self.render(
            str(rel / "index.html").replace("\\", "/"), "docs_dir.html",
            page={"title": page_title}, description=desc_html,
            folders=folders, files=file_entries, is_root=is_root,
            featured=featured, videos=folder_videos(meta),
            hide_file_list=bool(featured and featured["only_file"]),
            needs_math=bool(featured and featured["notebook_html"]),
            breadcrumbs=self._breadcrumbs(rel), current_path="/documents/",
        )

    @staticmethod
    def _featured(meta: dict, file_entries: list):
        """The file a folder page opens with, shown in place rather than linked.

        Either named by `featured:` in the folder README — with an optional
        `featured_title` and `featured_note` (Markdown) to say what the reader
        is looking at — or, when a folder holds a single file, that file: there
        is nothing to choose from, so the page shows it straight away.
        """
        name = meta.get("featured")
        if name:
            entry = next((e for e in file_entries if e["name"] == name), None)
            if entry is None:
                print(f"  ! featured file not found: {name}")
                return None
            note = meta.get("featured_note") or ""
            title = meta.get("featured_title") or prettify(Path(name).stem)
        elif len(file_entries) == 1:
            entry, note, title = file_entries[0], "", None
        else:
            return None

        return {
            "title": title,
            "note": render_markdown(note) if note else "",
            "name": entry["name"],
            "url": entry["view_url"] or entry["download_url"],
            "download_url": entry["download_url"],
            "kind": entry["kind"],
            "code_html": entry["code_html"],
            "notebook_html": entry["notebook_html"],
            "only_file": not name,
        }

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
            "kind": None,
            "code_html": None,
            "notebook_html": None,
        }

        kind, code_html, notebook_html = None, None, None
        if ext == ".pdf":
            kind = "pdf"
        elif ext in IMAGE_EXTS:
            entry["view_url"] = raw_url
            entry["kind"] = "image"
            return entry
        elif ext in VIDEO_EXTS:
            kind = "video"
        elif ext == ".ipynb":
            assets = src.stem + ".files"
            notebook_html = render_notebook(
                src, dest_dir / assets,
                "/" + str(rel / assets).replace("\\", "/"),
            )
            kind = "notebook" if notebook_html else None
        elif ext in CODE_EXTS and size <= MAX_INLINE_BYTES:
            code_html = self._highlight(src)
            kind = "code" if code_html else None

        if kind:
            view_rel = rel / (src.name + ".html")
            self.render(
                str(view_rel).replace("\\", "/"), "file_view.html",
                page={"title": src.name}, kind=kind, raw_url=raw_url,
                filename=src.name, code_html=code_html,
                notebook_html=notebook_html, needs_math=(kind == "notebook"),
                breadcrumbs=self._breadcrumbs(rel), current_path="/documents/",
            )
            entry["view_url"] = "/" + str(view_rel).replace("\\", "/")
        entry["kind"] = kind
        entry["code_html"] = code_html
        entry["notebook_html"] = notebook_html
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
    builder.build_pages()
    builder.build_theater()
    builder.build_carbomap()
    builder.build_documents()

    print(
        f"Built site into {OUTPUT}/ "
        f"({builder.carbomap_count} restaurant(s))."
    )


if __name__ == "__main__":
    main()
