RESULT: PASS
GATE: green — `set -e; python3 -m pytest tests -q` (11 passed, 2 skipped) then `python3 -m generators.build`, 0.5 s, run after the last edit and again by the Stop hook. It covers the build and the page's shape; it does not judge the plate by eye, and the light-ground finding below is outside it.
SESSION: b0ac3d03-4c45-4cf0-b303-2873273ffd34
HUMAN: none
PREMISE: held — `design/hero/flight` was still on disk and unshipped, README.md was still the 16 Sep page, and nothing in hot.md or the queue since 19 Sep revises the pick.

# The profile: finish "flight" and make it the README, ready to push

Not pushed. Two commits on `main`, `34cfe6d` and `48c2b7e`. Everything below was measured on this machine on 2026-09-24.

## What changed

**The page is the corridor and three lines.** `README.md` is now one `<picture>` (reduced-motion PNG stills first, then the dark GIF, the light GIF as the bare `img`), then `# Thomas van Pul`, the one line, and the three links. The Atrium section, its figures table, the BlueBand and Numeris cards, Also running, Stack, the snake and the footer are gone with it. 118 words on the page, 18 of them prose.

**The build ships the pick.** `generators/build.py` reads the four files of `content.HERO_PICK` (`flight`) from `design/hero/flight/assets/`, recomputes each name from the bytes (`stem.sha256[:7].ext`), writes them to `assets/`, and sweeps every SVG, GIF and PNG the README no longer names. The four SVGs of the old page were removed by the first run. GitHub data is still loaded, on purpose: the daily CI run is what refreshes `data/contributions.json`, and `bin/field_data.py` lays the corridor's substrate from that cache. `generators/svg/*` and `generators/showroom.py` stay in the tree, uncalled, on the orbit-plate precedent. `bin/hero.py` now previews a finish through the same `hero_picture` and the same `content.NAME` / `LINE` / `FOOTER_LINKS` the build publishes, so the design README and the shipped README are the same bytes.

**The docked panel aligns.** Docked left, the panel's type was right-aligned to the widest lane's panel, so `ATRIUM · HOST` sat up to 60 units to the right of the chronometer's margin and the date line and the counts under it shared no edge. It now anchors to the docking edge: left at x=54, which is the chronometer's own left edge, right at 786. The contact sheet of nine frames confirmed both sides line up at every station. `panel_width` went with it.

**Tests follow the page.** Six tests that asserted the old page (SVG well-formedness, the hero planet, the paints-ground check over the SVG generators, the plain card, the CSS-animation count, the figures-as-text list) are replaced by six that assert this one: hashes from bytes and orphans swept; tokenless equals tokened, and the tokened build still writes the cache; exactly one picture with reduced motion offered before colour scheme and the stills are PNG; `LABEL` and `VALUE` clear 11 px in a 358 px column and the shipped files are really 820 wide; both animations under 1,500 KB; name, line, links and the alt as text, one heading. The gate has no test-file guard, so this needed no exception.

## Sizes

| file | size | frames | loop |
|---|---|---|---|
| `assets/anim-dark.f20941f.gif` | 1,488 KB | 96 at 820 x 402 | 6.7 s as stored (see findings) |
| `assets/anim-light.db374fa.gif` | 1,484 KB | 96 | 6.7 s |
| `assets/still-dark.37dc699.png` | 34 KB | frame 45, Numeris being read | — |
| `assets/still-light.e0f8c07.png` | 34 KB | frame 45 | — |

Both animations are under the 1.5 MB target and the test now pins it. APNG was built for both and was larger (2,375 / 2,348 KB), so GIF ships.

## Loop seam

Mean absolute pixel difference between consecutive frames of the dark GIF: 7.06 (min 1.42, max 16.97). Across the join, frame 95 to frame 0: 7.76. The join is inside the range the loop already uses; the five largest steps are at frames 16, 30, 79, 80, 81, none near it. Confirmed by eye in both films, which each show the join about three times.

## Legibility at phone width

Smallest drawn type is `LABEL` = 31 units in an 820-unit plate: 13.5 px in GitHub's 358 px phone column. `VALUE` = 41 units reads at 17.9 px. `corridor._t` raises below 25.2 units, which is 11 px. `preview/page/dark-phone.png` and `light-phone.png` show all four panel lines and the chronometer readable at 390. Nothing was resized; the numbers held.

## `make page` and the recordings

`make page` rendered the README through `gh api /markdown` at 1012 and 390 in both themes; the four pages were shot and the dark ones filmed with a real Chrome, 8.5 s hold, 3 s scroll, 8.5 s hold:

| film | width | duration | size |
|---|---|---|---|
| `preview/page/hero-desktop.mp4` | 1012 | 21.4 s | 2,927 KB |
| `preview/page/hero-phone.mp4` | 390 | 21.4 s | 639 KB |
| `design/hero/flight/page/hero-desktop.mp4` (committed) | 1012 | 21.4 s | 2,911 KB |
| `design/hero/flight/page/hero-phone.mp4` (committed) | 390 | 21.4 s | 642 KB |

`preview/` is gitignored, so the committed pair under `design/hero/flight/page/` is the one to open; it films the same README bytes.

## The lanes question, resolved

The four projects with no commit data in `data/field.json` (IRIS, HFQ, Interstellar Sanctuary, the air-defence paper) **stay off the page.** Measured first: IRIS at `~/iris` has 242 commits in the window, more than blueband-concept's 13, so the data option was real. But `generators/corridor.py` is written around five lanes in `LANE_ORDER`, the station schedule, the floor layout and both alt strings, and the flight GIF sits at 1,488 KB against a 1,500 KB budget with 96 frames already cut from 112 to fit. A sixth lane is a redesign with a sixth station and a longer loop, not a finish, and this task is weighted light. The links line is not a project list. So the design language wins as written: nothing invented to fill space, and a page that argues three projects well. Recorded as a finding for the follow-up, not a decision closed.

## What a push would change

`main` is 7 commits ahead of `origin/main`, 0 behind: the five automatic snapshots since 20 Sep plus the two here, 278 files. The live page on github.com/thomasvanpul is the 12 Sep layout (centred, dark/light SVG pairs for hero, figures, flows and orbit). A push replaces it with the corridor and three lines, and carries with it everything since: the 19 Sep palette work, both design finishes under `design/hero/` (about 9 MB of GIF, PNG and MP4), `.review/` history, and the new `assets/` (3 MB). `profile.yml` runs on push: its build has a token, refreshes `data/contributions.json`, and commits only if README, assets or data changed. The README does not depend on data now, so that run commits at most the cache. Its pip line installs no numpy and `import generators.build` pulls in neither PIL nor numpy at module level (checked), so the CI import is safe. The stale comment in that workflow about Pillow and the showroom is prose only.

## Findings

- [ ] FINDING: `human` — the light plate's ground is (246, 248, 250), Primer's canvas.subtle, on GitHub's white canvas.default, so in light mode the plate reads as a grey slab with an edge rather than as the page. Dark uses (13, 17, 23), which is the canvas. Thomas picked flight from the dark film; the light pair has not been judged. where: `generators/corridor.py` `palette("light")["ground"]`
- [ ] FINDING: `actionable` — `animate.encode` requests 76 ms a frame (`int(1000/13)`) and Pillow stores 70 ms, so the GIF plays 96 frames in 6.7 s, not the 7.4 s every report has quoted. Either ask for 80 ms (12.5 fps, 7.7 s) or keep 13 fps and accept the number. where: `generators/animate.py:230`
- [ ] FINDING: `actionable` — with a token, `_load_data` still fetches every featured repo and its `.profile.yml` on the daily run though nothing on the page uses them; only the contributions series is consumed, by `bin/field_data.py`. The featured fetch and `_validate`'s "no featured repos" failure are now a way for the build to go red over data it does not use. where: `generators/build.py:116`
- [ ] FINDING: `human` — IRIS has 242 real commits in the window and could be a sixth lane without breaking the no-invented-marks rule; it needs a sixth `LANE_ORDER` entry, a sixth station in the schedule, and the frame budget re-cut. Decide whether the year of IRIS belongs on the page before rebuilding. where: `generators/corridor.py:200`

## What was not done

Nothing pushed, per the task. `tests/test_live_smoke.py` still skips without a token, as before. The `.review/BLOCKER.md` check (`test -f README.md`) passes but was already true before this task; its falsifier is the live page on 15 Oct, which only a push can move.
