[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/hendri-cyber/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/hendri-cyber/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

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

Built for the [make.fun](https://make.fun/bounty/news-image-20261121) "Sum up 21 November's world news in one image" bounty ($100 in USDC).
