# The instrument, finished — 19 September 2026

Two variations of one page, both animated. Built by `bin/instrument.py`, which
runs the Markdown through `gh api /markdown` — GitHub's own renderer, the same
call `make page` makes — and then photographs *and films* the result.

| | `quiet` | `dense` |
| --- | --- | --- |
| Desktop, 1012px | 2,719px | 3,668px |
| Phone, 390px | 2,028px | 2,403px |
| Words a reader reads | 191 | 203 |
| Static plates | 1 | 3 |
| Animated plates | 3 | 3 |
| Animation, total | 642 KB | 622 KB |

The page that is live is 2,611px and 494 words.

## The three animated plates

Each is real data moving through real time, and each moves differently, which
is the point — three bar charts sweeping left to right would be one idea drawn
three times.

| | What moves | Frames | Size |
| --- | --- | --- | --- |
| **THE YEAR** | the year's 53 real weekly contribution counts, swept through a still region of the lattice one week at a time; the sweep lights the field column it passes | 53 at 13fps | 202 / 212 KB |
| **THE DAY** | the same lattice region repainted once an hour in Atrium's own colours, following the eight real anchors of its DayCurve | 24 at 6fps | 302 / 310 KB |
| **THE WORK** | the five real lanes of `data/field.json` built up a week at a time, each lane's running commit total counting as it goes | 53 at 13fps | 139 / 100 KB |

Every plate is GIF. APNG was built for all six and was larger every time — by
5.9× for `the year`, 1.6× for `the day`, 2.9× and 6.9× for `the work` — so GIF
ships and the pair is printed by `bin/instrument.py` on every run.

Each is paired with a PNG still behind `prefers-reduced-motion`. The still is
the last frame for `the year` and `the work`, because frame zero of each is an
empty instrument; for `the day` it is 13:00, the hour the DayCurve's own
`lightness_range` peaks at.

### Why `the day` is the honest one to be proud of

`data/atrium-tokens.json` carries the DayCurve's anchors out of
`Sources/AtriumSurface/DayCurve.swift` and the seven-step density ramp out of
`LatticeRenderer.swift`. Feeding the curve's hue through the ramp reproduces
the published `density-0..6` hexes — `#080302 #450d0a #78140f #b81d14 #e84552
#f6eaec #ffffff` — exactly, to the byte, at the resting point. That is the
check that this plate is painted in Atrium's palette rather than in a palette
that resembles it.

## How to look at it

```
design/instrument/<variation>/page/scroll-desktop.mp4    18.6s, 1012x860
design/instrument/<variation>/page/scroll-phone.mp4      18.7s, 390x844
design/instrument/<variation>/page/dark-desktop.png      the still
design/instrument/<variation>/page/dark-desktop.html     open in Chrome; it plays
```

The stills cannot show the motion; that is what the last round got wrong. The
MP4s are the evidence, and `dark-desktop.html` is the thing itself.

## Type

Every drawn word clears both of this repo's floors — `tests/test_build.py` at
3.07% of the plate's own viewBox, and `bin/directions.py` at 11px apparent in
GitHub's 358px phone column.

| | Smallest drawn type | On a 390px phone |
| --- | --- | --- |
| SVG plates | 38.0px in 1200 (3.17%) | 11.3px |
| Animated plates | 31.0 units in 980 (3.16%) | 11.3px |

The raster plates cannot be checked by reading the file back, because their
type is pixels by then, so `generators/animate.py` refuses at the point of
drawing: `_text` raises below 30.1 units and `_foot` raises with the measured
overflow when a label is wider than its slot. It caught `CONTRIBUTIONS` at 279
units in 270 on the first run, which is why the foot labels are tracked at
.05em and not .08em.
