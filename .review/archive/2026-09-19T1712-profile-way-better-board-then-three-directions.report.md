RESULT: PASS
GATE: green — `python3 -m pytest tests -q` (14 passed, 2 skipped) then `python3 -m generators.build`, run after the last edit. The build rewrites `README.md` and `assets/` byte-identically, so the live page is untouched. The gate does not cover this task and cannot: all three steps are judgements about how a rendered page looks, and the gate checks that the tests pass and that the build reproduces. What carries the verdict below is 21 reference screenshots, six rendered pages (three directions, dark and light, at 1012px and 390px), three side-by-side comparison sheets, and a measurement of every text element each direction draws. No test was changed. The one gate test that is load-bearing here stayed green without being touched: `test_no_asset_sets_type_too_small_to_read_on_a_phone`.
SESSION: 9353c043-642b-4850-8d3a-24e42d6032c1
HUMAN: The board is in `design/reference-board/` — 21 pages, each with one screenshot and one line saying what specifically makes it look good. The three directions are in `design/directions/`, each beside the three references it borrows from in `design/comparisons/`. They differ in kind, not degree: `index` is nearly imageless and is type and rhythm only; `playback` is one animated image — a real region of the lattice as a dot screen, with the year's 53 real weeks swept through it a week at a time, 171 KB; `instrument` is the page as an Atrium readout, two plates with a lockup and three real counts along the foot of each. All three are less than half the height of the page that is live (2,611px desktop) and all three cut its 494 words by 41% to 56%. I would pick `instrument`: it is the only one that looks like Atrium at a glance and still survives a 390px phone, and its smallest drawn type reads at 11.2px there. The version I would actually ship is `instrument` with `playback`'s animation used once as the Atrium image — that is not one of the three, so it is written down rather than built. The four rejected directions are in `design/rejected/` with your verdict, not deleted.
PREMISE: The task's premise held. Its instinct that the last two rounds "optimised inside one idea" is exactly right and is measurable: the four rejected directions vary only in how many of the grid's 107 rows are field, from 99 down to 36, which is one axis. One sub-premise did not survive contact. The task suggests a direction "built around animated imagery (APNG or GIF of the real lattice moving)". The lattice moving is the wrong motion: a pan across a still frame is a camera move, it says nothing, and as a GIF it costs 3.7MB because every pixel changes every frame. Holding the field still and moving the *record* through it — 53 real weeks, one at a time — is both the honest animation and a 171 KB one. Second, the task asks for "one screenshot" per reference; three of the 24 sources cannot be photographed by headless Chrome at all, which is a fact about the screenshot and not about the site, and they were dropped rather than shown as blank rectangles.

# The profile, way better: a reference board first, then three bold directions

Task: `.review/archive/2026-09-19T1712-profile-way-better-board-then-three-directions.task.md`
Board, directions and comparisons: `design/`
Nothing committed, nothing pushed. `generators/build.py` is untouched.

## 1. The board

`bin/reference_board.py` shoots every row of `design/reference-board/sources.tsv`
through the same headless Chrome that `bin/directions.py` uses — 1280px wide,
device scale 1, a 9-second virtual time budget because a 4-second one
photographs a JavaScript site's loading state — and writes
`design/reference-board/index.md` from the same table, so the page and the
shots cannot drift apart.

24 sources were gathered. 21 are on the board:

| | Count | What they are |
| --- | --- | --- |
| GitHub profile READMEs | 12 | Designed rather than assembled out of badges: `Platane`, `jh3y`, `orhun`, `antfu`, `tholman`, `rednafi`, `simonw`, `caneco`, `natemoo-re`, `lowlighter`, `rossjrw`, `novatorem` |
| Portfolio pages | 5 | `rauno.me`, `brittanychiang.com`, `emilkowal.ski`, `georgefrancis.dev`, `anandchowdhary.com` |
| *Tron: Ares*, GMUNK | 4 | From `Atlas/Projects/Atrium/References/`, chosen after looking at all 40 |

Three were dropped: `bruno-simon.com` and `cassie.codes` photograph as empty
canvases headless, and `andyruwruw`'s generated now-playing card comes back as
grey placeholder boxes. Each is a failure of the screenshot, not of the site,
and the index page says so.

Each entry carries one line naming the single thing it is on the board for —
`antfu`: "the whole profile is one monospaced row of lowercase links";
`gmunk-interface-029`: "title lockup, tiny caption block, three staggered
rails each with one big numeral".

## 2. The three directions

Built by `generators/bold.py`, rendered and photographed by `bin/bold.py`
through the same GitHub Markdown renderer, at the same two widths, in both
themes.

| | What it is made of | Desktop | Phone | Words |
| --- | --- | --- | --- | --- |
| `index` | Type and rhythm. Six hairline rules, each a single row of the real lattice grid, and nothing else drawn. | 1,172px | 1,534px | 291 |
| `playback` | One animated image. The frame as a 120-column dot screen; 53 real weeks swept through it, and the sweep lights the field column it passes. 171 KB GIF, with a still for `prefers-reduced-motion`. | 941px | 1,213px | 278 |
| `instrument` | Two plates. A lockup at the top left, one caption line, three real counts along the foot of each. | 1,349px | 1,293px | 219 |
| **live page** | | **2,611px** | **2,554px** | **494** |

### Phone type, measured

GitHub's profile column is 390px, 358px inside its padding, so a 1200-unit
plate renders at 0.298×.

| | Text drawn inside images | Smallest, as it reads on a phone |
| --- | --- | --- |
| `index` | none | n/a |
| `playback` | none | n/a |
| `instrument` | 6 sizes across 2 plates | 11.2px, 0 below the floor |

`index` and `playback` cannot fail the floor, because neither puts a word a
reader has to read inside an image. `instrument` can, and clears it by two
tenths of a pixel.

## 3. Each direction beside what it borrows from

`design/comparisons/` — one sheet per direction, the rendered page at 1012px
on the left and its three references down the right, each captioned with the
one thing it was taken for.

| | Borrows from |
| --- | --- |
| `index` | `antfu` (one monospaced row), `caneco` (no imagery at all, weighted lines), `natemoo-re` (prose and a single rule doing all the structuring) |
| `playback` | `Platane` (one generated animation *is* the page), `orhun` (an animation anchoring a very short text block), `gmunk-process-047` (near-black ground, most of the frame empty) |
| `instrument` | `gmunk-interface-029` (title lockup, tiny caption, rails with one big numeral), `gmunk-interface-022` (a field held between docked readouts), `anandchowdhary.com` (live metrics treated as the page's typography) |

## 4. Four defects found while building, and what each cost

**The GMUNK rail composition does not survive the type floor.** The first
`instrument` pass put the readouts in two vertical rails either side of the
field, which is what `interface.022` does. At the floor a rail label is 37.4
units on a 1200-unit plate, and `CONTRIBUTIONS` is 291 units wide, so a rail
wide enough to hold it leaves 408 units of field between the two — and the
name, at 14 monospaced characters with .18em tracking, is 680 units and will
not fit in that gap. Both stills read `BUTIONS` and `ASSERTI`. `interface.029`
is the frame that does survive, because its rails are *horizontal*.

**Strings written by eye run off plates.** After the rewrite the foot still
read `LINES OF SWIFTASSERTIONS` and the caption was cut at `2026-0`. A
monospaced advance is 0.60em and `letter-spacing` adds its tracking to every
character including the last, so this is arithmetic, not judgement:
`generators/bold.py` now has `_fits()`, which raises with the measured
overflow. It caught `CONTRIBUTIONS` at 350 units in 335 on the next run, which
is why the labels are tracked at .08em and not .12em.

**The repo's two type floors disagree by two hundredths of a pixel.**
`tests/test_build.py` asserts ≥ 3.07% of the plate's own viewBox;
`bin/directions.py` asserts ≥ 11px apparent in a 358px column. 3.07% of 1200
is 36.8 units, which reads at 10.98px — so a plate set exactly at the test's
floor fails the preview tool's. The directions here are set at 3.12%, which
clears both. Nothing was changed in either check; this is reported, not fixed.

**A GIF of a moving field costs 3.7MB; a GIF of a moving readout costs 171 KB.**
Panning the frame changes every pixel in every frame and there is nothing to
delta. Holding the field still and moving one sweep line through it drops the
same 53 frames to 171 KB — but only with a *shared* palette and `disposal=1`.
Quantising each frame on its own gives every frame its own palette, which
forces a full frame into the file each time: 5.8MB for the identical pixels.

## 5. Which I would pick

`instrument`. It is the only one of the three that looks like Atrium at a
glance and also survives a phone, it cuts the most words, and it leads with
the number the page is really about. `index` is the safest and the least
memorable — it would look good on any engineer's profile, which is the
problem. `playback` is the one that makes someone stop scrolling, and it is
also the one whose single image has to carry everything.

The version I would actually ship is `instrument` with `playback`'s animation
used once, as the Atrium section's image, in place of the static showroom
plate. That is not one of the three the task asked for, so it is written here
rather than built.

## 6. The rejected four

`design/rejected/2026-09-19-lattice-frame-as-the-page/` holds `continuous`,
`quoted`, `trimmed` and `docked` — their stills, their READMEs, a copy of
`generators/directions.py` as it stood when they were built, and `VERDICT.md`
with Thomas's words. Nothing was deleted.

## 7. What is new on disk

```
bin/reference_board.py     shoot every source, write the board's index
bin/bold.py                build the three directions and photograph them
bin/compare_board.py       each direction beside its three references
generators/bold.py         the three directions
generators/motion.py       the animated lattice, as GIF and as a still
design/                    29MB, almost all of it screenshots
```

`design/` is not in `.gitignore` and is 29MB, nearly all PNG. If it is meant
to be committed it should be; if it is scratch, it wants a `.gitignore` line.
That is a decision, so it has not been made here.
