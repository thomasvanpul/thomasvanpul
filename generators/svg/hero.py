"""Hero banner — the contribution record plotted, with the name over it.

Every mark in this file is traceable to a number in the public GitHub
contribution calendar for `PROFILE_OWNER`. Nothing is decorative except the
planet core and its horizon arc, which are kept deliberately as an identity
mark and are the only two elements here that encode nothing.

What each element encodes
-------------------------
unit field     one mark per contribution — not per day. All `total` of them,
               in chronological order, packed left-to-right and top-to-bottom
               on a fixed pitch. Shading alternates per calendar month and a
               hairline is dropped at each month boundary, so the width of
               each tonal band is that month's volume.

               A per-day bar chart was built first and thrown away: 292 of
               the 370 days in this window have no contributions, so the
               honest plot of them was four fifths empty canvas. The counts
               are identical; only the unit is different. One mark per
               contribution is the same record at the density it deserves.
planet rings   the last six calendar months, outermost oldest. Each ring's
               drawn fraction is that month's share of the largest of the
               six, so the ring stack shows the work starting.
pip            nothing. It is the page's one moving mark and its one coloured
               one, and it is honest about encoding no count.
name           the only word in the plate, and the only one large enough to
               survive the column. 60px on a 1200 viewBox is 5.0% of the
               width, which reads at 17.9px on a 358px phone.

What left this file, and why
----------------------------
The readout row and the rotating subtitle used to be drawn here, at 26px/9px
and 15px. A README asset is a fixed-ratio image in a fluid column, so those
read at 7.8px, 2.7px and 4.5px on a phone. They are now markdown directly
under the plate: legible at every width, selectable, and visible to GitHub's
search, which never sees text inside an <img>. `readout_figures` and
`field_span` stay here so the numbers are still derived beside the field they
describe -- build.py formats them, it does not compute them.

What moves, and only this
-------------------------
One thing: the accent pip riding the outermost ring, 24 seconds to the orbit.

Stopping it is not done here, and the reason is a measurement. An
`<img>`-referenced SVG carries its own stylesheet and *is* told the reader's
colour scheme -- that is how the ground flips. It is **not** told the reader's
motion preference. The same file, the same emulated `prefers-reduced-motion:
reduce`, rendered twice in Chromium: opened as a document the rule matches,
loaded through an `<img>` it never does. A `@media (prefers-reduced-motion)`
block inside this file would be dead code that reads as a guarantee, which is
worse than no guard at all.

So the switch sits in the page, where the query works, and this module renders
both sides of it: `render(..., animate=False)` is the same figure with the pip
parked on the ring, and `build._hero_picture` hands the two to a `<picture>`
whose `<source media="(prefers-reduced-motion: reduce)">` picks the still. That
is the same mechanism the contribution snake already uses for its two themes.

The figure degrades to name + planet when no day series is available (a build
with neither a token nor a cached calendar). That path is exercised by the
mocked unit tests, which supply summary figures only.
"""
from __future__ import annotations

from math import sqrt

from . import ACCENT, field, palette, token
from ..content import HERO_ARIA

VIEW_W = 1200
VIEW_H = 268

# --- day field geometry ---------------------------------------------------
# Flush left and flush right. These were 70 and 1130, a margin inside the
# plate -- which is what a plate wants and a drawing on a page does not: with
# the panel gone there is nothing for the inset to be inset *from*, so it read
# as the hero sitting 57px to the right of every other line on the page.
FIELD_X0 = 0.0
FIELD_X1 = 1200.0
FIELD_TOP_Y = 164.0         # first row of marks
FIELD_PITCH = 6.0           # centre-to-centre spacing, both axes
FIELD_DOT_W = 3.0           # stroke width of a single mark

# --- name block -----------------------------------------------------------
NAME_X = 0.0
NAME_Y = 100.0
NAME_RULE_Y = 128.0
NAME_RULE_X1 = 630.0
NAME_PX = 60.0

# --- planet ---------------------------------------------------------------
PLANET_CX = 1000.0
PLANET_CY = 88.0
PLANET_ROT = -7.0
PLANET_CORE_R = 27.0

# The one moving mark on the page, and the one coloured one.
PIP_R = 5.0
ORBIT_SECONDS = 24.0

# (rx, ry) outermost first. Six rings, one per month, oldest outermost.
PLANET_RINGS = [
    (156, 24),
    (135, 20),
    (114, 17),
    (93, 14),
    (73, 11),
    (55, 8),
]
PLANET_MONTHS = len(PLANET_RINGS)

# Two spellings on purpose. MONO goes inside style="..." attributes, so it
# must not contain a double-quoted family name — that closes the attribute
# and emits invalid XML that `python3 -m generators.build` will happily
# write and only a rasteriser or an XML parse will reject. MONO_CSS goes
# inside the <style> block, where the quotes are fine.
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'
MONO_CSS = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace'


def _ring_path() -> str:
    """The outermost ring as a path, for the pip to travel.

    Two arcs rather than one: a single elliptical arc from a point back to
    itself is a zero-length sweep and draws nothing.
    """
    rx, ry = PLANET_RINGS[0]
    left, right = PLANET_CX - rx, PLANET_CX + rx
    return (f"M {left:g} {PLANET_CY:g} A {rx:g} {ry:g} 0 1 1 {right:g} {PLANET_CY:g} "
            f"A {rx:g} {ry:g} 0 1 1 {left:g} {PLANET_CY:g}")


def _fmt(n: int) -> str:
    return f"{n:,}"


def _x_for(index: int, n: int) -> float:
    """Left-to-right position of day `index` of `n` across the field."""
    if n <= 1:
        return FIELD_X0
    return FIELD_X0 + (FIELD_X1 - FIELD_X0) * index / (n - 1)


def _unit_field(contrib: dict, fg: str) -> str:
    """One mark per contribution, chronological, shaded by month.

    Marks are emitted as zero-length `h.01` path segments with a round
    linecap rather than as <circle> elements: at this count the circles cost
    roughly three times the bytes for a mark the reader cannot tell apart.
    Every coordinate lands on an integer because the pitch and origin are
    both integers, which keeps the d-string short.
    """
    months = contrib.get("months") or []
    total = contrib.get("total") or 0
    if not months or total <= 0:
        return ""

    cols = int((FIELD_X1 - FIELD_X0) // FIELD_PITCH) + 1

    def xy(k: int) -> tuple[int, int]:
        return (int(FIELD_X0 + (k % cols) * FIELD_PITCH),
                int(FIELD_TOP_Y + (k // cols) * FIELD_PITCH))

    # Two alternating opacities so neighbouring months separate tonally.
    bands: list[list[str]] = [[], []]
    boundaries: list[str] = []
    k = 0
    for m_index, (_label, count) in enumerate(months):
        if count <= 0:
            continue
        if k:
            bx, by = xy(k)
            boundaries.append(f"M{bx} {by - 3}v6")
        band = bands[m_index % 2]
        for _ in range(count):
            x, y = xy(k)
            band.append(f"M{x} {y}h.01")
            k += 1

    parts: list[str] = []
    for band, op in zip(bands, (".60", ".34")):
        if band:
            parts.append(
                f'  <path d="{"".join(band)}" stroke="{fg}" stroke-opacity="{op}" '
                f'stroke-width="{FIELD_DOT_W}" stroke-linecap="round" fill="none"/>\n'
            )
    if boundaries:
        parts.append(
            f'  <path d="{"".join(boundaries)}" stroke="{fg}" stroke-opacity=".9" '
            'stroke-width="1" fill="none"/>\n'
        )
    return "".join(parts)


def field_span(contrib: dict) -> str:
    """First and last month with any contribution in it, e.g. "2025-11 - 2026-09"."""
    months = [m for m in (contrib.get("months") or []) if m[1] > 0]
    if not months:
        return ""
    return f"{months[0][0]} - {months[-1][0]}" if len(months) > 1 else months[0][0]


def readout_figures(contrib: dict) -> list[tuple[str, str]]:
    """The four figures the field is a picture of. Derived here, set in markdown."""
    days = contrib.get("days") or []
    if not days:
        return []
    return [
        (_fmt(contrib["total"]), "contributions"),
        (f'{_fmt(contrib.get("active_days") or 0)} of {len(days)}', "days active"),
        (_fmt(contrib.get("peak_count") or 0), "busiest day"),
        (_fmt(contrib.get("longest_streak") or 0), "longest streak"),
    ]


def _planet(months: list[list], fg: str) -> str:
    """Rings carry the last six monthly totals; core, horizon and pip carry nothing.

    Ring i is drawn as a dashed ellipse whose drawn arc is that month's share
    of the busiest of the six. A month with no contributions leaves an almost
    undrawn ring, which is the honest picture of this account before July.

    The pip is the page's only moving mark and its only coloured one, and it
    rides the outermost ring rather than spinning in place. It travels on an
    `offset-path` describing that ring, with `offset-rotate: 0deg` so the mark
    is only ever translated.

    The obvious alternative was built first and is wrong: squash the space to
    the ring's aspect, rotate a pip inside it at radius `rx`, then unscale the
    pip so it stays round. It lands on the ellipse -- that much was measured --
    but the unscale is *inside* the rotation, so it stretches along an axis
    that turns with it, and the outer squash only compresses along the page's
    y. The pip is round at the two ends of the ring and a 32-unit red streak at
    the top and bottom of it. Measuring the position and not the shape is how
    that survived a check.

    What used to be here: a second ring pulsing outward, the core fading in and
    out, and a caret blinking beside the name. Nine animations on the page, none
    of them larger than 0.8% of a plate, which is why the page read as static.
    One thing moves now and it is 26% of the plate wide.
    """
    tail = [m[1] for m in months[-PLANET_MONTHS:]] if months else []
    while len(tail) < PLANET_MONTHS:
        tail.insert(0, 0)
    ceiling = max(tail) or 1

    parts = [f'  <g transform="rotate({PLANET_ROT} {PLANET_CX} {PLANET_CY})">\n']
    for (rx, ry), value in zip(PLANET_RINGS, tail):
        share = value / ceiling
        perim = 3.14159 * (3 * (rx + ry) - ((3 * rx + ry) * (rx + 3 * ry)) ** 0.5)
        drawn = max(perim * share, 1.5)
        gap = max(perim - drawn, 0.5)
        op = 0.22 + 0.68 * share
        parts.append(
            f'    <ellipse cx="{PLANET_CX}" cy="{PLANET_CY}" rx="{rx}" ry="{ry}" '
            f'fill="none" stroke="{fg}" stroke-opacity="{op:.2f}" stroke-width="1.3" '
            f'stroke-dasharray="{drawn:.1f} {gap:.1f}" stroke-linecap="round"/>\n'
        )
    # Identity mark: the core disc and the horizon arc across it. These encode
    # nothing and are the only two elements in this file that do not.
    r = PLANET_CORE_R * 1.5
    parts.append(
        f'    <path d="M {PLANET_CX - r:.1f} {PLANET_CY:.1f} '
        f'A {r:.1f} {r:.1f} 0 0 1 {PLANET_CX + r:.1f} {PLANET_CY:.1f}" '
        f'fill="none" stroke="{fg}" stroke-opacity=".45" stroke-width="1.1"/>\n'
        f'    <circle class="ground" cx="{PLANET_CX}" cy="{PLANET_CY}" r="{PLANET_CORE_R}"/>\n'
        f'    <circle cx="{PLANET_CX}" cy="{PLANET_CY}" r="{PLANET_CORE_R}" fill="none" '
        f'stroke="{fg}" stroke-width="1.6" stroke-opacity=".9"/>\n'
    )

    parts.append(
        f'    <circle class="pip" cx="0" cy="0" r="{PIP_R:g}"/>\n'
        '  </g>\n\n'
    )
    return "".join(parts)


def render(name: str, contributions: dict | None = None,
           aria: str = HERO_ARIA, animate: bool = True) -> str:
    fg, _ = palette()
    contrib = contributions or {}
    days = contrib.get("days") or []
    peak = contrib.get("peak_count") or 0

    motion = (f" animation: orbit {ORBIT_SECONDS:g}s linear infinite;"
              if animate else "")

    label = aria
    if days:
        label = (
            f"{aria}. {_fmt(contrib['total'])} contributions across "
            f"{contrib.get('active_days', 0)} active days in the "
            f"{len(days)} days to {days[-1]['date']}; busiest day {peak}."
        )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" '
        f'width="{VIEW_W}" height="{VIEW_H}" role="img" aria-label="{label}">\n'
        '  <style>\n'
        f'    .name {{ font: 600 {NAME_PX:g}px {MONO_CSS}; letter-spacing: 8px; fill: {fg}; }}\n'
        f'    .pip {{ fill: {token(ACCENT)}; offset-path: path("{_ring_path()}"); '
        f'offset-rotate: 0deg;{motion} }}\n'
        + ('    @keyframes orbit { from { offset-distance: 0%; } '
           'to { offset-distance: 100%; } }\n' if animate else '')
        + '  </style>\n\n'
    ]

    parts.append(field())
    parts.append(_planet(contrib.get("months") or [], fg))

    parts.append(
        f'  <line x1="{NAME_X:.0f}" y1="{NAME_RULE_Y:.0f}" x2="{NAME_RULE_X1:.0f}" '
        f'y2="{NAME_RULE_Y:.0f}" stroke="{fg}" stroke-opacity=".22" stroke-width="1"/>\n'
        f'  <text class="name" x="{NAME_X:.0f}" y="{NAME_Y:.0f}">{name}</text>\n'
    )

    if days:
        parts.append(_unit_field(contrib, fg))

    parts.append('</svg>\n')
    return "".join(parts)
