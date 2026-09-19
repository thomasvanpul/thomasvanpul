"""One measured number, set large enough to survive the column it lands in.

This used to be a lede number plus a row of three supporting figures. The row
is gone, and the reason is arithmetic rather than taste.

A README asset is a fixed-ratio image inside a fluid column, so its type
scales with the column while markdown type does not. GitHub's profile column
is 980px on a desktop and 358px on a phone, which means a 1200-unit viewBox
renders at 0.30x on a phone. The supporting row was set at 22px and 9px: 6.6px
and 2.7px as read. They were not small, they were absent.

The fix is not a bigger row. Three figures with captions cannot be set at a
legible size across one strip at any width that also leaves the lede dominant.
So the row moved out of the plate and into markdown, where it is legible at
every width, selectable, and findable by GitHub search. What stays here is the
one number the section opens on, and its unit.

The floor every text element in this repo is held to is 3.07% of the viewBox
width -- 11px as read on a 358px phone column, which is below the 12px GitHub
itself renders <sub> at. `tests/test_build.py` enforces it.
"""
from __future__ import annotations

from . import field, palette

# Narrower than the page, on purpose. Width here is not free space, it is the
# divisor: halving the viewBox doubles the apparent size of every mark in it.
# 760 is the widest this plate can be and still set its caption above the
# floor (26 / 760 = 3.42%).
VIEW_W = 760

# Everything is a fraction of the plate, so resizing it is a change of scale
# and not a change of design -- and so no width can quietly drop the caption
# below the 3.07% floor. CAP_FRAC is the binding one at 3.42%.
# Vertical only. The horizontal inset is zero for the reason hero.py gives:
# the plate has no edge any more, so an inset is not a margin, it is the one
# block on the page that does not line up with the rest.
MARGIN_FRAC = 0.058
NUM_FRAC = 0.0947
CAP_FRAC = 0.0342
ASPECT = 0.205          # height as a fraction of width, at the 760 default

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def render(number: str, caption: str, aria: str, view_w: int = VIEW_W) -> str:
    """One number and its unit on Atrium's field.

    `number` and `caption` must be traceable to something measured; this
    module carries no data of its own and composes nothing.
    """
    fg, _ = palette()
    m = view_w * MARGIN_FRAC
    num_px = view_w * NUM_FRAC
    cap_px = view_w * CAP_FRAC
    view_h = round(view_w * ASPECT)
    num_y = m + num_px * 0.78
    cap_y = num_y + cap_px * 1.25
    rule_y = view_h - m * 0.4

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" '
        f'width="{view_w}" height="{view_h}" role="img" aria-label="{aria}">\n'
        + field()
        + f'  <text x="0" y="{num_y:.1f}" '
          f'style="font:600 {num_px:.1f}px {MONO};letter-spacing:{view_w * 0.004:.1f}px" '
          f'fill="{fg}" fill-opacity=".95">{number}</text>\n'
          f'  <text x="3" y="{cap_y:.1f}" '
          f'style="font:400 {cap_px:.1f}px {MONO};letter-spacing:{view_w * 0.0032:.1f}px" '
          f'fill="{fg}" fill-opacity=".58">{caption}</text>\n'
          f'  <line x1="0" y1="{rule_y:.1f}" x2="{view_w:.0f}" '
          f'y2="{rule_y:.1f}" stroke="{fg}" stroke-opacity=".16" stroke-width="1"/>\n'
          "</svg>\n"
    )
