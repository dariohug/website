# Carbomap data

Each restaurant is one Markdown file in `restaurants/`. Photos go in `images/`.
Add one, push, and it appears on <https://dariohug.ch/carbomap/>.

## Add a restaurant

Create `restaurants/some-name.md`:

```markdown
---
name: "Da Enzo al 29"
lat: 41.88880          # right-click the spot in Google Maps → "copy coordinates"
lng: 12.47570          #   (paste gives "lat, lng" — split into these two)
city: Rome
country: Italy
rating: 4.5            # 0 to 5, in 0.5 steps (half-stars supported)
price: 16              # a number
currency: "€"          # shown next to the price (€, CHF, …)
guanciale: true        # uses real guanciale?
cream: false           # cream in the sauce?
image: da-enzo.jpg     # optional; a file you put in carbomap/images/
date: 2025-09-12       # optional
---
A few words about the carbonara — this becomes the popup / card text.
```

## Notes

- **Coordinates** are required (no lat/lng → the entry is skipped). Get them by
  right-clicking the place in Google Maps and choosing *"copy coordinates"*.
- **Photo** is optional. Upload it to `carbomap/images/` (GitHub: *Add file →
  Upload files*) and reference the filename in `image:`.
- The **filters** on the page use these fields: rating, price, `guanciale`,
  `cream`.
- The live **map** needs the `GOOGLE_MAPS_API_KEY` secret (see the main
  `README.md`). Without it the list view still works.
