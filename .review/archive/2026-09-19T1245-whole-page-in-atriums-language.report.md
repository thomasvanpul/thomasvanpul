RESULT: PASS
GATE: green — `python3 -m pytest tests -q` (11 passed, 2 skipped) then `python3 -m generators.build`, run after the last edit. The gate does not cover this task: it proves the build reproduces and the SVGs parse, and says nothing about colour, field or legibility. Everything visual below is carried by the rasterised evidence, not by the gate.
SESSION: b8a38235-2889-435e-90b6-fe506e67bee6
HUMAN: The whole page is on Atrium's palette now, taken from the generator you already built rather than picked by eye — `atrium-design` was already naming this repo as a consumer that had never been wired up, and its own audit went from 2 stray colours to 0. Every asset paints Atrium's field before it draws anything, so nothing floats on GitHub's chrome. You chose dark-field-everywhere over a light variant, and the consequence has been carried through: 14 assets became 7, every `<picture>` became an `<img>`, and the page is half the bytes. The four `---` rules are gone. The one thing GitHub will not let us fix is the prose between the plates — that typography is not ours, and I say exactly what it strips.
PREMISE: The task's premise held. "The pieces are right; everything between them is not" was accurate, and the specific diagnosis — that the assets were transparent and on GitHub's greys — was confirmed by an independent audit that already existed in `~/dev/atrium-design`. One sub-premise was wrong in a small way and is corrected below: the snake's restyle had not "never published", it simply had not run yet.

---

# The whole page in Atrium's language

## The central constraint, stated plainly

**GitHub strips everything that would let a README set its own typography or
ground.** Specifically, in a rendered README it removes `<style>` blocks,
`style=` attributes, `class` and `id`, and anything script-bearing. What that
leaves under GitHub's control and outside ours:

* the page background (`#0d1117` dark, `#ffffff` light, plus dimmed and
  high-contrast themes that are not either of those)
* the body typeface, size, line height and measure
* paragraph and heading spacing, and the rule GitHub draws under an `<h2>`
* link colour
* the tinted chip it draws behind an inline code span
* the width the images are scaled to

What *is* ours, completely:

* the entire contents of every SVG — including CSS inside it, SMIL animation,
  and its own background
* the five dot colours and the snake colour on the contribution snake, through
  query parameters in `.github/workflows/snake.yml`
* the markdown structure: what is a heading, what is an image, what is a rule,
  and whether a number is set in a code span

So the page cannot be a continuous surface. It can be a set of plates that all
belong to the same surface, with GitHub's prose between them. That is the best
achievable version and it is what shipped.

## What was actually wrong, measured

`~/dev/atrium-design` generates one palette from the Swift that runs —
`DayCurve.swift`, `FieldRenderer.swift`, `LatticeRenderer.swift` — and
`bin/consumers.py` already named `thomasvanpul/generators/svg/__init__.py` as a
downstream consumer. It had never been wired up. Its verdict before this
session:

    thomasvanpul/generators/svg/__init__.py
      line 1  #e6edf3  not density-5 #f6eaec, nearest token: sRGB distance 18, hue differs by 142 deg
      line 2  #0d1117  not field-light-edge #150b0c, nearest token: sRGB distance 15, hue differs by 138 deg

Two literals, both GitHub's own greys, both more than 135 degrees of hue from
the nearest Atrium token. **Every mark on the page descended from those two
values**, so the answer to "audit what each generator currently uses" is that
all five were on the same palette and it was the wrong one. Not one of them was
on the warm ramp.

After: `no untracked hex literals`.

The DayCurve range the task quotes, −7.8° to +13.1°, is confirmed in
`data/atrium-tokens.json` under `day_curve.hue_range_deg`. The stylesheet point
is the unweighted mean over the seven distinct anchors: hue 3.07°, lightness
0.132.

## What changed

**The palette is now read, not typed.** `data/atrium-tokens.json` is a verbatim
copy of `atrium-design/tokens/tokens.json`, and `generators/svg/__init__.py`
loads it. There is no hex literal anywhere in the module, including in its
docstring — the audit is a regex and counts those too, which cost two iterations
to notice. Vendored rather than imported so CI builds with no sibling checkout;
`test_vendored_tokens_match_atrium_design_when_it_is_checked_out` compares the
two when `~/dev/atrium-design` is present and skips when it is not.

**Every asset paints Atrium's field before it draws anything.** `field()` emits
a full-bleed rect in `field-light-edge`; hero, orbit, figures, flow and halftone
all open on it. `test_every_asset_paints_the_atrium_field_before_it_draws`
checks both that the ground is there and that it comes before the first mark,
because a ground painted last hides everything. Nothing in the old suite could
tell a transparent asset from a grounded one.

**Two tokens, and only two.** Ink `density-5`, ground `field-light-edge`.
`density-1` to `density-4` carry hue and hue is reserved for state; nothing on
this page has state, so nothing on it gets them. The one exception is the
snake, below, where colour maps to a measured count.

**Light mode.** Three options were rendered and compared. Thomas chose:
Atrium has no light mode, so neither does the page — the same dark field is
served to both themes. The rejected alternative was the symmetric swap, ground
`density-5` and ink `field-light-edge`, which is equally on-palette and equally
legible but reads distinctly rose at full width rather than warm. The third,
a pure-white ground from `density-6`, was rejected as GitHub's white wearing
Atrium's ink.

**The consequence of that choice was carried through rather than left
implicit.** With one field, the two variants render byte-identical bodies, so:

|  | before | after |
|---|---|---|
| files in `assets/` | 14 | 7 |
| bytes in `assets/` | 299,086 | 149,907 (−49.9%) |
| README | 8,227 bytes | 5,730 bytes (−30.4%) |
| asset filename | `hero.156d9d0-dark.svg` | `hero.13aefe1.svg` |
| markup per figure | `<picture>` + 2 `<source>` + `<img>` | one `<img>` |

**The snake is the one element that still needs two sources, and it is the one
element that cannot carry Atrium's field.** It is built by Platane/snk, its
background is transparent, and `snk` accepts no background parameter — only the
five dot steps and the snake colour. An asset that cannot paint its own ground
has to adapt to the ground it is given, so `prefers-color-scheme` still earns
its keep there and only there. Its five dot colours are the one place on the
page where hue is carrying information: index 0 is a day with no contributions
and the rest run low to high, which is Atrium's density ramp exactly. Dark runs
`density-0` → `density-4` forwards, light runs it backwards, so in both themes a
busier day sits further from the page behind it.

**The four `---` rules are gone.** A horizontal rule drawn by GitHub is a mark
this repo does not control, in a colour it does not choose, carrying no count,
no scale and no gradient. Nothing here earned a separator, so there is none:
each section opens on its own field and the edge of that field is the boundary.

**Figures in prose.** The figures strip already exists and already carries the
Atrium section's measurements. Inside prose the only lever GitHub leaves is the
code span, so the two headline measurements — `13 of 33` and `3 of 19` — are set
in it and the supporting numbers are not. A second figures strip mid-section was
considered and rejected: it would be the same layout template twice inside one
section, which is the objection already raised once.

## Numbers, and where they were measured

| | value | measured by |
|---|---|---|
| stray hex literals in this repo, before | 2 | `~/dev/atrium-design/bin/consumers.py` |
| stray hex literals in this repo, after | 0 | same, re-run |
| hue distance of the old greys from the ramp | 142° and 138° | same |
| ink on field, contrast | 16.50 : 1 | WCAG relative-luminance, computed this session |
| previous dark contrast | 16.02 : 1 | same |
| previous light contrast | 18.92 : 1 | same |
| plate against GitHub dark canvas | 1.02 : 1 | same |
| plate against GitHub light canvas | 1.17 : 1 | same |
| assets | 14 → 7 files, 299,086 → 149,907 bytes | `git ls-tree` vs `wc -c` |
| tests | 11 passed, 2 skipped | `python3 -m pytest tests -q` |

Contrast is preserved: 16.50:1 is above the previous dark figure and below the
previous light one, and both are far above AAA's 7:1. The plate figures are
deliberately near 1:1 — the plate differs from the canvas in hue, not in
luminance, which is why it reads as warmth rather than as a stripe.

## Evidence

`make page` is new. `make preview` rasterises assets one at a time, which
answers "is this asset right" and not "does this page hold together" — the
question that has now been failed twice. `bin/page_preview.py` renders the
whole README through **GitHub's own markdown renderer** (`gh api /markdown`), so
the HTML structure, heading sizes and code spans are not an approximation; the
surrounding canvas colour, text colour and content width are Primer's published
values written out in the script, and the profile column is slightly narrower
than the 1012px used here. Read the output as very close, not pixel exact.

* `.review/preview/page-dark-desktop.png` — the whole page, dark, 1012px
* `.review/preview/page-light-desktop.png` — the whole page, light, 1012px
* `.review/preview/page-dark-phone.png` — dark, 390px
* `.review/preview/page-light-phone.png` — light, 390px
* `.review/preview/asset-hero.png`, `asset-atrium-figures.png`,
  `asset-showroom-atrium.png` — three assets on their own

The snake in those renders is not the published file. The `output` branch was
last deployed 04:06 UTC on 2026-09-19 and `snake.yml` was restyled at 11:59 UTC
the same day, so what is published is still Platane's stock ramp with a purple
snake. The script fetches it and substitutes the colours the workflow now asks
for, which is what the next scheduled run will produce. **This is the one part
of the page neither of us can verify from here** — a GitHub Action has to run.
The cron is every 12 hours.

## Open, and not done

* **The snake is unverified in production**, as above. Until the workflow runs,
  the live page still shows a green snake with a purple head, which will be the
  only element on it not in Atrium's language.
* **Phone width degrades the wide diagrams.** At 390px the hero readout and the
  flow stage labels are below legible size, because the SVGs are authored at
  1200px and scaled. This predates the task and is unchanged by it, but it is
  visible in `page-dark-phone.png` and is the obvious next thing. A fix means
  authoring a second, narrower composition, not scaling the same one.
* **GitHub's non-default themes were not checked.** Dimmed (`#212830`) and the
  high-contrast themes serve a different canvas, and the plate was tuned against
  the default dark. It will still read as a warm plate; it will sit differently.
* **`density-6` is unused.** It is held for the focal set and nothing on this
  page is focal, which is correct, but worth recording so it does not look like
  an oversight.

## Corrections to things said earlier in this session

The first reading of the published snake was that `snake.yml`'s restyle "had
never published" and its comment was therefore false. That was wrong: the
restyle landed in `f1d88fc` at 11:59 UTC today and the branch was last deployed
at 04:06 UTC, so it is simply pending. The comment described the next run.
