"""A figures strip — one lede number and a row of supporting ones.

This exists so a featured section can open with a measurement instead of a
paragraph. It is the same typographic language as the hero's readout row,
which is deliberate: the two places on the page that state numbers should
look like the same instrument.

It carries no data of its own. Whatever is passed in has to be traceable to
something measured, and for the one caller that currently exists those
figures come from a dated record in the vault, not from this repo.
"""
from __future__ import annotations

from . import palette

VIEW_W = 1200
VIEW_H = 132

MARGIN_X = 70.0
LEDE_NUM_Y = 62.0
LEDE_CAP_Y = 82.0
ROW_NUM_Y = 58.0
ROW_CAP_Y = 78.0
RULE_Y = 104.0

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def render(theme: str, lede_number: str, lede_caption: str,
           figures: list[tuple[str, str]], aria: str) -> str:
    fg, _ = palette(theme)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" '
        f'width="{VIEW_W}" height="{VIEW_H}" role="img" aria-label="{aria}">\n',
        # The lede is left-aligned on the same margin as the body text, so the
        # number reads as the section's opening line rather than as a banner.
        f'  <text x="{MARGIN_X:.0f}" y="{LEDE_NUM_Y:.0f}" '
        f'style="font:600 54px {MONO};letter-spacing:2px" '
        f'fill="{fg}" fill-opacity=".95">{lede_number}</text>\n',
        f'  <text x="{MARGIN_X + 3:.0f}" y="{LEDE_CAP_Y:.0f}" '
        f'style="font:400 10px {MONO};letter-spacing:2.4px" '
        f'fill="{fg}" fill-opacity=".55">{lede_caption}</text>\n',
    ]

    if figures:
        right_edge = VIEW_W - MARGIN_X
        span = right_edge - 470.0
        step = span / len(figures)
        for i, (number, caption) in enumerate(figures):
            cx = 470.0 + step * (i + 0.5)
            parts.append(
                f'  <text x="{cx:.1f}" y="{ROW_NUM_Y:.0f}" text-anchor="middle" '
                f'style="font:600 22px {MONO};letter-spacing:1.4px" '
                f'fill="{fg}" fill-opacity=".88">{number}</text>\n'
                f'  <text x="{cx:.1f}" y="{ROW_CAP_Y:.0f}" text-anchor="middle" '
                f'style="font:400 9px {MONO};letter-spacing:1.3px" '
                f'fill="{fg}" fill-opacity=".50">{caption}</text>\n'
            )

    parts.append(
        f'  <line x1="{MARGIN_X:.0f}" y1="{RULE_Y:.0f}" x2="{VIEW_W - MARGIN_X:.0f}" '
        f'y2="{RULE_Y:.0f}" stroke="{fg}" stroke-opacity=".16" stroke-width="1"/>\n'
        "</svg>\n"
    )
    return "".join(parts)
