# Backfill a Deferred block so findings.py scans this repo instead of reporting it unscanned
Written: 2026-09-21
Queue: auto
Weight: light
Priority: low
Model: claude-sonnet-5

## Why

`~/.claude/scripts/findings.py` ranks every repo's open findings from the
`## Deferred` block in its `.review/` reports. This repo has none, so it is
reported *unscanned*, not clean. Thomas, 21 Sep: one backfill task per repo,
run by this repo's own session, rather than one session writing into all of them.

## Do

1. Read this repo's `.review/report.md` and `.review/archive/*.report.md`.
2. Pull out every defect already written in prose that is still true today:
   check each against the current code before listing it. Drop anything
   fixed or no longer applicable, and say which you dropped and why.
3. Write them into this task's report as a `## Deferred` block in the format
   `~/.claude/review-convention.md` defines
   (`- [ ] FINDING: <claim> | where: <file:line> | class: <class> | severity: <sev>`).
   If there are none, write the block with the single line `none found`, so
   the repo reads as scanned.
4. Verify: `python3 ~/.claude/scripts/findings.py` no longer lists this repo
   as unscanned. Put that output line in the report.

Do not fix the findings in this task. Listing them is the whole job.
