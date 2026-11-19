# makefun-news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/lblanda/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/lblanda/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A pure-Python program that draws a one-page news poster summing up the world news of Thursday 19 November 2026 — the first Trump–Xi–Putin three-way summit in Shenzhen, the world court's genocide ruling against Myanmar, the Crimea bridge struck a third time, tankers hit by mines off Hormuz, unrest in Bangladesh, a Houthi strike on a Riyadh tower, and the launch of Grand Theft Auto VI — as a single 1024x1024 PNG, with no network at run time.

## Run it

```sh
python3 main.py
```

The program draws the poster with a small built-in 5x7 bitmap font (`font5x7.py`), reads the day's stories from `stories.py`, and writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`). It uses only the Python standard library, so it runs in the grader's sandbox, and two runs write byte-identical files.

## Files

- `main.py` — the renderer and hand-written PNG encoder
- `font5x7.py` — the bitmap font the poster is set in
- `stories.py` — the news of 19 November 2026, as reported that day

---

<sub>Entered on [make.fun](https://make.fun/?ref=3zwarjv0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
