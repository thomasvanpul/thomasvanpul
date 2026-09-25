RESULT: PASS
GATE: green — `python3 -m pytest tests -q` (14 passed, 2 skipped), `python3 -m generators.build` exit 0, run at the end; tree unchanged apart from `.review/`. The gate does not cover this task (it is a prose-to-list backfill); it only shows nothing else was disturbed.
SESSION: 648cd987-b726-4a9a-b428-3b6a9c925158
HUMAN: none
PREMISE: held

# Backfill a Deferred block so findings.py scans this repo instead of reporting it unscanned

Read `report.md` (identical to the 19 Sep `profile-in-orhuns-shape` report, checked with `cmp`) and all 10 archived reports. Every open item was checked against current code, git and CI before listing.

## Kept (still true 24 Sep)

- Type floors: `tests/test_build.py:497` asserts >= 3.07% of viewBox (reads 10.98px on a phone), `bin/directions.py:40` asserts >= 11px. A plate set exactly at the test floor fails the preview tool. Reported unfixed in two consecutive reports; both files still carry those values.
- `design/` is 57M, 151 tracked files, and `.gitignore` (5 lines) does not mention it. Whether it stays tracked is Thomas's call.

## Dropped

- Snake colours unverified / CI unverified (18 Sep): `gh run list` shows Generate Snake succeeding on 22, 23 and 24 Sep.
- Wiring the chosen hero into `generators/build.py` (19 Sep): `corridor` is used only by `bin/hero.py`, so it is still unwired, but it is now the queued task `2026-09-23T2100-profile-finish-flight.md`. Not duplicated here.
- IRIS / HFQ / Interstellar Sanctuary / air-defence paper "nowhere on the page" (19 Sep): README.md lines 50-56 now name Sanctuary, HFQ and IRIS. Air-defence paper not searched for; it belongs to the hero decision above.
- Atrium showroom not built (18 Sep): superseded, `showroom.py` exists and commit f211301 built one.
- Phone-width legibility of the hero and flow plates, hero weakest at phone width, dominance choice desktop-only (19 Sep): those plates were replaced by the shipped redesign (8a3c601). Not re-measured, so "obsolete", not "fixed".
- Non-default GitHub themes unchecked, browser coverage of theme switch one engine deep, pip is 3px, `data/` caches committed by CI, `density-6` unused: preferences, deliberate choices, or unverifiable from code; not defects.
- `generators/svg/palette()` returns Primer defaults: already ranked by `findings.py` from another repo's report; not repeated.

## Deferred

- [ ] FINDING: the repo's two type floors disagree by about 0.02px (test asserts >= 3.07% of viewBox = 10.98px on a phone, preview tool asserts >= 11px), so a plate set exactly at the test floor fails the preview tool; make them one constant | where: tests/test_build.py:497 and bin/directions.py:40 | class: actionable | severity: low
- [ ] FINDING: `design/` is 57M across 151 tracked files and is not in `.gitignore`; decide whether design output stays in the repo | where: .gitignore:1 | class: human | severity: low

## Verification

`python3 ~/.claude/scripts/findings.py` before: `no Deferred block yet: chrome-tidy icss-briefs master-plan modular-bag thomasvanpul thomasvp`. After: `no Deferred block yet: chrome-tidy icss-briefs master-plan modular-bag thomasvp` (thomasvanpul gone; its floors finding now ranks at 53.0).
