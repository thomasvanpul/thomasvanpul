RESULT: PASS
GATE: green — `python3 -m pytest tests -q` (14 passed, 2 skipped) then `python3 -m generators.build`, run after the last edit, plus `python3 ~/dev/atrium-design/bin/conformance.py` → `OK … thomasvanpul: 17 files, 1/1 exceptions present, 1/1 vendored copies current, 0 stray`. The gate covers the two things this task can be wrong about mechanically — that a colour outside the token set is unaccounted for, and that more than one thing on the page moves — because two new tests encode them. It says nothing about whether the page looks good. Everything about the look below is carried by the four rendered pages, not by the gate.
SESSION: 581d9fa0-b53d-4328-93e1-4557a39dc1a8
HUMAN: You said the blue stays, so I stopped trying to make a warm ramp sit next to it and measured instead whether any Atrium token can read as *page* rather than as *panel*. None can: the closest, `field-light-edge`, is ΔE76 6.36 from GitHub's own dark canvas at almost the same lightness, and `density-0` is 6.44 — far enough to read as a slab, close enough to look like a mistake. So the plates lost their grounds entirely and now paint GitHub's canvas, which is why every plate is flush with the prose for the first time and why the page has a working light theme for the first time. The page is now near-monochrome with your blue as the only strong colour and exactly one warm mark on it: a single `density-4` pip orbiting the planet, 24 seconds a lap. That is the outcome your third option named, arrived at by measurement rather than by taste. One thing is still yours: A (BlueBand dominant, committed) or B (Atrium dominant). Both are rendered. I argue A in one sentence below and it is one word to switch.
PREMISE: The task offered three palettes and said one had to be chosen. The middle one — "cool the plates by moving down Atrium's ramp" — is not available, and that is a real finding rather than a preference: the measurement above says no token in the set is far enough from `#0d1117` to stop reading as a panel. The task's own stop condition ("if the warm palette cannot be made to work with GitHub's blue, say so plainly — that would mean the page should be near-monochrome with blue as its only colour") therefore fires, and the page shipped is that page, with one deliberate exception kept so the palette is present rather than absent.

---

# Blue links stay. Make everything else good.

## The colour decision, and the number behind it

The rejected render had `#150b0c` plates sitting on GitHub's `#0d1117` canvas.
Sampled from the render, converted to CIELAB, and compared against the canvas:

| candidate ground | ΔE76 from `#0d1117` | L\* |
|---|---|---|
| `field-light-edge` | 6.36 | 3.84 (canvas 4.95) |
| `density-0` | 6.44 | — |

Both land in the same bad band: far enough that the eye reads a rectangle,
close enough that the rectangle looks unintended. There is no third candidate —
those are the two darkest values in the ramp. **So "cool the plates" is
measurably not a fix, and the only ground that stops reading as a slab is the
page's own canvas.**

What shipped: every asset now paints Primer's canvas value and themes itself.

```
svg { color: density-5; --ground: #0d1117; }
@media (prefers-color-scheme: light) { svg { color: density-0; --ground: #ffffff; } }
```

`currentColor` is the single ink channel, so one media query retints a whole
asset. `--ground` is a custom property with a `.ground` class, because `var()`
is not allowed in a presentation attribute.

**One exception was needed and it is written down.** `EXCEPTIONS["thomasvanpul"]`
in `~/dev/atrium-design/bin/conformance.py` now holds `#0d1117` with the
reason: it is Primer's `canvas.default` on dark, it is the page this asset
lands on rather than a colour the design chooses, and the checker itself
reports it as 138° of hue away from anything in the ramp. The light canvas
needs no entry — GitHub serves pure white there and that is `density-6`
exactly.

Measured across the seventeen emitted assets, the whole page now uses **five
distinct hex values**: `#080302` and `#f6eaec` (the two ink ends), `#0d1117`
and `#ffffff` (the two canvases), and `#e84552` — the pip — which appears in
**two** files, `hero` and `hero-still`, and nowhere else. That is what "use
warm sparingly" came to.

Two consequences worth naming because neither was asked for:

- **Light theme works for the first time.** `prefers-color-scheme` inside an
  `<img>`-referenced SVG was verified to be evaluated (Chromium, both
  directions). `C-light-desktop.png` and `C-light-phone.png` are the first
  honest light renders this repo has produced.
- **The page has one left edge.** With the grounds gone there was nothing left
  for the internal insets to be inset *from*, so the hero (70 units), the
  figures strip (32) and the halftone (45) each started at a different offset
  from the prose. All three are now zero, and `18,470` lines up with the
  paragraph under it.

`bin/page_preview.py` also gained a per-theme link colour (`#4493f8` dark,
`#0969da` light). Hard-coding the dark one made every light preview lie about
the one colour on this page that is not ours to choose.

## Motion: one thing, and the switch is where it is actually read

Before: about ten SMIL animations across the page, none of them visible. Each
moved under 1% of its own plate's width, and a plate scales to 0.298x at
GitHub's 358px phone column, so the travel was **≤2px**. A blinking caret, a
pulse ring, seven flow-diagram dots.

After: **one CSS animation in the whole page, zero SMIL** — counted in the
emitted assets, not in the generators, so a new plate is covered the moment it
ships. It is a `density-4` pip on `offset-path` around the planet's outer ring,
`offset-rotate: 0deg` so it stays round, 24s linear.

- travel: 2 × rx = **312 units on a 1200 viewBox = 26.0% of the plate width**,
  which is **93px** as read on a phone.
- the mark itself: 10 units, 3.0px on a phone. Small, but it is the movement
  that is legible, not the dot.

It cost nothing in legibility: it is a mark, not a word, and it moves in the
one region of the hero that carries no type.

### The reduced-motion guard was dead code, twice over

First attempt put `@media (prefers-reduced-motion: reduce) { .pip { animation:
none } }` inside the asset. Under emulated `reduce` the pip still moved. A
colour probe settled why: the same file, with the reduced-motion rule also
setting `fill: #00ff00`, gives **green 0 / red 74** when loaded through an
`<img>` and **green 73 / red 0** when opened as a document. Chromium evaluates
`prefers-color-scheme` inside an image document and does **not** evaluate
`prefers-reduced-motion` there.

So the switch moved to the host page, where the query is really evaluated:

```html
<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="…/hero-still.003b166.svg">
  <img alt="…" src="…/hero.efad40a.svg">
</picture>
```

Verified end to end, both directions, on a copy of the real markup with the
still's pip recoloured green so the selected source is unmistakable:

| emulated | `img.currentSrc` | green px | red px |
|---|---|---|---|
| `reduce` | `probe-still.svg` | 61 | 0 |
| `no-preference` | `hero.efad40a.svg` | 0 | 58 |

And the open question from an hour ago — whether GitHub's sanitiser passes a
`<source media>` that is not a `prefers-color-scheme` query — is now answered
rather than hedged. GitHub's own renderer, `gh api --method POST /markdown -f
mode=gfm`, returns the element **unmodified**:

```
<source media="(prefers-reduced-motion: reduce)" srcset="…/hero-still.003b166.svg">
```

A test forbids the in-asset query, requires the `<source>` in the README,
requires exactly one `hero-still.*.svg`, and requires that it contains no
`animation:`.

## Clumps: what was cut, and why

Prose blocks: **460 words → 428 (−7.0%)**, longest block **70 → 59 words**,
README **8215 → 5744 bytes (−30.1%)**. The byte number is the larger one
because most of the fix was structural, not deletion — markdown has tables and
short lists, and a table is not a clump.

- **The hero standfirst's second line.** It listed the tools, and the Stack
  table lists the tools, within one screen. Origin and location moved to the
  footer, where they already were.
- **Atrium's figures line and two statistics buried in paragraphs** → a
  five-row table, headed `Atrium | measured 2026-09-16` so the date is stated
  once rather than per figure.
- **The `Swift | 18,470 lines across 75 files` row**, cut after looking at the
  first render: the plate directly above sets that same number at 85px. The
  same fact twice inside one screen is the clump in miniature.
- **Atrium's body**, three paragraphs tightened; the honest-state sentence
  ("No users, no release, and the acceptance harness has never passed") is
  verbatim and stays.
- **Numeris**, two paragraphs → one.
- **"Also running"**, one sentence each.
- **The Stack run-on line** → a three-row table.

Every cut is recorded in a comment next to where the text used to be, so the
next session can see what was removed rather than rediscovering it.

## A or B

**A — the object dominates.** `DOMINANT = "blueband"`. Committed.

The argument in a sentence: A opens on a made thing, which a reader understands
in two seconds without reading a caption, where B opens on an abstract dot
field that means nothing until its caption has been read — and B pays for its
lattice by shrinking the only physical object on the page to a pale 760-unit
render.

B is genuinely the stronger single image, and if the page is for engineers
rather than for recruiters that argument wins. It is one word in
`generators/content.py` and `make build`.

Both rendered from the current build, dark, at GitHub's own widths:

- **A** — `.review/preview/C-dark-desktop.png`, `C-dark-phone.png`, and the
  first light renders, `C-light-desktop.png`, `C-light-phone.png`.
- **B** — `.review/preview/D-dark-desktop.png`, `D-dark-phone.png`.

Measured at a 1012px viewport (997px of content): A is 3657px on a desktop and
3917px on a phone; B is 3620px and 3917px. No comparison is offered against the
earlier `A-*`/`B-*` captures — those were taken at a different viewport width,
so the heights are not comparable and quoting a delta would be inventing one.

The showroom crop for Atrium was also retuned: `(0.42, 0.44, 1.00, 0.86)`,
**52.2% inked against the previous 28.8%**, because at 760 units the old crop
was mostly empty field.

## What is open

1. **The A/B choice is yours**, and it is the only thing in the task I did not
   settle. A is committed because something had to be.
2. **Browser coverage of the theme switch is one engine deep.** The
   `prefers-color-scheme` behaviour inside an `<img>`-referenced SVG was
   verified in Chromium only. If an engine does not evaluate it, the asset
   falls back to its declared default — dark ink, dark ground — which is
   exactly what the page did before this session, so the downside is bounded at
   "no worse than the version you already have", not at "broken".
3. **The pip is 3px on a phone.** It reads because it travels 93px, not because
   it is large. If it disappears for you on a phone, the fix is `PIP_R` in
   `generators/svg/hero.py` and nothing else.
4. **`make build` is idempotent** — the README's hash is unchanged across two
   consecutive runs — and `data/atrium-tokens.json` was not touched;
   conformance reports the vendored copy current.
