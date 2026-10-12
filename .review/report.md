RESULT: PARTIAL
GATE: pytest 12 passed, 3 skipped (2 live-API smokes: no usable token in this session; 1 needs a sibling atrium-design checkout). Tokenless `python3 -m generators.build` run twice: second run leaves the tree unchanged. Render check through cmark-gfm plus a sanitiser, photographed in Chromium at 390px and 1280px, dark and light, cards closed and open: no horizontal overflow. GitHub's own markdown API was NOT run (refused from this session), so the render on github.com itself is unverified.
SESSION: cloud
HUMAN: Which thomasvp.com/work/<id> case pages exist for Atrium, BlueBand and Numeris? Nothing in this repo names one, so the cards link to repos and to thomasvp.com only.
PREMISE: Mostly ok. Two things in the task could not be done as written: `gh api markdown` is refused from a cloud session, so cmark-gfm stood in for it; and the task says to open a PR, but the run instructions say not to, so this is pushed to the cloud/ branch with no PR.
SHOW: design/interactive/after/dark-desktop-open.png

# GitHub profile: interactive, not animated

## What a visitor can now click or open

Before: one 1.5 MB looping GIF of the corridor (one each for light and dark), then name, line and links. Nothing to open; the image was not a link.

After, top to bottom (`README.md`):

1. **A still of the corridor**, docked on Atrium's surface lane. It is a link to thomasvp.com, and it switches between light and dark with the reader's theme.
2. Name, line, the three links, unchanged.
3. **A self-updating line**: "Most recent push to a featured public repo: <repo>, <date>." The daily `profile.yml` run rewrites it from the repo list the build already fetches, so it costs no extra API call and can only show public repos. A tokened build caches it in `data/activity.json` so `make build` offline prints the same line.
4. **Five `<details>` cards, closed by default**:
   - **Atrium**: what it is, the measurement paragraph, the honest-state line, the 2026-09-16 figures table, "Private repo." No picture inside, because the still at the top is Atrium's.
   - **BlueBand**: a still docked on the blueband-concept lane, which links to the repo, then one line and the repo link.
   - **Numeris**: a still docked on the Finance-Tracker lane, which links to the repo, then one line and the repo link.
   - **Also running**: the four items, including the password-gated Interstellar Sanctuary link.
   - **Stack**: the three-row table.

All copy comes from `generators/content.py` text that was live on the page before 24 Sep, with em dashes removed and nothing added. Each still is drawn from `data/field.json` (real commits, 2025-09-14 to 2026-09-19), and every count it shows is also in its alt text.

## What changed

- `generators/corridor.py`: `lane_still()` draws one frame of the flight, docked on one lane, at that lane's busiest week. I first used the middle of the loop's own schedule window. For Atrium that put "195 COMMITS" over an empty February lane, so I dropped it and anchor on the peak week instead, 4 frames back so the marks sit inside the rails.
- `bin/cards.py` (new): draws the six stills plus `design/cards/cards.json` (lane counts and date range for the alt text). The build only reads these files, so it needs no Pillow and no font.
- `generators/build.py`: ships the card stills under content hashes, renders the cards, the linked pictures and the push line, and writes `data/activity.json`. The orphan sweep removed both GIFs and the old stills from `assets/`. `assets/` went from 3.0 MB to 208 KB.
- `generators/animate.py`: `_font` falls back to DejaVu Sans Mono when macOS Menlo is missing.
- `.github/workflows/profile.yml`: also rebuilds on `design/cards/**` pushes. Comment explains the new data file.
- `tests/test_build.py`: the motion test is replaced by `test_nothing_on_the_page_moves` (every shipped asset is a non-animated PNG, no snake, no GIF). New `test_the_page_is_something_a_visitor_opens_and_clicks` checks: no style or script, every card is a closed `<details>` with the blank line after `</summary>`, and every picture is a link. New `test_the_push_line_is_the_most_recent_featured_repo` covers the push line, its cache and the tokenless replay. The size budget is now 100 KB per still (largest is 35 KB). The text test checks the alt counts and that there are no em dashes.
- `bin/page_shots.py` (new): the render and photo harness. It uses `gh api /markdown` when it can and falls back to cmark-gfm otherwise. `render.txt` records which one ran.
- The GIFs are still in `design/hero/flight/assets/`, so `git revert` or `content.HERO_PICK` can bring the animated page back.

## Renders

- Before: `design/interactive/before/{dark,light}-{phone,desktop}-closed.png` (GIF photographed on its first frame).
- After: `design/interactive/after/{dark,light}-{phone,desktop}-{closed,open}.png`.
- Page height, cards closed: 900px on a phone, 926px at 1280. All cards open: 2,698px and 2,655px.

## What failed or was not done

- **No render through GitHub itself.** The GitHub API answers "sessions are bound to their configured repositories" for `/markdown`. cmark-gfm is the same library GitHub uses, but its sanitiser and CSS are approximated. Check it once on github.com after merge, in particular that `<a><picture>` stays clickable.
- **No thomasvp.com/work/<id> links.** thomasvp.com cannot be reached from here and no repo file names a case page, so I invented none (see HUMAN).
- **Issue-driven element: not built, on purpose.** On a public repo anyone can open an issue. An Action that writes visitor input into the README is a defacement and spam channel, and making it safe takes moderation, which defeats the point. Without moderation it cannot be done safely.
- **Font:** the six stills were drawn here in DejaVu Sans Mono, not Menlo. The glyphs are near-identical, but not byte-identical to a Mac build. On a Mac, `python3 bin/cards.py && make build` redraws them in Menlo.
- **`data/activity.json`** was seeded from `data/repos.sample.json` (Finance-Tracker, 2026-08-18) because the live repo list is unreachable here. The first CI run after merge overwrites it with the real latest push.
- **Live smoke tests** were skipped here. They run in CI with the Actions token.
- **No PR**, per the run instructions.

## What is left

- Thomas: case-page ids, if he wants the cards to link to them.
- After merge: look at github.com/thomasvanpul in both themes and on a phone, and confirm the first daily run rewrote `data/activity.json`.
