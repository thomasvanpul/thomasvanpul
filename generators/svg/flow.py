"""A stage flow, small, because four words do not need the width of a render.

Two changes from the version this replaces, both forced by the same
measurement (see `figures.py` for the arithmetic).

**It is narrow.** At a 1200 viewBox its 12.5px labels read at 3.7px on a
phone. Width is the divisor, so the way to make a label legible is to shrink
the plate, not to grow the type inside a plate that stays wide. At 520 the
same diagram sets its labels at 17px, which is 3.27% of the viewBox and reads
at 11.7px on a phone and 17px on a desktop.

**The sublabels are gone from the drawing.** "enclosure, Fusion 360" under a
105px box cannot be set above the floor at any width that still fits four
stages across. They are not lost -- they are the aria label now, which is
where a screen reader was getting them anyway and where GitHub's search can
see them.

What is left is the claim the diagram exists to carry: one person, the whole
chain, in order.

**Nothing in it moves any more.** It used to carry seven animations -- four
stage outlines brightening in turn, two dots running the track and a third
falling into stage two. At a 520 viewBox in a 358px phone column the running
dot is 3 units of 520, which is 2px as read: a flicker, not a motion. The page
now has exactly one moving mark and it is in the hero, where it is 26% of the
plate rather than 0.6% of one. See `hero.py`.
"""
from __future__ import annotations

from . import field, palette

VIEW_W = 520

# Fractions of the plate, for the reason figures.py gives: a width change
# must not be able to push the label under the 3.07% floor. LABEL_FRAC is
# 3.27%, which is the tightest margin on the page.
Y_TOP_FRAC = 0.042
BOX_H_FRAC = 0.077
HEIGHT_FRAC = 0.162
LABEL_FRAC = 0.0327
SIDE_LABEL_FRAC = 0.027
SIDE_GAP_FRAC = 0.05
SIDE_H_FRAC = 0.058

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def _geometry(n: int, view_w: int):
    """Margins and gaps scale with the plate so the proportions hold at any width."""
    margin_x = view_w * 0.03
    gap = view_w * 0.027
    box_w = (view_w - 2 * margin_x - (n - 1) * gap) / n
    xs = [margin_x + i * (box_w + gap) for i in range(n)]
    return box_w, xs, [x + box_w / 2 for x in xs]


def _stage(x: float, w: float, cx: float, label: str, fg: str,
           y_top: float, box_h: float, label_px: float) -> str:
    return (
        '<g>'
        f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{w:.1f}" height="{box_h:.1f}" rx="3" '
        f'fill="none" stroke="{fg}" stroke-opacity=".40" stroke-width="1"/>'
        f'<text x="{cx:.1f}" y="{y_top + box_h / 2 + label_px * 0.35:.1f}" text-anchor="middle" '
        f'style="font:600 {label_px:.1f}px {MONO};letter-spacing:{label_px * 0.094:.2f}px" '
        f'fill="{fg}" fill-opacity=".92">{label}</text>'
        '</g>'
    )


def _arrow(from_x: float, to_x: float, y: float, fg: str) -> str:
    return (
        f'<line x1="{from_x:.1f}" y1="{y:.1f}" x2="{to_x:.1f}" y2="{y:.1f}" '
        f'stroke="{fg}" stroke-opacity=".3" stroke-width="1"/>'
        f'<path d="M {to_x - 5:.1f} {y - 2.6:.1f} L {to_x:.1f} {y:.1f} L {to_x - 5:.1f} {y + 2.6:.1f}" '
        f'fill="none" stroke="{fg}" stroke-opacity=".3" stroke-width="1"/>'
    )


def render(stages: list[tuple[str, str]], duration: float | None = None,
           side_input: dict | None = None, view_w: int = VIEW_W,
           aria: str | None = None) -> str:
    """Render a stage-flow diagram.

    stages: list of (label, sublabel). The sublabel is not drawn -- it goes
            into the aria label, because it cannot be set legibly at this size.
    duration: accepted and ignored; the diagram no longer animates. Kept so
              callers and the fixture do not have to change shape.
    side_input: optional {"label", "sublabel", "connects_to": int}.
    """
    fg, _ = palette()
    n = len(stages)
    if n < 2:
        raise ValueError("flow needs at least 2 stages")

    box_w, xs, centers = _geometry(n, view_w)
    y_top = view_w * Y_TOP_FRAC
    box_h = view_w * BOX_H_FRAC
    label_px = view_w * LABEL_FRAC
    side_gap = view_w * SIDE_GAP_FRAC
    side_h = view_w * SIDE_H_FRAC
    midline = y_top + box_h / 2
    height = round(view_w * HEIGHT_FRAC
                   + (0 if side_input is None else side_gap + side_h))

    if aria is None:
        aria = " to ".join(
            f"{label} ({sub})" if sub else label for label, sub in stages)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {height}" '
        f'width="{view_w}" height="{height}" role="img" aria-label="{aria}">\n',
        field(),
    ]

    for i, (label, _sub) in enumerate(stages):
        parts.append(_stage(xs[i], box_w, centers[i], label, fg,
                            y_top=y_top, box_h=box_h, label_px=label_px))

    for i in range(n - 1):
        parts.append(_arrow(xs[i] + box_w, xs[i + 1], midline, fg))

    if side_input is not None:
        idx = side_input["connects_to"]
        sx, scx = xs[idx], centers[idx]
        side_y = y_top + box_h + side_gap
        parts.append(
            '<g>'
            f'<rect x="{sx:.1f}" y="{side_y}" width="{box_w:.1f}" height="{side_h:.1f}" rx="3" '
            f'fill="none" stroke="{fg}" stroke-opacity=".22" stroke-width="1" stroke-dasharray="3 3"/>'
            f'<text x="{scx:.1f}" y="{side_y + side_h / 2 + view_w * SIDE_LABEL_FRAC * 0.35:.1f}" text-anchor="middle" '
            f'style="font:600 {view_w * SIDE_LABEL_FRAC:.1f}px {MONO};letter-spacing:1.4px" '
            f'fill="{fg}" fill-opacity=".7">{side_input["label"]}</text>'
            f'<line x1="{scx:.1f}" y1="{side_y}" x2="{scx:.1f}" y2="{y_top + box_h:.1f}" '
            f'stroke="{fg}" stroke-opacity=".25" stroke-width="1"/>'
            f'<circle cx="{scx:.1f}" cy="{side_y}" r="2.5" fill="{fg}" fill-opacity=".7"/>'
            '</g>'
        )

    parts.append('\n</svg>\n')
    return "".join(parts)
