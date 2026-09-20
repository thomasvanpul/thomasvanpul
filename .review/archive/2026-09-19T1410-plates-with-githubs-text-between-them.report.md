RESULT: PARTIAL
GATE: green — `python3 -m pytest tests -q` (13 passed, 2 skipped) then `python3 -m generators.build`, run after the last edit. The gate did not cover this task when the session started and now partly does: two new tests encode the measurement the redesign turns on. It still says nothing about whether the composition is good. Everything about composition below is carried by the rendered pages, not by the gate.
SESSION: 47e847b2-cae4-4a42-ae9e-1a4dd3ee4ccb
HUMAN: You asked whether the words should move into the plates. I measured it and the answer is the opposite, with a number behind it: a README asset is a fixed-ratio image in a fluid column, so its type shrinks with the column and markdown's does not. At GitHub's own profile widths that is 0.82x on a desktop and 0.30x on a phone — and 13 of the 15 type sizes on the page you rejected were rendering below 8px, the smallest at 2.5px. The flow diagrams, the hero's readout row, the orbit's tool names and the Atrium figures strip were not small, they were absent. So the words came *out* of the plates, not in: the plates now carry marks and one large number, and every word is markdown, where it is legible at any width and GitHub's search can see it. The orbit is cut — 330 units of height to set twelve names at 3.6px — and so is Numeris's flow diagram, which drew boxes around the sentence directly above it. Everything else is width: one section gets the full column and nothing else does. That last choice is yours and I have not made it. Two pages are rendered, A with the BlueBand render dominant and B with the Atrium lattice dominant, and they are genuinely different pages rather than two settings of one. A is committed; switching is one word in `content.py`.
PREMISE: The task's premise — "GitHub strips CSS from prose, it cannot strip text inside an SVG, so stop putting words there" — is true in its first half and does not survive its second. It is correct that GitHub controls the prose typography and this repo controls the SVG typography. It is not correct that this makes the SVG the better place for words, because the SVG's type is the thing that scales away. The premise is answered rather than accepted, and the argument is below under "Where the line falls".

---

# The page is plates with GitHub's text between them

## The measurement everything else follows from

`bin/page_preview.py` renders the README at GitHub's own profile widths: a
1012px column on a desktop and 390px on a phone, each with 16px of padding
either side. So the usable column is **980px** and **358px**.

An asset is an `<img>` with `max-width: 100%`. Its type therefore scales by
`column / viewBox width` — for the 1200-unit viewBox every plate on this page
used, that is **0.817x on a desktop and 0.298x on a phone**. Markdown does not
do this; 16px body text is 16px in both columns.

Measured across the five text-bearing plates of the rejected page:

| plate | viewBox | type in viewBox | as read, phone |
|---|---|---|---|
| `hero` | 1200x340 | 9, 15, 26, 44px | 2.7, 4.5, **7.8**, 13.1px |
| `atrium-figures` | 1200x132 | 9, 10, 22, 54px | 2.7, 3.0, **6.6**, 16.1px |
| `flow-finance-tracker` | 1200x182 | 8.5, 9.5, 10.5, 12.5px | **2.5**, 2.8, 3.1, 3.7px |
| `flow-blueband-concept` | 1200x150 | 9.5, 12.5px | 2.8, **3.7**px |
| `orbit` | 1200x330 | 12px | **3.6**px |

**Fifteen distinct type sizes. Two of them clear 11px. Thirteen render below
8px and the smallest is 2.5px.** The four-box flow diagrams, the hero's
readout row, the Atrium figures row and all twelve orbit labels were not
small type — on a phone they were texture.

The floor used from here on is **11px as read**, which is below the 12px
GitHub itself renders `<sub>` at, with a pixel of slack for rasteriser
rounding. Expressed as the thing a generator can actually check, that is
**3.07% of the plate's own viewBox width**.

The consequence that decides the whole task: *width is the divisor.* There is
no font size that fixes a wide plate, because making the type bigger in a
1200-unit viewBox to reach 11px on a phone means 37px — a four-stage flow
diagram cannot be set at 37px across 1200 units. A plate is legible only if it
is **narrow**, or if the words **leave**.

## Where the line falls

This is the judgement the task asked for, and it is argued rather than
asserted.

**In the plate:** marks that carry no words — halftone dots, the contribution
field, the planet — and at most one large number with its unit. Those survive
at any width because they are already 5–9% of the plate.

**In markdown:** every heading, every link, every sentence, and every figure a
reader is meant to *read*.

Four reasons, in the order they matter:

1. **Scaling, above.** Small type in a wide plate is not readable and cannot
   be made readable without narrowing the plate past what the drawing needs.
2. **A screen reader gets one `alt` string per plate.** Not headings, not
   links, not landmarks, not a reading order — one run-on sentence for the
   whole image. Three sentences of prose inside a plate is three sentences a
   screen reader user receives as an undifferentiated blob they cannot
   navigate, skim or link out of. This is the task's own stop condition, and
   it fires: accessibility beats aesthetics, so the prose stayed prose.
3. **A link cannot exist inside an `<img>`-referenced SVG.** Anything with a
   URL in it is disqualified from the plate by construction — which is most of
   the page's wayfinding, including the entry point below.
4. **GitHub never sees it.** Not code search, not the browser's Ctrl-F, not a
   copy-paste. A recruiter searching the page for "Postgres" finds nothing if
   "Postgres" is a vector path.

What this costs, stated plainly: the page keeps GitHub's grey system-serif
prose, which is the thing you disliked. There is no version of this page where
that typography is ours *and* readable. The fix available is to have **less**
of it and to give it a rhythm the plates set, which is what was done — not to
hide it in an image where it becomes 3px tall and invisible to search.

## What changed

**Hierarchy.** One section gets the full column and nothing else does.
`content.DOMINANT` picks which, and it changes the section order and two plate
widths. Nothing else in the page moves.

**Rhythm.** Plates are 1200, 560 and 520 units wide and are left-aligned
against the same margin as the prose rather than centred, so a narrow plate
reads as subordinate instead of as a small full-width one. The BlueBand flow
is 520 units — a four-box diagram no longer takes the space a halftone render
does. Rendered plate height on a desktop went from **2067px to 1321px, −36%**.

**An entry point.** After the hero there is now `Start here`: three names,
three anchors, one claim each. It is markdown because every line of it is a
link, which is reason 3 above doing real work.

**Length.** Desktop **3801px → 3436px (−9.6%)** for option A, 3524px for B.
Per section, option A: top 410, Start here 190, BlueBand 951, Atrium 930,
Numeris 238, Also running 302, Stack 398.

**Weight.** Seven assets and 147 KB became **five assets and 131 KB**.

### What was cut, and why

- **The orbit plate.** 330 units of page height to set twelve tool names at
  3.6px. The same twelve names as one line of markdown are legible at every
  width, selectable, and findable by search. `generators/svg/orbit.py` and
  `data/orbit.json` are left in place; reinstating it is an import, a render
  line and a README line.
- **Numeris's flow diagram.** It drew BANK → INGEST → POSTGRES → API → UI,
  which is the sentence directly above it with boxes around it. BlueBand's
  diagram was kept because "one person doing the whole chain" is a claim the
  diagram proves and the sentence only asserts.
- **The hero's readout row and rotating subtitle.** Same words, now markdown
  under the plate. The numbers are still derived in `svg/hero.py`, beside the
  field they describe; `build.py` only sets them.
- **The Atrium figures row.** The lede number stayed in the plate and got
  bigger; 418 / 218,016 / 10 MB moved to markdown.
- **Sublabels inside the flow boxes.** They cannot be set above the floor at
  any width that fits four stages. They are the `aria-label` now, which is
  where a screen reader was getting them anyway.
- Prose trims throughout — deletions only, nothing added. The Atrium
  honest-state paragraph is verbatim.

### What the gate now covers

Two tests, both run against the assets a real build emits rather than against
the generators, so a plate rendered at a new width is covered the moment it
ships:

- `test_no_asset_sets_type_too_small_to_read_on_a_phone` — every `font:` size
  in every emitted asset must be ≥3.07% of its own viewBox width. The tightest
  margin on the page is the flow label at 3.27%.
- `test_the_page_carries_its_figures_as_text` — the figures that left the
  plates have to be in README.md and not only in an asset.

Both generators that can be resized (`figures`, `flow`) now express type as a
fraction of their plate, so no future width change can quietly drop below the
floor.

## The choice that is yours

The task's second stop condition fired: the composition cannot be judged
without you choosing what dominates, and averaging the two is what produced
seven equal plates. Both are rendered, neither is averaged.

- **`.review/preview/compare-desktop.png`** — before, A, B, side by side.
- **`.review/preview/compare-phone.png`** — the same three at 390px.
- Individually: `A-dark-desktop.png`, `A-dark-phone.png`, `B-dark-desktop.png`,
  `B-dark-phone.png`. The rejected page is `page-dark-desktop.png` /
  `page-dark-phone.png`.

**Option A — the object dominates.** `DOMINANT = "blueband"`. The BlueBand
render is 980px wide and is the biggest thing on the page; Atrium's lattice
is 560. The page says *I make physical things.* Committed.

**Option B — the measurement dominates.** `DOMINANT = "atrium"`. The lattice
is 980px wide and `18,470` is set at 85px; BlueBand's render is 620. The page
says *I measure what I build.*

Looking at both rendered: **B has the stronger plate.** The Atrium lattice at
full width is thousands of individually visible marks and it is the most
arresting image either page contains; at 560 in option A it collapses into a
dark smudge and loses the thing that makes it worth showing. A's argument is
that the BlueBand render is the more legible *object* — a recruiter sees a
product in two seconds, where the lattice needs its caption read first. A is
committed only because something had to be, not because it won.

To switch: one word in `generators/content.py`, then `make build`.

## What did not work, and what is open

**Phone length got worse, by 16.8%.** 3263px → 3810px, and identically for
both options. This is the direct cost of the judgement above: markdown wraps
and a plate does not, so every line of words that left a plate costs two or
three lines in a 358px column, while the plate it left was already scaling to
the same 358px regardless of its viewBox. Cutting the orbit and a flow
recovered about 180px of that; the words added about 700px. The lever exists
if you want it back — putting the figures into the plates makes the phone page
shorter and illegible again — but under the task's own stop condition
(accessibility beats aesthetics) I did not take it. Desktop is shorter, phone
is longer, and that trade is not hidden.

**The dominance choice is desktop-only.** Both options render at exactly
3810px on a phone, because every plate fills the 358px column whatever its
viewBox. On a phone A and B are the same page in a different order. If the
page is mostly read on a phone, the composition work done here is largely
invisible and only the cuts and the legibility survive — which is worth
knowing before choosing.

**The hero is still the weakest plate at phone width.** Its name reads at
17.9px and everything else has left it, so it is correct but it is now a
banner rather than a figure. A hero that reads well in both columns probably
needs two different drawings, which a single fixed-ratio SVG cannot provide
without CSS media queries inside the asset. That technique may work — an
`<img>`-referenced SVG evaluates media queries against its own rendered box —
but `rsvg-convert` and the preview harness will not agree with a browser about
it, so it could not be verified here and was not shipped. Named as a follow-up
rather than attempted.

**Judgement calls you may want to overrule, each a small change:**

1. **Cutting the orbit.** The most defensible cut under the measurement and
   the one most likely to be unwanted — it was the page's only ornament and
   the only thing on it that moved slowly. Reinstating it costs three lines
   and 270px of desktop height, and its labels stay at 3.6px on a phone.
2. **Keeping `18,470 / LINES OF SWIFT` as Atrium's lede number.** For a
   ninety-second read the stronger number is `13 of 33` — the flakiness
   finding is the best story on the page and lines of code is the weakest
   brag. I did not swap it, because which claim ledes a section is a
   Verified-Claims question and not mine to make silently.
3. **Cutting Numeris's flow diagram** leaves that section with no plate at
   all. Three sections with a plate and one without is deliberate rhythm; if
   it reads as neglect instead, `content.FEATURED["Finance-Tracker"]["flow"]`
   turns it back on.

**Not checked:** light theme. The light-desktop and light-phone HTML are
written by `make page` but were not rasterised or reviewed; the assets carry
their own dark field, so the only light-theme surface is GitHub's prose, which
is unchanged. Stated rather than assumed.
