RESULT: PASS
GATE: green — `python3 -m pytest tests -q` (14 passed, 2 skipped) then `python3 -m generators.build`, run after the last edit; the build rewrites `README.md` and `assets/` byte-identically, so the live page is untouched. The gate does not cover this task and cannot: all three steps are judgements about how a rendered page looks, and the gate checks that the tests pass and the build reproduces. What carries the verdict below is eleven rendered pages — four directions plus today's page as a baseline, dark, at 1012px and 390px — in `.review/archive/2026-09-19T1551-*.preview/`, and a measurement of every mark this page draws at both widths. No test was changed. One test the gate does run is load-bearing here and stayed green: `test_no_asset_sets_type_too_small_to_read_on_a_phone`.
SESSION: 21dab8e6-270a-4468-b901-4cd6bd2baa92
HUMAN: It can be done, and the version I would ship is 129px shorter than today's page rather than taller. The move that makes it work is not a bigger picture: it is that the whole page is cut from one frame of the real lattice, at one pitch, so the columns line up down its entire length and the text sits in the gaps of a single image — and then each project's own record is drawn over its own region of that frame, as a row of period cells with one circle on its busiest month and a line running out of the field into the heading below. Today's page spends 25.7% of its height on imagery and all of it is one picture; the version I recommend spends 25.1% and all of it counts something. Two things you should know before you pick. First, the field cannot be built from per-project data this repo had — I added `bin/field_data.py`, which reduces your three private Atrium working copies and the two public repos to one week-aligned series and commits it, so nothing is fetched at build time. Second, I found and fixed a defect of the same family as the one that got the page rejected three times, but in line work instead of type: the first pass drew 53 weekly columns, which measured out at a 0.95px null tick, a 0.45px circle stroke and a 0.36px leader on a phone — the whole instrument was invisible there. It is 13 four-week periods now and every part of it is at least 1px. Nothing is shipped and nothing is pushed; `generators/build.py` is untouched and still emits the page that is live.
PREMISE: The task's premise held, and its stated escape hatch was not needed. It said that if the stills show images cannot carry this without becoming unreadable on a phone, say so and propose the closest honest version. The stills show images *can* carry it, but only after the instrument was coarsened — so the premise was right about the risk and wrong only about the remedy being a retreat. One sub-premise is off in a way worth naming: the task says each project should be "a region of one lattice field **in its real data's grammar** (commits, files, gates)". A region drawn in its own grammar and a page that is one continuous field are in tension, because three different grammars do not tile into one frame. What is built resolves it the way `Design-Language.md` finding 1 does — the frame is the scene, every region is a slice of it, and the project's own record is a *measurement laid over* that scene. Gates are not in it: this repo has no per-project gate history to draw.

# The profile is an Atrium interface, not a page with an Atrium picture on it

Task: `.review/archive/2026-09-19T1551-profile-is-an-atrium-interface.task.md`
Stills: `.review/archive/2026-09-19T1551-profile-is-an-atrium-interface.preview/`
Nothing committed, nothing pushed. Working tree was clean at `8a3c601` when this started.

## 1. What "Atrium over the entire thing" can mean inside a README

A GitHub README renders Markdown, sanitised HTML and images. An SVG served through
an `<img>` gets no script and no pointer events, so an *interface* cannot be built.
What can be built is a page that is **one picture with text in the gaps**, and the
whole of this design follows from taking that literally.

`showroom/atrium-lattice.png` is a real 10× frame of the lattice — 218,016 events
from 31 repositories. It is reduced **once** to a single tall luminance grid, and
every band on the page is a contiguous slice of that one grid, drawn at one pitch
and one phase. The columns therefore line up down the whole page; every band paints
GitHub's own canvas before it draws, which the assets already did; and the Markdown
between two bands sits on the same ground the bands are painted on. Scrolling the
page is panning down one frame.

The crop was measured, not chosen. Searched over left/top/bottom for the best
combination of high mean darkness and low spread across eighths, restricted to
aspect ratios that give a page-length column of bands:

| Crop | Mean (0–9) | Rows, top to bottom | Columns, left to right |
| --- | --- | --- | --- |
| `(0.70,0.56,1.00,0.80)` — today's, tuned for one plate | 5.01 | 3.4 → 5.4 | 4.2 → 4.5 |
| `(0.60,0.45,1.00,0.95)` — **chosen** | 3.78 | 2.1 → 5.3 → 2.5 | 1.3 → 5.2 → 4.5 |
| `(0.62,0.34,1.00,1.00)` | 3.53 | 2.3 → 5.2 → 2.5 | 1.3 → 4.4 |
| `(0.55,0.40,1.00,1.00)` | 3.18 | 1.8 → 4.7 → 2.1 | 0.6 → 4.4 |

Today's crop is denser because it only has to fill one band. No tall crop of this
frame is evenly inked — the frame genuinely darkens toward its lower right — and
that turned out to be useful rather than a compromise: the top of the column is the
quiet ground the name wants, the middle is where Atrium's own region lands, and the
tail fades as the page ends.

**Then the nine primitives, mapped to what a README can actually do.**

| Primitive (`Design-Language.md`) | On this page |
| --- | --- |
| 2 · density fill | the lattice frame itself, sliced per section — *texture* |
| 1 · squarepacking | **not used.** An honest treemap across projects sizes Numeris largest (1,062 files, 712 commits against Atrium's 442 and 208), which fights the editorial hierarchy `content.DOMINANT` sets |
| 3 · null cells | a period with no commits, drawn as a tick — see §4 for why not an X |
| 4 · tracked points | one circle per region, on its busiest four weeks |
| 5 · leader → stat panel | the line out of the field into the Markdown heading below, and the readout docked to the band's own edge |
| 8 · micro-labels | **Markdown, not drawn.** See §3 |
| 9 · the chronometer | one dominant readout for the whole page, on the region the page is built around |
| 6 · connection lines, 7 · raster patches | not used — nothing on this page links across regions, and the frame *is* the raster |

The three resolution bands hold: thousands of lattice marks as texture, thirteen
period cells per region as structure, one circle and one leader per region as focus.
`Design-Language.md` notes frame 3 has about eight circles against tens of thousands
of marks; the recommended page has three.

## 2. Where the data came from, because the repo did not have it

`data/repos.sample.json` carries names, languages and diagram stages. It carries no
counts, so a field drawn from it would have been invented, and the design note is
explicit that a mark invented to fill space is decoration with extra steps.

`bin/field_data.py` (new) reduces every region to one week-aligned series and writes
`data/field.json`. Three sources, none of them touched at build time:

| Region | Source | Commits | Files | Periods lit, of 13 |
| --- | --- | --- | --- | --- |
| Atrium — `atrium-surface` | local `git log` (private) | 195 | 404 | 1 |
| Atrium — `atrium-host` | local `git log` (private) | 12 | 14 | 1 |
| Atrium — `atrium-design` | local `git log` (private) | 1 | 24 | 1 |
| BlueBand | GitHub API | 13 | 11 | 1 |
| Numeris | GitHub API | 712 | 1,062 | 4 |
| the substrate | `data/contributions.json`, already committed | 2,774 | — | — |

Private repos reduced once, by hand, to the few numbers the page draws, and those
numbers committed — the same treatment `showroom/atrium-lattice.png` already gets.
`generators/` never runs the script, never reaches the network, and reads only the
committed JSON, so the build stays reproducible offline and CI does not depend on a
private checkout existing.

**The finding inside the data.** Of 53 weeks, 15 carry anything and 11 of those are
consecutive and recent: weeks 42–52 hold 2,491 of the 2,774 contributions. Every
region on this page is one or four lit periods out of thirteen. That is not a defect
to design around — it is the most interesting true thing the field says, and it says
it without a sentence: a long run of null ticks, then everything at the right-hand
end.

## 3. Why every word is Markdown, including the micro-labels

`Design-Language.md` primitive 8 is a scatter of tiny, mostly unreadable text.
This repo has a floor that forbids exactly that: every text element must be at least
3.07% of its own viewBox width, because a 1200-unit plate renders at 0.30× in a
358px phone column. In a 1200-wide band that floor is 36.8px — a headline, not
texture. The two cannot both be honoured inside an image.

So the micro-labels are Markdown `<sub>` rows of real counts — `SCN·01 · 208 COMMITS
· 442 FILES · 3 REPOSITORIES · 218,016 EVENTS` — where they are legible at every
width, selectable, and visible to GitHub's search, which never sees text inside an
`<img>`. The only type any band draws is one region's dominant readout at 72px
(6.00% of the plate, 21.5px as read on a phone) and its caption at 38.4px (3.20%,
11.5px).

**The readout had to be docked rather than floated, and that is a measurement.**
The first stills set it straight onto the field. `18,470` survived at 72px because it
is near-white and enormous; `LINES OF SWIFT, 75 FILES` at 38.4px did not — the
frame's densest marks punch straight through 38px letterforms at any opacity that
still reads as a caption. It now paints the page's own ground first, with a hairline
on its left and bottom edges: primitive 5's stat panel, and the same occlusion the
planet's core already uses. `zoom-atrium-band-desktop.png` is the after.

## 4. The defect this found, and it is the same family as the one that got the page rejected three times

The first pass drew the measurement row at **53 weekly columns**. Measured at the
two widths `bin/page_preview.py` renders:

| Element | Units | Desktop, 0.817× | **Phone, 0.298×** |
| --- | --- | --- | --- |
| null-week tick | 3.20 | 2.61px | **0.95px** |
| tracked circle stroke | 1.50 | 1.23px | **0.45px** |
| leader line stroke | 1.20 | 0.98px | **0.36px** |
| baseline stroke | 1.00 | 0.82px | **0.30px** |
| week cell, quietest lit | 7.00 | 5.72px | 2.09px |
| week cell pitch | 22.64 | 18.49px | 6.75px |

On a phone the instrument was not small, it was **absent** — no cells, no circle, no
leader, just a grey smear. That is precisely the failure the 3.07% type floor exists
to prevent, in line work, which no test covers.

**The rule that fixes it, and it is worth keeping.** *Texture may go sub-pixel;
structure and focus may not.* A lattice mark's job is tone, and tone survives being
smaller than a pixel because it averages with its neighbours — the lightest lattice
mark is 0.60px on a phone and is correct. A period cell's job is to be one countable
mark, a circle's is to be found, a leader's is to be followed; none of those averages
into anything. So everything in the structure and focus layers is now at least 3.36
units — one pixel at 0.298× — and the resolution was spent to buy it:

| Element | Units | Desktop | Phone |
| --- | --- | --- | --- |
| null-period tick | 11.0 | 8.98px | 3.28px |
| period cell, quietest lit | 20.0 | 16.33px | 5.97px |
| period cell, busiest | 62.0 | 50.63px | 18.50px |
| period pitch | 81.5 | 66.6px | 24.3px |
| tracked circle radius | 44.0 | 35.93px | 13.13px |
| tracked circle stroke | 4.0 | 3.27px | 1.19px |
| leader line stroke | 3.6 | 2.94px | 1.07px |
| baseline stroke | 3.4 | 2.78px | 1.01px |

Thirteen four-week periods rather than 53 weeks. A phone cannot resolve 53 columns of
this page at any stroke width, so drawing 53 is drawing a number the reader cannot
count. `zoom-atrium-band-phone.png` is the result at 390px: baseline, twelve null
ticks, one lit cell, the circle round it and the leader leaving the frame, all legible.

Two smaller ones found the same way and fixed: the tracked circle always lands on the
most recent period for every region, so an edge-to-edge row had its one focal element
sliced in half by the band's right edge (cx 1153, ring 62, viewBox 1200) — the row is
inset by the ring; and a 120-unit band cut the readout's caption through the middle,
so a band under 230 units carries no readout at all.

## 5. The directions, measured

Widths are `bin/page_preview.py`'s: GitHub's 1012px profile column and a 390px phone.
Heights are the rendered page, trimmed to content. "instr" is bands carrying a
measurement; "tex" is bands carrying only texture.

| Page | Desktop | Phone | Images | instr | tex | Field as % of desktop height | Smallest type on a phone |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **today, `8a3c601`** | 2,611px | 2,554px | 3 | 0 | 1 | 25.7% | 12.3px |
| **continuous** | 2,627px | 2,644px | 6 | 3 | 2 | 27.4% | 11.5px |
| **trimmed** ← recommended | **2,482px** | 2,561px | 4 | 3 | 0 | 25.1% | 11.5px |
| **quoted** | 2,364px | 2,566px | 6 | 1 | 4 | 19.7% | 11.5px |
| **docked** | 2,272px | 2,475px | 3 | 1 | 0 | 11.5% | 12.3px |

Word count is identical across all four and within thirty of today's page; nothing was
rewritten, three `<sub>` micro-label rows were added.

**continuous** — the most literal, as the task asked for. Every section stands in the
field: six bands, 99 of the grid's 107 rows, masthead through Stack. It works, and its
weakness is visible in the table — two of its six bands carry no measurement, and on a
phone those are 19px and 16px of grey strip. They add page height and give a reader
nothing to read.

**trimmed** — `continuous` with those two bands cut, because `Design-Language.md` says
a region with nothing to measure should be empty rather than filled. This is the one I
would ship.

**quoted** — the middle. The field runs the whole page and the instrument appears only
on Atrium; every other band is a thin quotation of the same frame with its counts in the
Markdown below. Shorter, and four of its six bands are decoration by the note's own
definition. On a phone its tail bands are 8px tall.

**docked** — the most readable, as the task asked for. The field appears exactly twice:
under the name and as Atrium's own region. It is the shortest and the least Atrium — it
is essentially today's page with a field under the name, and it does not answer the brief.

## 6. Which I would ship, and why

**`trimmed`.** Three reasons, in order of weight.

1. **It costs nothing.** Today's page already spends 25.7% of its height on imagery and
   every pixel of it is one picture. `trimmed` spends 25.1% — the same budget — and
   every band in it counts something. It is **129px shorter than today's page on
   desktop** and 7px taller on a phone. "Atrium over the entire thing" turns out not to
   be a request for more page.
2. **It is the only one where the field is never decorative.** `continuous` has two
   texture-only bands, `quoted` has four. In `trimmed` the field appears in exactly four
   places and three of them carry a measurement; the fourth is the masthead, where the
   name stands in it. That is the note's own rule — a mark invented to fill space is
   decoration with extra steps — applied rather than quoted.
3. **It survives the phone, and that is now measured rather than hoped.** Smallest type
   11.5px against an 11px floor; smallest structure mark 1.01px against a 1px floor.
   `trimmed-dark-phone.png` is the evidence.

Checked in light theme as well as dark — `trimmed-light-desktop.png`. The field inverts
to dark marks on white, the readout's docked panel paints white and still occludes, the
links stay blue, the one warm pip survives.

**What `trimmed` gives up, stated rather than hidden.** "Also running" and "Stack" have
no field at all, so the last third of the page is not an Atrium interface. That is the
honest consequence of having no data for them. If you want the field to reach the
bottom, `continuous` is one word away and costs 145px; it is the same code with two
plan entries changed from 0.

## 7. Odd

**The tension between the field and the hierarchy.** Every honest quantitative treemap
across these three projects puts Numeris first — 1,062 files and 712 commits against
Atrium's 442 and 208. `content.DOMINANT` says Atrium leads, which is an editorial
decision and a correct one. They coexist here only because the field is not normalised
across projects: each region's cells are scaled against that region's own busiest
period, so Atrium's one lit cell and Numeris's four are each full-size in their own
band. That is a real design choice and it is reversible; if you want the page to show
the projects at true relative scale, say so and the cells share one ceiling — and
Numeris will visibly dwarf Atrium.

**The pitch is 132 columns because that is what has already been judged.** The Atrium
showroom has been reduced at 132 columns since it shipped. Keeping it means the marks
are the size someone has already looked at, not a new scale nobody has.

**Nothing is shipped.** `generators/build.py`, `content.py`, `README.md` and `assets/`
are untouched; the build after the last edit rewrote them byte-identically. New files:
`generators/svg/lattice.py`, `generators/directions.py`, `bin/directions.py`,
`bin/field_data.py`, `bin/__init__.py`, `data/field.json`, `data/field-grid.json`.
Adopting one of these directions is a change to `build.py`, which I have not made.

**A harness note for whoever measures this page next.** Headless Chrome shoots the
window, not the document, and has no flag for a full page. `bin/directions.py` shoots
into a 7000px window and trims the dead canvas, which also yields the page height as a
measurement rather than an estimate. Separately, `bin/page_preview.py`'s `pick_theme`
rewrites asset URLs to `../../assets/`, which is right for `preview/page/` and one
level too far up from `preview/directions/<name>/page/`. Before that was caught, every
image was a broken link — and a page of broken links renders at a plausible height and
photographs without an error. All three directions came back **exactly 1992px tall**,
which is the only reason it was noticed.
