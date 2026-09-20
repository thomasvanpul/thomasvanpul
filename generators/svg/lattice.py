"""One field for the whole page, sliced into bands, with the measurement over it.

The idea, and why it is the only one a README can carry
-------------------------------------------------------
Thomas: *"use the Atrium over the entire thing, making it seem like the
interface."* A GitHub README renders Markdown, sanitised HTML and images. An
SVG served through an `<img>` gets no script and no pointer events, so an
interface cannot be built. What can be built is a page that is **one picture
with text in the gaps**, and that is what this module does.

`showroom/atrium-lattice.png` is a real 10x frame of the Atrium lattice --
218,016 events from 31 repositories. It is reduced once to a single tall
luminance grid, and every band on the page is a contiguous slice of that one
grid, drawn at one pitch and one phase. The columns therefore line up down the
whole page, every band paints GitHub's own canvas before it draws, and the
Markdown between two bands sits on the same ground the bands are painted on.
Scrolling the page is panning down one frame.

The measurement laid over the scene
-----------------------------------
`Atlas/Projects/Atrium/Design-Language.md`, finding 1: *"There is no lattice.
The lattice is a measurement laid over a scene that already has depth."* So the
band is the scene, and each project's own record is drawn **over** it as
structure: 53 week cells on one baseline, lit by that project's real commits
from `data/field.json`, with one tracked point circling its busiest week and a
leader line running out of the field into the heading below.

Three resolution bands, from the same note, and this module keeps the ratio:
texture is the thousands of lattice marks, structure is the 53 week cells, and
focus is one circle and one leader per region. Frame 3 of the reference has
about eight circles against tens of thousands of marks, and that ratio is why
the eye knows where to go.

What this module refuses to draw
--------------------------------
**Micro-labels.** Primitive 8 in that note is a scatter of tiny unreadable
text, and this repo has a floor that forbids it: every text element must be at
least 3.07% of its own viewBox width, because a 1200-unit plate renders at
0.30x in a 358px phone column and anything below that floor is not small, it
is absent. `tests/test_build.py` enforces it. In a 1200-wide band the floor is
36.8px, which is a headline, not texture. So the micro-labels are Markdown --
where they are legible at every width, selectable, and visible to GitHub's
search, which never sees text inside an `<img>` -- and the only type this
module draws is a region's one dominant number, well above the floor.

**Null cells as X marks.** The note's honesty valve is an X-crossed cell. At
this page's scale a week cell is 22.6 units, which is 6.7px in a phone column,
and an X inside 6.7px is a smudge. A null week is drawn as a dim 3-unit tick
instead: same statement, legible at the size it is actually rendered at.
"""
from __future__ import annotations

from . import ACCENT, field, palette, token
from .halftone import DOT_WIDTH, INK_FLOOR

VIEW_W = 1200

# The grid the whole page is cut from. 132 columns is the width the Atrium
# showroom has been reduced at since it shipped; keeping it means the marks are
# the size that was already judged, not a new scale nobody has looked at.
FIELD_COLS = 132
PITCH = VIEW_W / (FIELD_COLS - 1)

# The crop of showroom/atrium-lattice.png the page is cut from, measured
# rather than chosen. Searched over left/top/bottom for the best combination
# of high mean darkness and low spread across eighths, restricted to aspects
# that give a page-length column of bands: this one is mean 3.78 on the 0-9
# scale with rows running 2.1 at the top to 5.3 near the bottom and columns
# 1.3 to 5.2 left to right. The frame is genuinely denser at its lower right,
# so a band near the top of the page is a quieter region of the same field --
# which is what the masthead wants behind a name, and what the tail of the
# page wants as it ends.
FIELD_CROP = (0.60, 0.45, 1.00, 0.95)

# --- the measurement row --------------------------------------------------
# The floor this row is held to, and why it is not the type floor.
#
# `tests/test_build.py` holds every text element to 3.07% of its plate, which
# is 11px in a 358px phone column. Line work has the same problem and no test:
# the first pass drew this row at 53 weekly columns and measured out at 0.95px
# null ticks, a 0.45px tracked-circle stroke and a 0.36px leader -- all of it
# below one device-independent pixel, so on a phone the row was a grey smear
# with no cells, no circle and no leader in it. That is the defect the page
# was rejected for three times, in strokes instead of type.
#
# The distinction that fixes it: **texture may go sub-pixel, structure and
# focus may not.** A lattice mark's job is tone, and tone survives being
# smaller than a pixel because it averages with its neighbours. A week cell's
# job is to be one countable mark, a circle's is to be found, and a leader's
# is to be followed; none of those averages into anything. So everything in
# this row is at least 3.36 units -- one pixel at 0.298x -- and the resolution
# was spent to buy it: 13 four-week periods, not 53 weeks. A phone cannot
# resolve 53 columns of this page at any stroke width, so drawing 53 is
# drawing a number the reader cannot count.
PERIODS = 13
PERIOD_WEEKS = 4
# The row is inset by the tracked point's outer ring, because the busiest
# period on this page is the most recent one for every region -- so the circle
# always lands on the last cell, and a row that runs edge to edge has its one
# focal element sliced in half by the band's own right edge. Measured on the
# first stills: cx 1153, ring 62, viewBox 1200.
ROW_INSET = 70.0
PERIOD_PITCH = (VIEW_W - 2 * ROW_INSET) / PERIODS
NULL_SIDE = 11.0
LIT_MIN, LIT_MAX = 20.0, 62.0
BASELINE_UP = 44.0          # the row's distance from the band's bottom edge
BASELINE_W = 3.4
TRACK_R = 44.0
TRACK_RING_R = 62.0
TRACK_W = 4.0
LEADER_W = 3.6
LEADER_X = 40.0

# A band shorter than this carries marks only. There is no room under a
# 90-unit band for a baseline, a tracked point and the leader that leaves it.
MEASURE_MIN_H = 108.0

# And a band shorter than this cannot carry the readout either. The first
# stills were cut at 120 units and the caption under "13" was sliced through
# the middle by the band's own bottom edge -- the number was legible and the
# unit it was counting was not, which is the one failure mode this page has
# been rejected for three times. 230 rather than 180 because a band that
# carries the readout also carries the measurement row under it, and the
# tracked point's outer ring reaches 62 units above a baseline that sits 44
# above the band's floor: anything shorter and the ring runs into the panel.
LEDE_MIN_H = 230.0

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# The one dominant readout a region is allowed, as a fraction of the band
# width. 0.060 is 72px on a 1200 band, which reads at 21.5px in a 358px phone
# column -- the floor is 3.07% and this is nearly double it.
LEDE_FRAC = 0.060
LEDE_CAP_FRAC = 0.0320


def band(grid: dict, row0: int, rows: int) -> dict:
    """A contiguous run of rows out of the page's one grid.

    Slicing rather than re-cropping is the whole mechanism: two bands cut from
    the same grid at the same pitch have the same columns in the same places,
    so the field appears to continue behind the text between them.
    """
    cols, total = grid["cols"], grid["rows"]
    if row0 < 0 or rows < 1 or row0 + rows > total:
        raise ValueError(f"rows {row0}..{row0 + rows} outside a {total}-row grid")
    start, end = row0 * cols, (row0 + rows) * cols
    return {"cols": cols, "rows": rows, "cells": grid["cells"][start:end]}


def _marks(slice_: dict, fg: str) -> tuple[list[str], float]:
    """The scene: the lattice frame itself, one path per darkness bucket."""
    cols, rows, cells = slice_["cols"], slice_["rows"], slice_["cells"]
    view_h = (rows - 1) * PITCH if rows > 1 else PITCH
    buckets: dict[int, list[str]] = {}
    for idx, ch in enumerate(cells):
        value = ord(ch) - 48
        if value < INK_FLOOR:
            continue
        x = round((idx % cols) * PITCH)
        y = round((idx // cols) * PITCH)
        buckets.setdefault(value, []).append(f"M{x} {y}h.01")

    parts = []
    for value in sorted(buckets):
        opacity = min(0.40 + 0.06 * (value - INK_FLOOR), 0.95)
        parts.append(
            f'  <path d="{"".join(buckets[value])}" stroke="{fg}" '
            f'stroke-opacity="{opacity:.2f}" stroke-width="{DOT_WIDTH[value]:.2f}" '
            'stroke-linecap="round" fill="none"/>\n'
        )
    return parts, view_h


def _periods(weeks: list[int]) -> list[int]:
    """53 weekly counts folded to 13 four-week periods, remainder on the last."""
    out = [sum(weeks[i:i + PERIOD_WEEKS])
           for i in range(0, PERIODS * PERIOD_WEEKS, PERIOD_WEEKS)]
    out[-1] += sum(weeks[PERIODS * PERIOD_WEEKS:])
    return out


def _measure(weeks: list[int], view_h: float, fg: str) -> list[str]:
    """The structure: 13 real periods, one tracked point, one leader.

    A lit cell's side goes with the square root of its count against the
    region's own busiest period, so area is roughly proportional to volume
    rather than side being proportional to it -- the same reason a bubble
    chart takes a square root. Periods with nothing in them are ticks, not
    absences: a run of ticks is the region saying the work was not happening
    yet, which is true of every project on this page and is most of the
    record's shape. The design note's honesty valve is an X-crossed cell; an
    X inside 3.3px is a smudge, so at this page's scale it is a square tick.
    """
    counts = _periods(weeks)
    peak = max(counts) or 1
    peak_i = counts.index(peak)
    y = view_h - BASELINE_UP

    lit, null = [], []
    for i, count in enumerate(counts):
        cx = ROW_INSET + (i + 0.5) * PERIOD_PITCH
        if count <= 0:
            null.append(f"M{cx - NULL_SIDE / 2:.1f} {y - NULL_SIDE / 2:.1f}"
                        f"h{NULL_SIDE:.1f}v{NULL_SIDE:.1f}h-{NULL_SIDE:.1f}z")
            continue
        side = LIT_MIN + (LIT_MAX - LIT_MIN) * (count / peak) ** 0.5
        lit.append(f"M{cx - side / 2:.1f} {y - side / 2:.1f}"
                   f"h{side:.1f}v{side:.1f}h-{side:.1f}z")

    parts = [
        f'  <line x1="0" y1="{y:.1f}" x2="{VIEW_W}" y2="{y:.1f}" stroke="{fg}" '
        f'stroke-opacity=".22" stroke-width="{BASELINE_W}"/>\n',
        f'  <path d="{"".join(null)}" fill="{fg}" fill-opacity=".26"/>\n',
        f'  <path d="{"".join(lit)}" class="cell" fill="{fg}" fill-opacity=".90"/>\n',
    ]

    # Focus: one circle, one concentric ring, one leader out of the field.
    px = ROW_INSET + (peak_i + 0.5) * PERIOD_PITCH
    parts.append(
        f'  <circle cx="{px:.1f}" cy="{y:.1f}" r="{TRACK_R}" fill="none" '
        f'stroke="{fg}" stroke-opacity=".80" stroke-width="{TRACK_W}"/>\n'
        f'  <circle cx="{px:.1f}" cy="{y:.1f}" r="{TRACK_RING_R}" fill="none" '
        f'stroke="{fg}" stroke-opacity=".32" stroke-width="{TRACK_W * 0.6:.1f}"/>\n'
        f'  <path d="M{px - TRACK_RING_R:.1f} {y:.1f} H{LEADER_X:.0f} '
        f'V{view_h:.1f}" fill="none" stroke="{fg}" stroke-opacity=".50" '
        f'stroke-width="{LEADER_W}"/>\n'
    )
    return parts


def _lede(number: str, caption: str, view_h: float, fg: str) -> list[str]:
    """A region's one dominant readout, docked rather than floated.

    Primitive 9 in the design note is a single readout the rest of the frame
    responds to, and primitive 5 is how detail appears without a window: a
    panel that docks and points back at its subject, never one that floats
    over the data. The first stills floated it, and the measurement is the
    argument for this rewrite -- "18,470" survived at 72px because it is
    near-white and enormous, and "LINES OF SWIFT, 75 FILES" at 38.4px did
    not, because the field's densest marks punch straight through 38px
    letterforms at any opacity that still reads as a caption.

    So the panel paints the page's own ground first. That is the same
    occlusion the planet's core already uses in the masthead, and the same
    rule the note states: the field stays whole, and nothing is ever hidden
    by the thing describing it -- the panel is docked to the band's own edge,
    not dropped in the middle of the frame.
    """
    num_px = VIEW_W * LEDE_FRAC
    cap_px = VIEW_W * LEDE_CAP_FRAC
    pad = 14.0
    num_y = pad + num_px * 0.80
    cap_y = num_y + cap_px * 1.45
    panel_h = cap_y + pad * 1.25
    # 0.72 of the cap height per character, not 0.6: the advance of this
    # monospace at this size plus the 3.4 units of letter-spacing the caption
    # is set with. At 0.63 the caption overflowed its own panel by 40 units
    # and the panel's left edge was drawn through the first letter.
    panel_w = max(len(caption), len(number) + 2) * cap_px * 0.72 + pad * 2
    panel_x = VIEW_W - panel_w
    return [
        f'  <rect class="ground" x="{panel_x:.1f}" y="0" width="{panel_w:.1f}" '
        f'height="{panel_h:.1f}"/>\n',
        f'  <path d="M{panel_x:.1f} 0 V{panel_h:.1f} H{VIEW_W}" fill="none" '
        f'stroke="{fg}" stroke-opacity=".34" stroke-width="1.2"/>\n',
        f'  <text x="{VIEW_W - pad:.1f}" y="{num_y:.1f}" text-anchor="end" '
        f'style="font:600 {num_px:.1f}px {MONO};letter-spacing:4.8px" '
        f'fill="{fg}" fill-opacity=".97">{number}</text>\n',
        f'  <text x="{VIEW_W - pad:.1f}" y="{cap_y:.1f}" text-anchor="end" '
        f'style="font:400 {cap_px:.1f}px {MONO};letter-spacing:3.4px" '
        f'fill="{fg}" fill-opacity=".62">{caption}</text>\n',
    ]


def render(slice_: dict, aria: str, weeks: list[int] | None = None,
           lede: tuple[str, str] | None = None, pad_bottom: float = 0.0) -> str:
    """One band of the page's field, with whatever is laid over it.

    `slice_` is the scene, `weeks` the structure, `lede` the focus. A band with
    none of the last two is pure texture, which is what the quiet regions of
    the page get -- and a quiet region is drawn quiet rather than filled, for
    the reason the design note gives: a mark invented to fill space is
    decoration with extra steps.
    """
    fg, _ = palette()
    parts, view_h = _marks(slice_, fg)
    view_h += pad_bottom
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {view_h:.0f}" '
        f'width="{VIEW_W}" height="{view_h:.0f}" role="img" aria-label="{aria}">\n',
        field(),
    ]
    body.extend(parts)
    if lede and view_h >= LEDE_MIN_H:
        body.extend(_lede(lede[0], lede[1], view_h, fg))
    if weeks and view_h >= MEASURE_MIN_H:
        body.extend(_measure(weeks, view_h, fg))
    body.append("</svg>\n")
    return "".join(body)


def masthead(slice_: dict, name: str, months: list[list], aria: str,
             animate: bool = True) -> str:
    """The first band, with the name and the planet standing in the field.

    The name and the planet are the hero this page already had; what changed is
    the ground under them. They used to sit on an empty plate, which is why the
    lattice below read as a picture someone had pasted into a README. Here they
    are the near edge of the same field every later band is cut from.
    """
    from .hero import (NAME_PX, ORBIT_SECONDS, PIP_R, PLANET_RINGS, _planet,
                       _ring_path, MONO_CSS)

    fg, _ = palette()
    parts, view_h = _marks(slice_, fg)
    # The name sits low in the band so the field reads above and behind it.
    name_y = view_h - 46.0
    rule_y = view_h - 18.0
    planet_dy = name_y - 100.0 - 88.0 + 100.0  # keep the planet clear of the name
    motion = (f" animation: orbit {ORBIT_SECONDS:g}s linear infinite;"
              if animate else "")

    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {view_h:.0f}" '
        f'width="{VIEW_W}" height="{view_h:.0f}" role="img" aria-label="{aria}">\n',
        '  <style>\n',
        f'    .name {{ font: 600 {NAME_PX:g}px {MONO_CSS}; letter-spacing: 8px; fill: {fg}; }}\n',
        f'    .pip {{ fill: {token(ACCENT)}; offset-path: path("{_ring_path()}"); '
        f'offset-rotate: 0deg;{motion} }}\n',
        ('    @keyframes orbit { from { offset-distance: 0%; } '
         'to { offset-distance: 100%; } }\n' if animate else ''),
        '  </style>\n',
        field(),
    ]
    body.extend(parts)
    # The planet's own core paints the ground, so it occludes the field behind
    # it rather than sitting transparently on top of it. Detail docks, it does
    # not float -- the same rule the design note states for stat panels.
    body.append(f'  <g transform="translate(0 {planet_dy:.1f})">\n')
    body.append(_planet(months, fg))
    body.append('  </g>\n')
    body.append(
        f'  <line x1="0" y1="{rule_y:.1f}" x2="630" y2="{rule_y:.1f}" '
        f'stroke="{fg}" stroke-opacity=".28" stroke-width="1"/>\n'
        f'  <text class="name" x="0" y="{name_y:.1f}">{name}</text>\n'
    )
    body.append("</svg>\n")
    return "".join(body)
