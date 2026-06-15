# dariohug.ch

Source for my personal site at <https://dariohug.ch>. It's a small static site:
plain Markdown + folders of files, compiled to HTML by `build.py` and deployed
to GitHub Pages by a GitHub Action on every push to `main`.

## Add content (all doable from the GitHub website)

| I want to…            | Do this |
|-----------------------|---------|
| Write a **blog post** | Add `content/blog/YYYY-MM-DD-title.md` with a `--- title / date ---` header. |
| Add a **document**    | Open the course folder under `documents/`, **Add file → Upload files**, drag PDFs/code in. PDFs get an inline viewer, code gets highlighting, all get a download link. |
| Add a **school/course** | Create a new folder under `documents/` (commit a file inside it). Add a `README.md` with `title:` for a nicer name. |
| Add a **video**       | Add a YouTube link under `videos:` in `content/theater.md`. |
| Edit a **page** or the menu | Edit `content/pages/*.md` or the `nav:` list in `site.yml`. |

Push, and the site rebuilds and publishes in about a minute.

## Build locally

```bash
pip install -r requirements.txt
python build.py                       # writes the site to _site/
python -m http.server -d _site 8000   # preview at http://localhost:8000
```

## Layout

- `build.py` — the static site generator (read it; it's short).
- `site.yml` — title, navigation, email, base URL.
- `templates/` — Jinja2 HTML templates.
- `static/css/style.css` — the one stylesheet.
- `content/` — pages, blog posts, theatre page (Markdown).
- `documents/` — uploaded files, organised in folders.
- `_site/` — build output (generated; not committed).
- `.github/workflows/static.yml` — build + deploy to GitHub Pages.
