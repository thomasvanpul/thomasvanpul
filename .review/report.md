RESULT: PARTIAL
GATE: green — `python3 -m pytest tests -q` (11 passed) then `python3 -m generators.build`, run after the last edit
SESSION: 41f3a5f2-e94f-40b4-acad-7b1b6c59aa3e
HUMAN: The page now carries a dense hero built from the real contribution record, a BlueBand showroom, an honest Atrium section and three differently-shaped featured entries. Two of the three showrooms you named are not automatable and I say why. The snake restyle is written but unverifiable from here — a GitHub Action has to run before either of us can see it.
PREMISE: One premise in the task is wrong: the six `rule` SVGs were six *references* to one cached file, so they cost one request, not six. The aesthetic objection stands and I cut them anyway.

# A profile with something to look at

## Look at these first

| | |
|---|---|
| the page, dark, in order | `.review/preview/page-dark.png` |
| hero alone | `.review/preview/hero-dark.png` |
| BlueBand showroom | `.review/preview/showroom-blueband-concept-dark.png` |
| Atrium figures strip | `.review/preview/atrium-figures-dark.png` |
| everything at phone width | `.review/preview/phone-375px.png` |

Everything new was rasterised with `make preview` and looked at. `make preview`
had to be fixed first: it composited every theme onto transparency, which
viewers show as white, so a dark-theme asset drawn in `#e6edf3` rasterised to a
blank page. It now passes `-b` per theme.

## Cost, measured

Counted from the generated README by matching each `<picture>`'s `<source>` for
one colour scheme, which is what a browser actually fetches. Bytes are the
on-disk size of the dark-theme assets; gzip is what the wire carries, since
GitHub serves SVG compressed.

| | requests | raw bytes | gzipped |
|---|---|---|---|
| before (HEAD) | 7 | 28,969 | 5,413 |
| after | 7 | 115,810 | 24,952 |
| change | **0** | +86,841 | **+19,539** |

Request count is unchanged: `rule` and `stats` left, `showroom` and
`atrium-figures` arrived. The snake is the eighth request in both columns and is
external — measured live at 44,855 bytes, unchanged by this work.

**+19.5 KB gzipped is the honest cost of the redesign**, and it buys the hero
field (8.8 KB gz) and the product showroom (12.7 KB gz). For scale, the snake
alone is heavier than every generated asset on the page put together was
before. I did not treat this as a "materially slower" stop condition; if you
disagree, the showroom's `cols` in `content.SHOWROOMS` is the single dial.

## Part 1 — the hero

`generators/svg/hero.py`, rewritten. 1200×340.

**What each element encodes:**

| element | encodes |
|---|---|
| unit field | one mark per contribution — all 2,774 of them, chronological, packed on a 6px pitch. Shading alternates per calendar month; a hairline drops at each month boundary, so each tonal band's width is that month's volume. |
| readout row | 2,774 contributions · 78 of 370 days with commits · 151 busiest day · 45 longest streak |
| planet rings | the last six calendar months, outermost oldest. Each ring's drawn arc is that month's share of the largest of the six. |
| planet core + horizon arc | **nothing.** The only two marks on the canvas that encode no number. Kept deliberately as an identity mark, and named here rather than smuggled in. |
| name, subtitle, cursor | unchanged; `HERO_SUBTITLES` rotation intact. |

**What I built first and threw away.** The obvious plot is one mark per *day*,
height = that day's count. I built it, rasterised it, and it was four fifths
empty canvas — because 292 of the 370 days in the window have no contributions.
It was honest and it was exactly the failure the task names. The counts are
identical either way; only the unit changed. One mark per contribution is the
same record at the density it deserves.

The old `stats.svg` panel is gone — its three numbers are in the readout row.
They were previously a separate request, one screen below the field they
describe.

**Dropped:** the 27 hand-frozen `STARS`. Random positions, random opacities,
traceable to nothing.

## Part 2 — showrooms

**BlueBand — automated.** `blueband-concept` already commits six canonical
renders publicly. The build fetches `01_three_quarter_with_band.png` (1.9 MB),
reduces it to a coarse luminance grid, and draws it as a halftone dot screen:
4,713 marks, size carrying luminance, in the profile foreground colour. It
inverts correctly between themes because the mark is the ink. 57 KB raw /
12.7 KB gzipped, against 1.9 MB if the render were referenced directly — and a
photographic raster would have read as a foreign object on a page of line work.

The grid is committed to `data/showroom-blueband-concept.json` (8 KB), so CI
does not re-download 1.9 MB per run and an offline build is identical. Ingest
needs Pillow; without it the build falls back to the committed grid, and
without that the showroom is simply absent. **A profile build never fails
because a picture was slow.**

**Atrium — not automatable. ** Stills exist at `~/.atrium/stills/<sha>/` and are
current, but two things stop them:

1. **They are not product shots.** I looked at `09a9dcf/lattice-0100x.png` and
   `lattice-kinds-detail.png`. They are diagnostic lattice and census renders in
   a red palette — visually striking, genuinely on-reference for the GMUNK
   comparison, and a misrepresentation of what Atrium is if captioned as a view
   of it.
2. **CI cannot make one.** The profile build runs on `ubuntu-latest`; Atrium is
   Metal on macOS and needs a GPU and a display. No workflow in this repo can
   produce that image.

The only automatic route is a push *from Atrium's own build* on your machine
into this repo. That is real automation, but it lives in Atrium, not here, and
it publishes a private project's render. I have not done it — it is outside
this repo and it is your call.

**Interstellar Sanctuary — not automatable, and the page was wrong about it.**
`https://interstellarsanctuary.com` returns **HTTP 401**, `www-authenticate:
Basic realm="interstellarsanctuary"`, body `This site is temporarily private.`
A headless screenshot in CI would capture a password prompt. The question of
what Playwright costs in workflow time never arises.

Separately: the README claimed **"Live at interstellarsanctuary.com"**. It is
not live to anyone without the password. I changed the line to say it is behind
a password while data licensing is settled — **please confirm that wording is
right**, since I inferred the reason rather than being told it.

## Part 3 — Atrium on the profile

`content.ATRIUM`. Every figure copied from
`Atlas/Projects/Atrium/Verified-Record.md`, measured 2026-09-16. Nothing written
from memory of a conversation.

The section leads with the figures strip — 18,470 lines / 418 assertions, 38% of
code / 218,016 events, 31 repos / 10 MB resident, 0% idle CPU — then the drift
story (13 red verdicts in 33 runs of unchanged code; one frozen binary run 33
times over 6.5 hours, 448 values compared per run), then the honest-state
paragraph: **no users, no release, all eleven acceptance criteria UNMEASURED,
3 of 19 interface elements built.** That paragraph is not optional and the card
renderer treats it as body text like the others so it cannot be quietly
dropped.

## Part 4 — breaking the template

Three shapes, chosen by what each project's evidence actually is:

* **BlueBand → the object first.** Its whole point is a physical thing. The
  render carries more than the first paragraph does, so it sits above the
  prose, with the flow diagram after as the build chain.
* **Numeris → prose first.** What makes it interesting is a claim in words —
  that daily use forced the rate limits, dirty data and cache invalidation to
  be dealt with. The flow diagram is the supporting exhibit, so it sits between
  the claim and its consequence.
* **Atrium → a number first.** No public repo to link, no diagram worth drawing
  at this size. What it has is measurements, so it opens with them.

**The six rules are cut.** Correcting the premise: they were six references to
one file, so one cached request and ~600 bytes, not six requests. But it was
the same mark six times carrying nothing, which is the objection that mattered.
Sections are now separated by their own shape and a plain `---`, which costs
nothing. `generators/svg/rule.py` and `stats.py` are deleted.

## The snake

**Kept.** `Platane/snk` takes per-output query parameters — verified against the
action's own README, which documents `color_snake` and `color_dots` (exactly
five colours, index 0 = a day with no contributions, then low to high). Both
outputs in `snake.yml` now request the profile palette: a neutral grey ramp
ending on `#e6edf3` for dark and `#0d1117` for light. Filenames are unchanged,
so `content.py` needed no edit.

**This is the unverified part of the work.** The `output` branch still holds the
old green SVGs and will until the snake workflow runs. I cannot trigger it and I
have not looked at the result. If the colours come out wrong, the fix is two
strings in `snake.yml`.

## Two things I fixed that were not asked for

**`make build` did not reproduce the page.** A build with no `GITHUB_TOKEN`
silently dropped the contributions panel and rewrote README.md without it. That
is why the tree was already dirty when I started — `assets/stats.*` deleted and
7 lines gone from README.md — and it would have happened on every local run and
every Stop-hook gate, since the gate runs without a token. The build now commits
`data/contributions.json` (the total plus the raw day series; everything else is
derived, so the cache cannot disagree with itself) and replays it when there is
no token. Verified: two consecutive builds, one tokened, one not, produce a
byte-identical README. There is a test for it.

**The build could write invalid XML and the gate would pass.** My first hero
put a double-quoted font family inside a `style="..."` attribute, which closes
the attribute early. `python3 -m generators.build` wrote it happily; only
`rsvg-convert` rejected it. There is now a test that parses every emitted SVG
with ElementTree, both themes.

## Workflow changes — required, as the task asked me to flag

`.github/workflows/` is touched three times, each because a chosen option
needed it:

* `profile.yml`: `pip install ... Pillow` for the showroom ingest.
* `profile.yml`: `git add README.md assets/ data/` — without `data/`, the
  committed caches drift from what CI last saw and offline reproducibility
  quietly dies.
* `snake.yml`: the palette parameters above.

**None of these have run.** CI has not been exercised by this session.

## Phone width

Rasterised at 375 px: `.review/preview/phone-375px.png`.

The name, the four big readout figures, the Atrium lede number, the unit field
and the showroom all survive — the halftone in particular reads better small
than large. **Every 9–10 px caption does not.** At 375 px they are ~2.8 px tall
and reduce to a grey smudge: the readout captions, the Atrium figure captions,
the flow sublabels. This was already true of the old page's stats captions and
flow sublabels; it is not a regression, and it is not fixable inside
`<picture>`, which selects on colour scheme and not on width. The mitigation
that does work is the `alt` text, and the hero and figures strip both carry
their numbers in full there.

## Not done / open

* **Snake colours unverified** — needs one workflow run.
* **CI unverified** — Pillow install and the widened `git add` have not run.
* **Interstellar Sanctuary wording** — I inferred "while the data licensing is
  settled". Correct it if that is wrong.
* **Atrium showroom** — deliberately not built. Needs a decision from you about
  publishing a private project's render, and the work belongs in Atrium's repo.
* The `data/` caches are now part of what CI commits. If you ever want a
  genuinely clean rebuild, delete them and run a tokened build.
