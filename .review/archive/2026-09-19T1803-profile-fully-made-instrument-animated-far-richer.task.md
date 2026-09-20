# The profile, fully made: instrument direction, animated, far richer
Written: 2026-09-19
Queue: auto
Weight: light
Model: claude-opus-5

## Thomas's verdict on round 3 (19 Sep 18:00)

"I still feel the GitHub page is severely under-made, I do not see any
animations at all. I guess I feel the Atrium one is nicer, but still though."
He looked at the comparison PNGs, so he saw no motion anywhere. He prefers
**instrument** (the page as an Atrium readout). Your own report said you would
ship **instrument with playback's animation**. Do that, and go much further.

## Do

1. **Build instrument out fully**, as a page that looks designed and finished,
   not a sketch: every section real, every plate carrying real data, typography
   and spacing refined, the Atrium lockup, BlueBand at equal weight, Atrium
   leading. Much less prose than any earlier round.
2. **Motion is required, not optional.** At least three animated plates
   (APNG or GIF, whichever is smaller for the same quality), each carrying real
   data changing over real time (your 53-week sweep is one; find two more:
   e.g. gate history, events.tsv activity by hour, the lattice resolving on
   approach). Keep each under ~500 KB; state sizes. Still fallbacks for
   `prefers-reduced-motion`.
3. **Show it the way he will see it:** render through GitHub's own markdown
   renderer (`make page`) and open the result in Chrome so the animations play;
   also record a 15 to 20 second screen capture of the page scrolling
   (desktop and phone width), saved as MP4 beside the stills. Stills alone are
   not acceptable evidence this time.
4. Two variations of the finished instrument page so he can pick (for example,
   quieter vs denser), both animated.

## Do not

- Do not push to GitHub.

## Report

Paths to both pages and both recordings, animation file sizes, smallest phone
type size, and which you would ship.
