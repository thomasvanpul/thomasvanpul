RESULT: PARTIAL
GATE: green — `python3 -m pytest tests -q` (14 passed, 2 skipped) then `python3 -m generators.build`, run after the last edit. `README.md` and `assets/` came back byte-identical, so the live page is untouched and nothing here is shipped. The gate does not cover this task and cannot: every deliverable is a judgement about one animated image and a three-line page, and the gate looks at neither. What it proves is that this work disturbed nothing. What carries the verdict is four filmed pages at two widths, eight rendered stills, a six-frame strip across the loop join, and the encoded size of every plate. No test was changed.
SESSION: db209344-7e93-4ccc-9a22-6643edbfd953
HUMAN: Two finishes of one piece, both in `design/hero/`. Watch `readout/page/hero-desktop.mp4` and `flight/page/hero-desktop.mp4` first, 21.5s each, with phone cuts beside them. Both are the same thing: one year of your real commits as a corridor you fly down, the floor cut from the Atrium lattice, five lanes for Atrium's surface, host and design repos, BlueBand and Numeris, one mark per commit, and the camera stopping at each lane in turn so the page shows projects without needing hover. `flight` gives the corridor the whole frame and docks one panel that swaps sides depending on which lane is being read. `readout` insets the corridor and spends the margins on chrome: a rail naming all five lanes at all times with the live one lit, and a foot carrying its three real counts. **I would ship `readout`.** It is also the smaller file, 1,222 KB against 1,450 KB dark. **One thing is not in either and it is your call:** only the five lanes with commits in `data/field.json` are in the piece. IRIS, HFQ, Interstellar Sanctuary and the air-defence paper have no commit data, the design language forbids inventing a mark to fill space, and a very short text block has no room for four unlinked names. They are currently nowhere on the page.
PREMISE: held

# The profile in orhun's shape

## What was built

`generators/corridor.py`, 1,000 lines, one hero in two finishes and two themes.
`bin/hero.py` builds all four plates, writes the README, renders it through
GitHub's own Markdown, shoots it in headless Chrome at both widths in both
themes, and films it in a real Chrome for twenty seconds at each width.

The world is the one `Atlas/Projects/Atrium/Design-Language.md` already
describes: "time as a receding corridor: today at the near edge, the past
running away to a horizon, repos as lanes along it". The camera flies down it
once per loop, leaning laterally toward whichever lane it is reading.

Where every mark comes from:

| element | source | count |
|---|---|---|
| floor | `data/field-grid.json`, one real Atrium lattice frame reduced to 132 x 107 density levels | 14,124 cells |
| lanes | the five real lanes of `data/field.json` | 5 |
| marks | one filled square per commit, stacked by week | 933 |
| lane width | files touched, 4 columns at the narrowest and 12 at the widest | 11 to 1,062 files |
| null cells | a lane-week with no commits draws the X of primitive 3 | Atrium's design lane is 52 of them and one mark |
| dates | `data/field.json` week starts, 2025-09-14 to 2026-09-13 | 53 weeks |

Nothing is invented. 38 of the 53 weeks are empty and they are drawn empty;
the camera moves faster through them, which is the only reason the loop is
not three quarters dead air.

## Sizes, measured

| plate | encoding | size | also built | frames | seconds | pixels | still |
|---|---|---|---|---|---|---|---|
| flight dark | GIF | 1,449.7 KB | APNG 2,371.6 KB | 96 | 7.4 | 820 x 402 | 34 KB |
| flight light | GIF | 1,451.6 KB | APNG 2,345.2 KB | 96 | 7.4 | 820 x 402 | 34 KB |
| readout dark | GIF | 1,222.4 KB | APNG 1,589.7 KB | 96 | 7.4 | 820 x 452 | 44 KB |
| readout light | GIF | 1,245.1 KB | APNG 1,629.4 KB | 96 | 7.4 | 820 x 452 | 43 KB |

All four are inside the ~1.5 MB budget the task set. APNG was built for every
one and was larger every time, so GIF ships. The stills are what a reader with
`prefers-reduced-motion` gets, and they are taken from the middle of the
largest lane's window rather than from frame zero, which is the smallest.

Why the plate is 820 wide and not the 980 the static plates use: a corridor
that moves has no still region to delta against, so the file is close to
linear in pixels times frames. At 980 x 430 the same loop encodes to 2,630 KB
and will not come down without taking the motion out. On a phone it costs
nothing, because every image is scaled to GitHub's 358px column anyway.

Supersampling is off, and that is a measurement rather than a preference: at
SS 2 the same frames encode to 5,990 KB instead of 2,630 KB, and the
hard-edged version is also the better one, because the marks read as discrete
cells, which is what the field is.

## The recordings

| film | width | duration | size |
|---|---|---|---|
| `design/hero/flight/page/hero-desktop.mp4` | 1012 | 21.6s | 2,953 KB |
| `design/hero/flight/page/hero-phone.mp4` | 390 | 21.4s | 636 KB |
| `design/hero/readout/page/hero-desktop.mp4` | 1012 | 21.6s | 2,650 KB |
| `design/hero/readout/page/hero-phone.mp4` | 390 | 21.4s | 472 KB |

Each is a real Chrome loading the README as GitHub renders it: 8.5s hold, a
3s scroll, 8.5s hold. The hold is most of it because this page barely
scrolls, so the time belongs to the animation. At 7.4s per loop, each film
shows the loop join about twice.

`bin/instrument.py`'s `record` grew three optional arguments for this and is
otherwise unchanged; its defaults are the constants it always used.

## Smoothness

Judged two ways, because a film of a loop cannot show you the join twice in
the same instant.

By eye, at full frame rate, in the films above.

By arithmetic, across frames 93, 94, 95, 0, 1, 2: the camera advances 0.320,
0.319, 0.320, 0.266, 0.266 weeks per frame. The step across the join is 0.320,
inside the range the rest of the loop already uses, so there is no jolt. The
station handover happens to straddle the join, and its easing runs 0.055,
0.198, 0.394, 0.606, 0.802, 0.945 straight through it. The strip is in the
session scratchpad as `strip-seam.png`.

The camera's speed is data-driven and then cyclically blurred, which is what
keeps the wrap continuous: the blur wraps too, so the first frame and the last
frame are neighbours in the smoothing as well as in the playback.

## Type

Smallest drawn label is 31 units in an 820-wide plate, which reads at 13.5px
in GitHub's 358px phone column. `_t` raises rather than drawing anything below
25.2 units, which is this repo's 11px floor. Nothing in either plate is near
it. The phone shots confirm it: `readout/page/dark-phone.png` has all five
lane names, the chronometer, and three counts legible at 390.

## Six defects found and fixed after looking at the render

Every one of these was in the first build and none was caught by the gate.

1. **flight ruled a line through its own chronometer.** The docked panel's top
   edge landed at y 128 and the chronometer value `W51/53` occupies 93 to 134.
   `FLIGHT_H` was 360 and had no room for both. Now 402, which is the
   chronometer's bottom plus 20 clear plus the panel plus the pad.
2. **readout drew its foot labels over the corridor.** The foot needs
   `18 + VALUE + LABEL + 12` = 102 units under the field and had 92, so the
   labels sat inside the last ten rows of lattice. `READOUT_FOOT` is now 130.
3. **readout's station rail ran over its foot values.** Six rows at the old
   spacing ended at y 392, through `1 / 53`. The gaps are now 8 and 10, which
   ends the rail at 338, and `READOUT_H` is 452.
4. **`1 COMMITS`.** Atrium's design lane really is one commit across 24 files,
   so the panel that reads it is the one a reader looks at hardest. There is
   now a `_count` helper, and every number on the plate carries a thousands
   separator, so it reads `1,062 FILES` as the rest of the page does.
5. **The leader line ran into the `1` of `12 COMMITS`.** `_readout` returns
   where the type starts, not where the panel starts; the leader now stops at
   the panel's edge.
6. **`FLIGHT_ALT` described a tracking box** that was replaced by rails several
   iterations earlier. A screen reader would have been told about something
   that is not there.

1 to 3 are now `check_layout()`, which runs before any frame is drawn and
raises with the height the constant would have to be. They were found in a
screenshot, and a screenshot only catches what someone happens to look at.

Paying for 1 to 3 cost eight frames: the taller flight plate encoded to
1,559 KB at 112 frames, over budget, so the loop is 96 frames and 7.4s.

## Two finishes, and why there are two rather than five

The task asked for two variants of the hero, both finished, and the design
note leaves one question open that these two answer differently: whether the
piece takes the full column edge to edge, or docks into a gutter. `flight`
takes the frame. `readout` docks. Picking one settles the note.

They differ structurally, not cosmetically, which is the point. A reader
would describe the difference in words: one of them names all five projects
all the time, the other names one at a time.

## Why I would ship `readout`

Your objection to hover chrome, in your own words, is "not knowing what is
there". `flight` reproduces that objection in a different medium: at any
instant it names one lane, so a reader who glances at it, or sees the
reduced-motion still, or has images loading slowly, learns about one
repository. `readout` names all five at all times and lights the one being
read, which is the opposite of hover and the closest this page can get to
what you asked hover for.

It is also the smaller file by 228 KB, and its corridor is the cleaner read.
`flight` paints an opaque ground panel over the field, because a 38-unit
caption does not survive over lit lattice at any opacity that still reads as
a caption, so the docked panel punches a rectangle out of the scene. In
`readout` the chrome is in the margins and the corridor is never covered.

What `flight` has that `readout` does not: the corridor is 820 x 402 rather
than 544 x 226, so the scene is roughly two and a half times the area, and
the composition changes at every station because the panel swaps sides. It is
the more cinematic of the two. If the page is meant to be looked at rather
than read, it is the better one, and the pick flips.

## What is not here, and it is a judgement call

The task says the animation should cycle "Atrium, BlueBand, Numeris and the
other projects". Only those three are in it, as five lanes, because only those
three have commit data in `data/field.json`. IRIS, HFQ forming research,
Interstellar Sanctuary and the air-defence paper have none.

Two rules collide and I let both stand rather than breaking either. The design
language: "If a mark has to be invented to fill space, the region should be
empty instead." And the task: "A very short text block under it: name, one
line, links. Nothing else." So they cannot be drawn and they cannot be written
about. Of the four, only Interstellar Sanctuary has a URL at all.

Three ways out, none of them mine to choose:

* Leave them off the profile. The page argues three projects well.
* Add them to the links line, which stretches "links" to mean a project list
  and only works for the one with a URL.
* Give them data. IRIS is a private repo with real commits; if the field
  builder can read it, IRIS becomes a sixth lane with no rule broken.

## AI-slop check

Against `Atlas/Style-AI-Slop-Tells.md`, the checklist at the bottom.

Words: zero em dashes, zero banned phrases, zero hedges. 18 words of prose on
the page. Grounded in a real institution, and the image carries 53 real dates,
five real repository names and four real counts per lane.

Colour: three, and each means something. Ground is GitHub's own `#0d1117`.
One hue ramp of seven steps out of `data/atrium-tokens.json` carries how much
happened. One near-white is the focal reserve and is spent on exactly one
thing per frame, the lane being read. The link blue was removed from the image
entirely, and the rule that leaves behind is worth keeping: blue means
clickable, and nothing inside a README image is clickable.

Composition: the vanishing point sits at 0.42 of the width, not the centre.
The corridor runs off three edges of the frame. The camera leans rather than
centring.

The deliberate odd choice: the panel docks away from the lane it names, so
which side of the frame it sits on is decided by where the camera is looking.
Five stations, five different compositions, rather than one composition five
times. The second one, if it counts: the five lanes are not five identical
treatments. A lane's width is its files touched, and the small lanes are
mostly X-crossed null cells while the large ones are solid, so Atrium's design
lane and Numeris are drawn in visibly different grammars because they are
visibly different things.

Code: `check_layout` exists because two callers' worth of the same arithmetic
was already wrong. Every new comment says why. The diff touches
`generators/corridor.py`, `bin/hero.py` and three optional arguments in
`bin/instrument.py`.

## What was not done

Nothing is shipped. `README.md` and `assets/` are untouched, and both pages
live in `design/hero/`. Wiring the pick into `generators/build.py` is the next
task, and it is one function and one content block.

True hover belongs on thomasvp.com. A README cannot do it, the animation is
the substitute, and the substitute is worse than the real thing in one
specific way: the reader cannot choose which project to look at. That is the
follow-up.
