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
readout row    four figures: total, active days out of the window, peak day,
               longest streak. These replaced the separate stats.svg panel,
               which carried the same numbers one screen further down.
planet rings   the last six calendar months, outermost oldest. Each ring's
               drawn fraction is that month's share of the largest of the
               six, so the ring stack shows the work starting.
name, subtitle unchanged; the subtitle rotation is still driven by
               content.HERO_SUBTITLES.

The whole figure degrades to name + subtitle + planet when no day series is
available (a build with neither a token nor a cached calendar). That path is
exercised by the mocked unit tests, which supply summary figures only.
"""
from __future__ import annotations

from math import sqrt

from . import palette
from ..content import HERO_ARIA

VIEW_W = 1200
VIEW_H = 340

# --- day field geometry ---------------------------------------------------
FIELD_X0 = 70.0
FIELD_X1 = 1130.0
FIELD_TOP_Y = 236.0         # first row of marks
FIELD_PITCH = 6.0           # centre-to-centre spacing, both axes
FIELD_DOT_W = 3.0           # stroke width of a single mark
FIELD_CAPTION_Y = 337.0

# --- readout row ----------------------------------------------------------
READOUT_NUM_Y = 190.0
READOUT_CAP_Y = 207.0

# --- name block -----------------------------------------------------------
NAME_X = 70.0
NAME_Y = 104.0
SUB_Y = 136.0
NAME_RULE_Y = 156.0
NAME_RULE_X1 = 470.0
CURSOR_X = 58.0
CURSOR_Y = 124.0

# --- planet ---------------------------------------------------------------
PLANET_CX = 950.0
PLANET_CY = 88.0
PLANET_ROT = -7.0
PLANET_CORE_R = 27.0
PLANET_PULSE_R = 33.0

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

# Subtitle rotation.
SUBTITLE_TOTAL_DUR = 13.60
SUBTITLE_FADE = 0.0331  # fraction of total per fade in/out

# Two spellings on purpose. MONO goes inside style="..." attributes, so it
# must not contain a double-quoted family name — that closes the attribute
# and emits invalid XML that `python3 -m generators.build` will happily
# write and only a rasteriser or an XML parse will reject. MONO_CSS goes
# inside the <style> block, where the quotes are fine.
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'
MONO_CSS = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace'


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
    for band, op in zip(bands, (".78", ".46")):
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


def _field_caption(contrib: dict, fg: str) -> str:
    months = [m for m in (contrib.get("months") or []) if m[1] > 0]
    if not months:
        return ""
    span = f"{months[0][0]} – {months[-1][0]}" if len(months) > 1 else months[0][0]
    cap = (f'style="font:400 9px {MONO};letter-spacing:1.8px" '
           f'fill="{fg}" fill-opacity=".45"')
    return (
        f'  <text x="{FIELD_X0:.0f}" y="{FIELD_CAPTION_Y:.0f}" {cap}>'
        f'ONE MARK · ONE CONTRIBUTION · SHADED BY MONTH</text>\n'
        f'  <text x="{FIELD_X1:.0f}" y="{FIELD_CAPTION_Y:.0f}" text-anchor="end" {cap}>'
        f'{span}</text>\n'
    )


def _readout(contrib: dict, fg: str) -> str:
    """Four figures spanning the width, bridging the name and the planet.

    This is the old stats.svg, moved. Keeping it as a separate image meant a
    second request for three numbers that belong beside the field they
    describe.
    """
    n_days = len(contrib.get("days") or [])
    cols = [
        (_fmt(contrib["total"]), "CONTRIBUTIONS · 12 MONTHS"),
        (f'{_fmt(contrib.get("active_days") or 0)} / {n_days}', "DAYS WITH COMMITS"),
        (_fmt(contrib.get("peak_count") or 0), "BUSIEST DAY"),
        (_fmt(contrib.get("longest_streak") or 0), "LONGEST STREAK"),
    ]
    inner = FIELD_X1 - FIELD_X0
    step = inner / len(cols)
    parts = []
    for i, (number, caption) in enumerate(cols):
        cx = FIELD_X0 + step * (i + 0.5)
        parts.append(
            f'  <text x="{cx:.1f}" y="{READOUT_NUM_Y:.0f}" text-anchor="middle" '
            f'style="font:600 26px {MONO};letter-spacing:1.5px" '
            f'fill="{fg}" fill-opacity=".92">{number}</text>\n'
            f'  <text x="{cx:.1f}" y="{READOUT_CAP_Y:.0f}" text-anchor="middle" '
            f'style="font:400 9px {MONO};letter-spacing:2px" '
            f'fill="{fg}" fill-opacity=".50">{caption}</text>\n'
        )
    return "".join(parts)


def _planet(months: list[list], fg: str, bg: str) -> str:
    """Rings carry the last six monthly totals; core and horizon carry nothing.

    Ring i is drawn as a dashed ellipse whose drawn arc is that month's share
    of the busiest of the six. A month with no contributions leaves an almost
    undrawn ring, which is the honest picture of this account before July.
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
        f'    <circle cx="{PLANET_CX}" cy="{PLANET_CY}" r="{PLANET_CORE_R}" fill="{bg}"/>\n'
        f'    <circle cx="{PLANET_CX}" cy="{PLANET_CY}" r="{PLANET_CORE_R}" fill="none" '
        f'stroke="{fg}" stroke-width="1.6" stroke-opacity=".9">\n'
        '      <animate attributeName="stroke-opacity" values=".9;.45;.9" dur="5.5s" repeatCount="indefinite"/>\n'
        '    </circle>\n'
        f'    <circle cx="{PLANET_CX}" cy="{PLANET_CY}" r="{PLANET_PULSE_R}" fill="none" '
        f'stroke="{fg}" stroke-width="0.7" stroke-opacity=".26">\n'
        f'      <animate attributeName="r" values="{PLANET_PULSE_R};{PLANET_PULSE_R + 7};{PLANET_PULSE_R}" dur="5.5s" repeatCount="indefinite"/>\n'
        '      <animate attributeName="stroke-opacity" values=".26;.05;.26" dur="5.5s" repeatCount="indefinite"/>\n'
        '    </circle>\n'
        '  </g>\n\n'
    )
    return "".join(parts)


def _subtitle_animation(i: int, n: int) -> tuple[str, str, str]:
    slot = 1.0 / n
    slot_start = i * slot
    slot_end = (i + 1) * slot
    if i == 0:
        # First subtitle fades out at start and re-fades-in at end for a clean loop.
        values = "1;1;0;0;1"
        key_times = f"0.0000;{slot_start + slot - SUBTITLE_FADE:.4f};{slot_end:.4f};{1 - SUBTITLE_FADE:.4f};1.0000"
        return values, key_times, "1"
    values = "0;0;1;1;0;0"
    key_times = (
        f"0.0000;{slot_start:.4f};{slot_start + SUBTITLE_FADE:.4f};"
        f"{slot_end - SUBTITLE_FADE:.4f};{slot_end:.4f};1.0000"
    )
    return values, key_times, "0"


def render(theme: str, name: str, subtitle_lines: list[str],
           contributions: dict | None = None, aria: str = HERO_ARIA) -> str:
    fg, bg = palette(theme)
    contrib = contributions or {}
    days = contrib.get("days") or []
    peak = contrib.get("peak_count") or 0

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
        f'    .name {{ font: 600 44px {MONO_CSS}; letter-spacing: 6px; fill: {fg}; }}\n'
        f'    .sub  {{ font: 400 15px {MONO_CSS}; letter-spacing: 3.2px; fill: {fg}; fill-opacity: .70; }}\n'
        f'    .cur  {{ fill: {fg}; }}\n'
        '  </style>\n\n'
    ]

    parts.append(_planet(contrib.get("months") or [], fg, bg))

    parts.append(
        f'  <line x1="{NAME_X:.0f}" y1="{NAME_RULE_Y:.0f}" x2="{NAME_RULE_X1:.0f}" '
        f'y2="{NAME_RULE_Y:.0f}" stroke="{fg}" stroke-opacity=".22" stroke-width="1"/>\n'
        f'  <text class="name" x="{NAME_X:.0f}" y="{NAME_Y:.0f}">{name}</text>\n'
    )
    n = len(subtitle_lines)
    for i, line in enumerate(subtitle_lines):
        values, key_times, initial_op = _subtitle_animation(i, n)
        parts.append(
            f'  <text class="sub" x="{NAME_X + 2:.0f}" y="{SUB_Y:.0f}" opacity="{initial_op}">{line}'
            f'<animate attributeName="opacity" values="{values}" keyTimes="{key_times}" '
            f'dur="{SUBTITLE_TOTAL_DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/></text>\n'
        )
    parts.append(
        f'  <rect class="cur" x="{CURSOR_X:.0f}" y="{CURSOR_Y:.0f}" width="7" height="16" opacity=".8">\n'
        '    <animate attributeName="opacity" values=".8;0;.8" dur="1.1s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5;1"/>\n'
        '  </rect>\n\n'
    )

    if days:
        parts.append(_readout(contrib, fg))
        parts.append(_unit_field(contrib, fg))
        parts.append(_field_caption(contrib, fg))

    parts.append('</svg>\n')
    return "".join(parts)
