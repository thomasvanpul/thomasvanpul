# The profile, way better — 19 September 2026

Three directions that differ in kind, and the board they were drawn from.

* `reference-board/` — 21 references, one screenshot and one line each.
* `directions/` — the three, built from real content and photographed through
  GitHub's own Markdown renderer at 1012px and 390px, dark and light.
* `comparisons/` — each direction beside the three references it borrows from.
* `rejected/` — the four directions Thomas turned down on 19 September, with
  his verdict.

## What changed about the question

The four rejected directions differ in **degree**: they vary only in how much
of the page is lattice field, from 99 of the grid's 107 rows down to 36. That
is one axis, and "way way better" is not a point on it. These three vary in
**kind** — what the page is made of at all.

## The three

| | What it is | Desktop | Phone | Words |
| --- | --- | --- | --- | --- |
| **index** | Nearly imageless. Type, rhythm, and one hairline rule per section — each rule a single row of the real lattice grid. | 1,172px | 1,534px | 291 |
| **playback** | One animated image carries the page: the frame as a dot screen, with the year's 53 real weeks swept through it a week at a time. | 941px | 1,213px | 278 |
| **instrument** | The page as an Atrium readout. Two plates, a lockup, and three real counts along the foot of each. | 1,349px | 1,293px | 219 |
| *live page, for scale* | | *2,611px* | *2,554px* | *494* |

All three are less than half the height of the page that is live, and all
three cut its word count by between 41% and 56%.

## Type on a phone

GitHub's profile column is 390px, 358px inside its padding. A 1200-unit plate
therefore renders at 0.298×, and `tests/test_build.py` holds every drawn text
element to 3.07% of its own plate width — 11px apparent.

| | Text drawn in images | Smallest, as it reads on a phone |
| --- | --- | --- |
| index | none — every word is Markdown | n/a |
| playback | none — the animation carries no words | n/a |
| instrument | 6 sizes across 2 plates | **11.2px**, none below the floor |

`index` and `playback` cannot fail this test, because they put nothing a
reader has to read inside an image. `instrument` can, and the margin it has is
two tenths of a pixel.

## Which I would pick

**`instrument`.** It is the only one of the three that looks like Atrium at a
glance *and* survives a phone, it cuts the most words, and it leads with the
number the whole page is really about. `index` is the safest and the least
memorable — it would look good on any engineer's profile, which is the problem.
`playback` is the one that makes someone stop scrolling, and it is also the one
whose single image has to carry everything.

The version I would actually ship is `instrument` with `playback`'s animation
used once, as the Atrium section's image, in place of the static showroom
plate. That is not one of the three, which is why it is written here rather
than built.

## Built with

```
python3 bin/reference_board.py      # the board: shoot every source, write its index
python3 bin/bold.py                 # the three directions, built and photographed
python3 bin/compare_board.py        # each direction beside what it borrows from
```

Nothing here is shipped. `generators/build.py` is untouched, `README.md` and
`assets/` rebuild byte-identically, and nothing has been pushed.
