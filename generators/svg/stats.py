"""Contributions panel — four large mono figures under captions.

Visual language matches hero/flow: hairline scale on top, monospace type,
transparent background, dark/light foreground swap. Animation is confined to
a single blinking cursor next to the CURRENT STREAK number — the one figure
whose value actually changes day-to-day. Nothing else moves.
"""
from __future__ import annotations

from . import palette

VIEW_W = 1200
VIEW_H = 150

MARGIN_X = 70
SCALE_Y = 20                # hairline rule across the top
NUMBER_Y = 82               # baseline for the large figures
CAPTION_Y = 108             # baseline for the small caption
SUB_Y = 128                 # baseline for the sub-line (e.g. "N private")


def _tick(x: float, fg: str) -> str:
    return (
        f'<line x1="{x:.1f}" y1="{SCALE_Y - 3:.1f}" x2="{x:.1f}" y2="{SCALE_Y + 3:.1f}" '
        f'stroke="{fg}" stroke-opacity=".28" stroke-width="1"/>'
    )


def _column(cx: float, number: str, caption: str, sub: str | None,
            fg: str, cursor: bool) -> str:
    parts = [
        f'<text x="{cx:.1f}" y="{NUMBER_Y}" text-anchor="middle" '
        'style="font:600 40px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:2px" '
        f'fill="{fg}" fill-opacity=".92">{number}</text>',
        f'<text x="{cx:.1f}" y="{CAPTION_Y}" text-anchor="middle" '
        'style="font:400 10.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:2.2px" '
        f'fill="{fg}" fill-opacity=".55">{caption}</text>',
    ]
    if sub:
        parts.append(
            f'<text x="{cx:.1f}" y="{SUB_Y}" text-anchor="middle" '
            'style="font:400 9.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:1.6px" '
            f'fill="{fg}" fill-opacity=".38">{sub}</text>'
        )
    if cursor:
        # Small blinking block just to the right of the number, sized like the
        # hero cursor. Placement is offset by roughly half a mono digit width.
        cx_right = cx + max(1, len(number)) * 12 + 4
        parts.append(
            f'<rect x="{cx_right:.1f}" y="{NUMBER_Y - 30:.1f}" width="6" height="26" '
            f'fill="{fg}" opacity=".65">'
            '<animate attributeName="opacity" values=".65;0;.65" dur="1.1s" '
            'repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5;1"/>'
            '</rect>'
        )
    return "".join(parts)


def _fmt(n: int) -> str:
    return f"{n:,}"


def render(theme: str, stats: dict) -> str:
    fg, _ = palette(theme)

    restricted = stats.get("restricted") or 0

    # Column spec: (number, caption, sub, cursor). "repos_committed_to" is
    # deliberately omitted — under the CI token's read:user scope it counts
    # only public repos, which would understate the true figure.
    columns: list[tuple[str, str, str | None, bool]] = [
        (_fmt(stats["total"]), "CONTRIBUTIONS", None, False),
    ]
    if restricted:
        columns.append((_fmt(restricted), "PRIVATE", "CONTRIBUTIONS", False))
    columns.append((_fmt(stats["current_streak"]), "CURRENT STREAK", "DAYS", True))
    columns.append((_fmt(stats["longest_streak"]), "LONGEST STREAK", "DAYS", False))

    n = len(columns)
    inner = VIEW_W - 2 * MARGIN_X
    step = inner / n
    centres = [MARGIN_X + step * (i + 0.5) for i in range(n)]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" '
        f'width="{VIEW_W}" height="{VIEW_H}" role="img" '
        'aria-label="Contributions in the last 12 months">\n',
        # Hairline scale across the top with ticks at each column centre.
        f'  <line x1="{MARGIN_X}" y1="{SCALE_Y}" x2="{VIEW_W - MARGIN_X}" y2="{SCALE_Y}" '
        f'stroke="{fg}" stroke-opacity=".14" stroke-width="1"/>\n',
    ]
    for cx in centres:
        parts.append("  " + _tick(cx, fg) + "\n")

    for cx, (number, caption, sub, cursor) in zip(centres, columns):
        parts.append("  " + _column(cx, number, caption, sub, fg, cursor) + "\n")

    parts.append("</svg>\n")
    return "".join(parts)
