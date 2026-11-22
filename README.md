# news-image-20261121 — "The World in One Day"

A program that writes one image summing up **Saturday 21 November 2026**
to `/output/entry.png`.

- `draw.py` renders the newspaper front page with PIL (all art drawn in
  code: Gulf map, quake cross-section, COP31 calendar, world map, icons).
- `main.py` copies the rendered `entry.png` to the output directory.
- `entry.png` is the rendered front page: 35 stories (3 leads, 10 mids,
  22 briefs), 9 regions, UTC timeline, big-number strip, world map with
  numbered pins, DATE CHECK box, verification legend.

Build: `python3 draw.py` then `python3 main.py`.
