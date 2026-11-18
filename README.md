# The World Today — 18 November 2026 (v2)

A dense newspaper front page summing up the world's news of Wednesday
18 November 2026 in a single image: masthead and dateline, the lead story
(Ukraine's second-day strike on the Crimea bridge), a world map marking
where the news happened, and 32 short real stories from every region.

## Run

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024 PNG, about 37 KB).

## How it works

`main.py` is pure Python 3.13 standard library — no dependencies, no
network, no randomness. It draws everything itself: a hand-written 5x7
bitmap font, a scanline-filled world map from rough continent outlines,
and a three-column layout of numbered headlines with one-line summaries.
Two runs produce byte-identical output.
