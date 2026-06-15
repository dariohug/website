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
| Add a **carbonara**   | Add `carbomap/restaurants/<name>.md` (+ optional photo in `carbomap/images/`). See `carbomap/README.md`. |
| Edit a **page** or the menu | Edit `content/pages/*.md` or the `nav:` list in `site.yml`. |

Push, and the site rebuilds and publishes in about a minute.

## Carbomap — Google Maps key (one-time)

The Carbomap page (`/carbomap/`) needs a Google Maps API key. The key is injected
at build time from a GitHub Actions **secret** and never lives in the repo.

1. **Google Cloud Console** → create/select a project (with billing attached) →
   enable the **Maps JavaScript API**.
2. Create an **API key** and restrict it:
   - *Application restrictions → HTTP referrers*: `dariohug.ch/*`,
     `*.dariohug.ch/*` (add `localhost:*` only for local testing).
   - *API restrictions*: Maps JavaScript API only.
   - Set a **quota cap** on map loads to avoid surprise charges.
3. GitHub repo → **Settings → Secrets and variables → Actions → New repository
   secret**: name `GOOGLE_MAPS_API_KEY`, value = the key.
4. Re-run the deploy (push, or *Actions → Run workflow*).

Without the key the build still succeeds — Carbomap shows the list view and
filters, only the interactive map is disabled. To test the map locally, run
`GOOGLE_MAPS_API_KEY=... python build.py`.

**Contact:** there's no public email on the site (to avoid spam); the footer
links to LinkedIn, configured via `linkedin:` in `site.yml`.

## Build locally

```bash
pip install -r requirements.txt
python build.py                       # writes the site to _site/
python -m http.server -d _site 8000   # preview at http://localhost:8000
```

## Layout

- `build.py` — the static site generator (read it; it's short).
- `site.yml` — title, navigation, LinkedIn link, base URL.
- `templates/` — Jinja2 HTML templates.
- `static/css/` — stylesheets; `static/js/carbomap.js` — the map page script.
- `content/` — pages, blog posts, theatre page (Markdown).
- `documents/` — uploaded files, organised in folders.
- `carbomap/` — restaurant entries (`restaurants/`) and photos (`images/`).
- `_site/` — build output (generated; not committed).
- `.github/workflows/static.yml` — build + deploy to GitHub Pages.
