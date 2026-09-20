RESULT: PASS
GATE: green — `python3 -m pytest tests -q` (14 passed, 2 skipped) then `python3 -m generators.build`, run after the last edit, and the build is idempotent (a second run rewrites nothing). The gate does not cover this task and cannot: every one of the four points is a judgement about how the page looks, and the gate checks that the tests pass and the build reproduces. What carries the verdict below is eight rendered pages — before and after, dark and light, 1012px and 390px — in `.review/archive/2026-09-19T1603-*.preview/`. Two tests changed; neither was relaxed. Both asserted the existence of the thing point 4 removes, so they now assert its absence and that the record it carried is still derived and still on the page as markdown.
SESSION: 95b4194d-273a-44ae-a78e-3a47f1a76c55
HUMAN: All four are done and the page is about a third shorter. Atrium now opens the page under your name and takes the full column, and its crop had to change to do it — the old band was cut to sit at 760 wide and at 1200 its left half is a void, which I measured rather than guessed. BlueBand's render is gone rather than shrunk. The dots came off: they encoded one mark per contribution shaded by month, which is real and is unreadable at 2px of pitch on a phone, and the page already said the same thing twice elsewhere — the four figures under your name, and the snake at the bottom. Two things I decided that you did not ask for by name, both one line to reverse: BlueBand's little CAD→PCB→FIRMWARE→APP strip went too, because you asked for BlueBand at "the same weight as the others" and Numeris has no diagram; and "Start here" went, because with Atrium leading and every project down to one line, its three lines were each restating the project body a screen below them. If either was wrong, say so and it is back in a word.
PREMISE: The task's premise held on all four points and the fourth was sharper than it looks. "I don't get all the dots under my name" reads as a complaint about taste; it is actually a correct reading of a plot whose encoding cannot survive its own rendered size. The measurement is below. One sub-premise in the task is slightly off: it guessed the dots were "the hero's halftone dot screen or a data strip" — they were neither, they were a unit field, one mark per contribution.

# The profile reads as Atrium-first, with fewer words and nothing he has to decode

Task: `.review/archive/2026-09-19T1603-atrium-first-fewer-words-nothing-to-decode.task.md`
Commits: `9614feb` (the two earlier reports, committed before starting, as asked) and `8a3c601` (this task).

## Before starting: the working tree

The task asked for the dirty tree to be read, committed as its own commit naming the 12:45 and 14:57 reports, and for anything unexplained to be reported rather than committed. Every diff traced to one of the three tasks already archived today:

| File | Belongs to |
| --- | --- |
| `.github/workflows/snake.yml` | 12:45 — snake restyled to Atrium's density ramp |
| `generators/**`, `assets/**`, `README.md` | 12:45 and 14:57 — dark field everywhere, plates grounded, 14 assets to 7 |
| `Makefile`, `bin/page_preview.py` | 14:10 — `make page` renders the whole README |
| `data/atrium-tokens.json` | 12:45 — the vendored token set |
| `.gitignore` (`.playwright-mcp/`) | 14:10 — preview tooling |
| `.claude/gate.timing` | the gate's own cached timing, 0.7 to 4.1 |

Nothing was unexplained, so nothing was held back. That is `9614feb`.

## The four points

### 1. BlueBand shrinks, and the band render goes — MET

`showroom-blueband-concept` is deleted from `content.SHOWROOMS`, so the asset is no longer generated and no longer referenced. It was the three-quarter halftone of the module and band, drawn at the full 1200-unit column — the largest object on the page, sitting above the project that was meant to be leading it.

It is removed rather than reduced to a smaller plate, because a smaller copy of a picture you do not want is still the picture. The source is public and unchanged at `raw.githubusercontent.com/thomasvanpul/blueband-concept/main/renders/01_three_quarter_with_band.png`, and reinstating it is the dict entry and nothing else.

**The judgement call.** The build-chain strip (`CAD → PCB → FIRMWARE → APP`) went too, and the task did not ask for that by name. The reasoning: the task says BlueBand "stays as a project line at most, same weight as the others", and the section it is being levelled with — Numeris — carries no diagram. Leaving the strip in place would have left BlueBand visibly heavier than the thing it was told to match. It is the smaller of the two things it could have been, so it is the reversible one: delete `"flow": False` from `content.FEATURED["blueband-concept"]` and it is back. If the intent was only the big render, that is the one-word correction.

BlueBand is now a heading, one line, and its repo line.

### 2. Atrium becomes the lead — MET

`content.DOMINANT` is `"atrium"`, so the order is Atrium, BlueBand, Numeris and the lattice takes the full 1200-unit column instead of 760. Atrium is now the first thing under the name and the four figures.

**The crop had to change, and this is the finding of the task.** The existing band, `(0.42, 0.44, 1.00, 0.86)`, was chosen in an earlier session to sit at 760 wide. Simply drawing it at 1200 looked wrong, so I measured mean darkness per sixth of the frame, left to right, on the reduced 0–9 grid:

| Crop | Mean | Sixths, left to right |
| --- | --- | --- |
| `(0.42, 0.44, 1.00, 0.86)` — old | 2.95 | 1.3 · 0.7 · 2.0 · 3.6 · 5.3 · 4.7 |
| `(0.70, 0.56, 1.00, 0.80)` — new | 5.07 | 4.2 · 5.1 · 5.8 · 5.6 · 5.2 · 4.5 |

The old band's left half is effectively empty, so at full width the picture sat in the right-hand third of its own frame with a void beside it. The same imbalance was present at 760 and small enough to miss. The new band is evenly inked across the full width and is still a wide band (132×69) rather than the near-square a deeper crop gives, because the lead image sets the height of the first screen.

Note the earlier session's comment claiming "52.2% inked" for the old crop: ink *presence* was 71.3% and hid this entirely, because a barely-visible level-1 cell counts as inked exactly like a level-9 one. Mean level is the measure that shows it.

### 3. Much less text everywhere — MET

Measured on the rendered page at the 1012px profile column, which is what GitHub serves a desktop reader including at a 1440px viewport:

| | Before | After |
| --- | --- | --- |
| Visible words on the page | 511 | 330 |
| Paragraphs | 27 | 20 |
| Longest paragraph | 3 lines | **2 lines** |
| Rendered page height, dark desktop | 3,659px | 2,629px |
| README bytes | 5,744 | 4,156 |
| Generated assets | 6 | 4 |

The constraint "no paragraph anywhere longer than two lines at 1440px" is met: the longest is two lines, and there are only two of those (Atrium's first and second paragraphs). Every project is one line: BlueBand, Numeris and all four "Also running" entries.

Nothing true was dropped. What went was restatement — "moving forward through it is moving back through the history" is "depth is recency" said twice; "one frozen binary, 33 runs over 6.5 hours, 448 values compared per run" is the shape of the 13-of-33 figure rather than a second finding; "it would be dishonest to file it as anything else" is the sentence before it defending itself. **Atrium's honest-state claim is intact in full** — "No users, no release, and the acceptance harness has never passed." — as `Atlas/Projects/Atrium/Verified-Record.md` requires. The table of measured figures is untouched.

**"Start here" was cut, and this is the second judgement call.** It was a heading and three links, one per project, each with a one-line claim. Two of the four points remove its reason to exist: Atrium is now the first thing under the name rather than the fourth, and every project body is now the single line that "Start here" was already setting — so the page stated each project's claim twice, a screen apart, and the first statement was the one the eye hit first. Reinstating it is the `START_HERE` block in `content.py` and `_start_here` in `build.py`.

### 4. The dots under his name — MET, by removal

**What they were.** Not a halftone screen and not a data strip, which is what the task guessed. They were a *unit field*: one mark per contribution, all 2,774 of them, packed left-to-right on a 6-unit pitch in chronological order, with opacity alternating 0.60/0.34 per calendar month and a 1-unit hairline dropped at each month boundary. The width of each tonal band was that month's volume. The encoding was real and it was honest.

**Why it could not be read.** The plate is a 1200-unit viewBox in a fluid column, so it renders at 0.84× in GitHub's 1012px profile column and 0.33× on a 390px phone. That puts the pitch at 5.1px and **2.0px** respectively, and the marks at 2.5px and 1.0px. At phone width the entire field is a uniform grey bar. Even at desktop, the two opacity bands on a near-black ground do not separate — the zoom in `before-hero-dots-zoom.png` is the evidence, and it is why "shaded by month" was invisible and the month rules were not there at all. Thomas's reading was correct: a picture whose meaning needs its caption to survive is the caption doing the work.

**Why removal rather than a two-word label.** The task allowed either. Removal wins because the page already stated the same record twice more, both legibly: the four figures directly beneath it (**2,774** contributions · **78 of 370** days active · **151** busiest day · **45** longest streak), and the contribution snake in the footer, which is a real calendar on Atrium's density ramp. The unit field was the third statement and the only illegible one. A label would have kept the height and added a word.

**What changed.** `_unit_field`, `_x_for` and `field_span` are gone from `svg/hero.py`, with the `FIELD_*` geometry. `content.FIELD_LEGEND` — "One mark, one contribution, shaded by month" — is gone with the field it captioned, and so is `build._field_legend`. The hero's viewBox drops from 268 to **144**: 268 was the name, its rule, the planet and then 84 units of field, and leaving it would have left an empty third of a plate that reads as a gap nobody put there.

**What stayed.** `readout_figures` still lives in `svg/hero.py`, so the numbers are still derived beside the figure and formatted by `build.py`. The planet, its six month-rings and the one moving pip are untouched — the rings still encode the last six monthly totals, and they are the reason the hero still differs depending on the contribution data.

## The two tests

Both asserted the unit field. Neither was weakened:

- `test_hero_draws_one_mark_per_contribution` counted `h.01` segments and asserted the count equalled the contribution total. The marks are gone, so the assertion could only be rewritten or deleted — and deleting it leaves nothing to notice the field quietly returning. It is now `test_hero_plots_no_contribution_field_and_still_derives_the_figures`: asserts `h.01` is absent, asserts the viewBox is `0 0 1200 144`, and asserts `readout_figures` still returns the four captions and the right total.
- `test_tokenless_build_reproduces_the_tokened_one` used `"h.01" in hero_svg` as its proof that contributions reached the render. That proof is gone, so it now asserts the hero built with contributions differs from one built with none, and that the planet's ring dasharrays are present. The test's actual subject — that a tokenless build reproduces a tokened one from the cache — is unchanged and still passing.

## Odd, and one thing worth keeping

**The phone stills were wrong twice before they were right, and it was my harness, not the page.** Headless Chrome on macOS clamps the viewport to a 500px minimum. Asking for `--window-size=390` silently renders at 500 and then crops the screenshot to 390, which cuts 110px off the right of a centred body and looks *exactly* like text overflowing the page. I nearly filed a phone-width layout bug that did not exist. The shot script now uses 1044 for desktop (1012 column + 32px of padding) and 500 for phone, and the corrected before-stills were regenerated from a throwaway git worktree at `9614feb` so the comparison is like-for-like. Anything measuring this page in a headless browser needs to know this.

**`data/showroom-blueband-concept.json` was deleted** — the cached luminance grid for the removed showroom. Nothing reads it now that the `SHOWROOMS` entry is gone, and it regenerates from the public source if the entry comes back.

**Not pushed**, as the task required. Stills first.

## Verify, as asked

- `make page` at 1012px and 390px, dark and light, before and after: eight files in `.review/archive/2026-09-19T1603-*.preview/`, plus three zooms — `before-hero-dots-zoom.png` (the dots, which is the clearest evidence in the set), `after-hero-zoom.png`, and `after-atrium-lead.png`.
- Gate green without loosening: 14 passed, 2 skipped, build reproduces and is idempotent.
- Light theme checked as well as dark; the lattice inverts, the links stay blue, the one warm pip survives.
