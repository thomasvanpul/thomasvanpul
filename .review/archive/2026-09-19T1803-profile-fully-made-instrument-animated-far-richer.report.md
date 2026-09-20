RESULT: PASS
GATE: green — `python3 -m pytest tests -q` (14 passed, 2 skipped) then `python3 -m generators.build`, run after the last edit. `README.md` and `assets/` came back byte-identical, so the live page is untouched. The gate does not cover this task and cannot: every deliverable here is a judgement about a rendered page and three animations, none of which the gate looks at. What it does prove is that this work disturbed nothing. What carries the verdict below is two filmed pages at two widths, six rendered stills, the measured type floor on both the vector and the raster plates, and a pixel-difference measurement showing motion in the recording while the page is not scrolling. No test was changed.
SESSION: 3b2dd024-b992-47d4-93e6-eef053608e08
HUMAN: Both pages are in `design/instrument/`. Watch `quiet/page/scroll-desktop.mp4` and `dense/page/scroll-desktop.mp4` first — 18.6 seconds each, both hold still at the top for 2.6s so you can see the plates moving before anything scrolls, and there are phone-width cuts beside them. Three animated plates, all real data over real time: **THE YEAR** (53 real weeks swept through the lattice, 202/212 KB), **THE DAY** (the same lattice repainted hourly in Atrium's own DayCurve colours, 302/310 KB) and **THE WORK** (the five real lanes of `data/field.json` building a week at a time, 139/100 KB). All six are GIF; APNG was built for every one and was larger every time, by 1.6× to 6.9×. Smallest drawn type is 11.3px on a 390px phone, on both the vector plates (38.0px in 1200, 3.17%) and the animated ones (31.0 units in 980, 3.16%) — nothing under either of this repo's two floors. **I would ship `dense`.** It costs 3,668px of page against `quiet`'s 2,719px and the live page's 2,611px, and it buys the thing you actually objected to: in `quiet` BlueBand and Numeris are still one line of prose under a small heading, which is round 3's bare-heading failure surviving into round 4. In `dense` each has its own plate with its own real counts, and the page has no section that is only a word.
PREMISE: The task's premise held completely and its instinct about the evidence was the real finding. Round 3 shipped an animation and reported it with a PNG, and a PNG of a moving image is a picture of a thing standing still — that is why you saw no motion, not because there was none. So this round's tooling ends in video, and the claim "it moves" is now a measurement: between two frames of the recording taken 1.6s apart while the page is stationary, 158,847 pixels differ. One sub-premise was wrong and is worth knowing. The task offers "the lattice resolving on approach" as a third animation. It cannot be built honestly — the lattice still has no per-mark timestamp, so mapping its columns to weeks would be an invention dressed as data — and `events.tsv` by hour is 136 rows inside one 45-minute window today, which is not a day. Atrium's own DayCurve is, and it was already on disk.

# The profile, fully made: instrument direction, animated, far richer

Task: `.review/archive/2026-09-19T1803-profile-fully-made-instrument-animated-far-richer.task.md`
Both pages, both recordings, the index: `design/instrument/`
Nothing committed, nothing pushed. `generators/build.py`, `README.md` and `assets/` are untouched.

## 1. The two pages

Built by `bin/instrument.py`, which runs the Markdown through `gh api
/markdown` — GitHub's own renderer, the same call `make page` makes — and then
photographs *and films* the result. `make page` itself renders the live
`README.md` and cannot render a page that is not live, so the equivalent for
these two imports the same four functions from `bin/page_preview.py` rather
than reimplementing them.

| | `quiet` | `dense` | live page |
| --- | --- | --- | --- |
| Desktop, 1012px | 2,719px | 3,668px | 2,611px |
| Phone, 390px | 2,028px | 2,403px | 2,554px |
| Words a reader reads | 191 | 203 | 494 |
| Raw `split()` words | 419 | 467 | 494 |
| Static plates | 1 | 3 | — |
| Animated plates | 3 | 3 | 0 |
| Animation bytes | 642 KB | 622 KB | 0 |

The two word counts differ because three `<picture>` blocks carry about 130
words of `alt` text nobody reads. `bin/instrument.py` prints both; the prose
count is the one comparable with round 3's `instrument` at 219.

## 2. The three animated plates

Each is real data moving through real time, and each moves *differently* —
three bar charts sweeping left to right would be one idea drawn three times.

| | What moves | Frames | `quiet` / `dense` |
| --- | --- | --- | --- |
| **THE YEAR** | the 53 real weekly counts swept through a still region of the lattice, one week at a time; the sweep lights the field column it passes | 53 at 13fps, 4.1s | 202 / 212 KB |
| **THE DAY** | the same lattice region repainted once an hour in Atrium's own colours, along the eight real anchors of its DayCurve | 24 at 6fps, 4.0s | 302 / 310 KB |
| **THE WORK** | the five real lanes of `data/field.json` built up a week at a time, each lane's running commit total counting as it goes | 53 at 13fps, 4.1s | 139 / 100 KB |

**GIF every time.** APNG was encoded for all six and lost every time: 5.9× and
5.7× larger for `the year`, 1.6× for `the day`, 2.9× and 6.9× for `the work`.
`encode()` builds both on every run and prints the pair, so this is a
measurement that will re-decide itself if a plate ever changes shape.

**Every plate has a still** behind `prefers-reduced-motion`. The still is the
*last* frame for `the year` and `the work`, because frame zero of each is an
empty instrument — one week lit, nothing built — and a reader who asked for no
motion should get the finished readout. `the day` has no finished state, so
its still is 13:00, the hour its own `lightness_range` peaks at.

### `the day` is the one worth checking

`data/atrium-tokens.json` carries the DayCurve's anchors out of
`Sources/AtriumSurface/DayCurve.swift` and the seven-step density ramp out of
`LatticeRenderer.swift`. Feeding the curve's hue and lightness through the ramp
reproduces the published `density-0..6` hexes — `#080302 #450d0a #78140f
#b81d14 #e84552 #f6eaec #ffffff` — exactly, at the resting point. That is the
check that separates "painted in Atrium's palette" from "painted in a palette
that looks like Atrium's", and it is the reason this plate is on the page.

## 3. The recordings

| | Length | Size | Scrolled |
| --- | --- | --- | --- |
| `quiet/page/scroll-desktop.mp4` | 18.6s | 2.3 MB | 1,928px |
| `quiet/page/scroll-phone.mp4` | 18.7s | 1.0 MB | 1,188px |
| `dense/page/scroll-desktop.mp4` | 18.8s | 3.1 MB | 2,856px |
| `dense/page/scroll-phone.mp4` | 18.6s | 1.0 MB | 1,533px |

Filmed through Playwright driving the installed Google Chrome, 2.6s held at the
top, 12s of eased scroll, 2.6s held at the bottom, then converted to H.264 MP4
— WebM does not open in Quick Look and MP4 does, which is the difference
between evidence and a file you have to find a player for.

**That they move is measured, not asserted.** Two frames of
`quiet/page/scroll-desktop.mp4` taken at 0.8s and 1.6s, while the page is
stationary, differ in **158,847 pixels**; at 2.4s, **199,716**. Both pages were
also opened in the real Chrome at the end of the run.

## 4. Type, measured on both kinds of plate

| | Smallest drawn | On a 390px phone | Under either floor |
| --- | --- | --- | --- |
| SVG plates (1, then 3) | 38.0px in 1200 (3.17%) | 11.3px | 0 |
| Animated plates (3) | 31.0 units in 980 (3.16%) | 11.3px | 0 |

The repo's two floors still disagree by two hundredths of a pixel —
`tests/test_build.py` asserts ≥ 3.07% of the viewBox, which reads at 10.98px,
while `bin/directions.py` asserts ≥ 11px apparent. Everything here is set
above both. Nothing was changed in either check; this is the second round it
has been reported and not fixed.

The animated plates cannot be checked by reading the file back — their type is
pixels by then — so the check lives at the point of drawing. `_text` raises
below 30.1 units and `_foot` raises with the measured overflow when a label is
wider than its slot. It fired twice: `CONTRIBUTIONS` at 279 units in 270 (the
foot labels are tracked at .05em, not .08em, because of it) and `DESIGN
ENGINEERING · IMPERIAL COLLEGE LONDON` at 1,169 units in 589 in the masthead's
top-right slot, which is now `IMPERIAL COLLEGE LONDON`.

## 5. Four things found while building

**The masthead was cut from the emptiest part of the frame.** Measured over
the 107-row grid in tens, mean ink runs 2.05 at the top to 5.40 at rows 80–90:
the lattice still is genuinely much emptier at its upper left. The first pass
gave the masthead rows 0–34 and it photographed as a name floating over
nothing. The plates now take their rows by density — masthead from 68, the two
small plates from 52 and 38 — so the page reads down the frame's *density*
rather than down its row numbers. What the plates share, and what the eye
actually reads, is the pitch, and that is unchanged.

**The old crop's right tenth fell out of the picture.** The crop the animations
inherited was searched for the highest mean ink at the lowest spread, which
says nothing about whether the ink is spread across the frame. Re-searched for
coverage — the most vertical twelfths whose mean clears 0.12 — `(1080, 800,
1530, 940)` is the only window of any size tried that fills all twelve, and the
animated plates stopped photographing with an unfinished right edge.

**A plate that prints the same number twice inside one screen.** `the year`'s
dense foot first read `CONTRIBUTIONS 2,774 · WEEKS ACTIVE 15/53`, both of which
the masthead sets 400px above it. It now carries `BUSIEST WEEK 546 · ITS WEEK
2026-08-30 · FIRST WEEK 2025-11-09`, none of which appear anywhere else.

**A heading and a lockup saying the same word in two sizes.** In `dense` the
BlueBand plate's `BLUEBAND` lockup sat directly under a markdown `### BlueBand`
at 20px. The markdown heading is dropped in `dense` where a plate carries the
name, and kept in `quiet` where nothing else does — which is one of the two
real differences between the variations rather than a cosmetic one.

## 6. Which I would ship, and what it costs

**`dense`.** Your verdict was that the page is under-made, and `quiet` does not
fully answer it: BlueBand and Numeris are still a heading and one line, which
is the shape round 3 was rejected for. `dense` gives every section something
measured — five plates, three of them moving — and reads as one instrument
rather than as a page with three animations dropped into it.

The cost is length: 3,668px against the live page's 2,611px, 40% more. If that
is the wrong trade, the cheapest 700px to remove is the two small plates'
foot rails and `the work`'s bottom rail, which would land it at about 3,000px
without losing a single number. That is a judgement, so it has not been made.

`quiet` is not a weaker version of the same page — it is the one to pick if you
want the three animations to be the only things that speak.

## 7. What is new on disk

```
generators/animate.py      the three animated plates, GIF and APNG, both measured
generators/instrument.py   the finished page, in two variations
bin/instrument.py          build both, render through GitHub, photograph, film
design/instrument/         both pages, both recordings, index.md
```

`generators/motion.py`, `generators/bold.py` and `bin/bold.py` are untouched,
so the three round-3 directions still build exactly as they did.

`design/` is now 49MB and still not in `.gitignore`. That was raised last round
and is still open; it is a decision, so it has not been made here.
