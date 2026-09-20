# The profile in orhun's shape: one beautiful animated Atrium piece and a very short text block
Written: 2026-09-19
Queue: auto
Weight: light
Model: claude-opus-5

## Thomas's direction (19 Sep 19:05)

After five rounds (all in `design/rejected/` or `design/directions/`), he picked
from the reference board: **gh-orhun**, "paired light/dark animated terminal
GIFs anchoring a very short text block". His words: "we can also animate a
properly looking Atrium design and then show certain things based on hover like
projects and stuff." On round 4 (instrument quiet/dense): "not the best of
designs, it doesn't feel fluid and doesn't feel like it works together."

## The constraint to be honest about

A GitHub README cannot do hover: images are served as images, no script, no CSS
interaction. So on GitHub, "things on hover" becomes either (a) the animation
itself cycling through projects (each project gets its moment inside one
continuous loop, labelled in the frame), or (b) each project as its own small
animated tile that links to its repo. Build (a) as the lead, (b) only if it
reads as one piece. Note in the report that true hover belongs on thomasvp.com,
where it can be built as a follow-up.

## Do

1. **One hero animation**, the only large thing on the page: a properly
   designed, fluid Atrium piece in the look Thomas loves (read
   `Atlas/Projects/Atrium/Thomas-Answers-Frames.md` for the frames he loved and
   the ones he marked wrong; `Design-Language.md`; the tokens). Real data. It
   cycles through Atrium, BlueBand, Numeris and the other projects inside one
   continuous motion, so the page shows projects without hover. Smooth: judge by
   eye at full frame rate, no jumps between loops, no stutter. Light and dark
   pair as orhun does. Size budget ~1.5 MB each, state actual.
2. **A very short text block** under it: name, one line, links. Nothing else.
3. Two variants of the hero (e.g. terminal-like readout vs pure lattice flight),
   both finished.
4. Evidence: `make page` rendered through GitHub's markdown, opened in Chrome,
   and a 20 s MP4 of each variant at desktop and phone width. Check against
   `Atlas/Style-AI-Slop-Tells.md` if it exists.

## Do not

- Do not push.

## Report

The two recordings, sizes, and your pick.
