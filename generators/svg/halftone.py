"""Halftone showroom — a committed product render redrawn as a dot screen.

Why a dot screen rather than the render itself
----------------------------------------------
The canonical BlueBand renders live in the public `blueband-concept` repo and
are ~1.9 MB each. Referencing one directly would be the single heaviest
request on the page by an order of magnitude, and a photographic raster next
to a page of monochrome line work reads as a foreign object.

Screening it solves both. The output is a monochrome SVG in the profile
palette, it inverts cleanly between themes because the mark *is* the ink, and
it lands in the same visual language as the rest of the page: a field of small
marks where size carries the information.

Where the pixels come from
--------------------------
Not from here. `generators/build.py` fetches the source PNG once, reduces it
to a coarse luminance grid, and commits that grid to `data/`. This module only
turns a grid into marks. That split is deliberate: the build stays
reproducible offline, CI does not re-download a 1.9 MB PNG on every run, and
the only thing in version control is a few kilobytes of numbers.

Mapping
-------
Cell value is *darkness*, 0 (paper) to 9 (ink), quantised on ingest. Mark
radius rises with darkness, so the band renders as marks and the lit backdrop
renders as nothing. The same mapping serves both themes because in each one
the foreground colour is the ink and the page is the paper.
"""
from __future__ import annotations

from . import palette

VIEW_W = 1200
# Tighter than the rest of the page's 70px margin on purpose: this is the
# only picture on the profile and it was still the tallest thing on it at
# 70. Every pixel of margin here costs two pixels of page height.
MARGIN_X = 45.0

# Darkness below this is backdrop and gets no mark at all. Set from looking at
# the rasterised output: at 2 the lit background picks up a faint tone that
# reads as noise rather than as the seamless sweep the render actually has.
INK_FLOOR = 3

# Stroke width per darkness bucket, indexed 0-9. Zero means "no mark".
DOT_WIDTH = [0.0, 0.0, 0.0, 2.0, 2.9, 3.8, 4.7, 5.6, 6.5, 7.4]


def render(theme: str, grid: dict, aria: str) -> str:
    """Render a quantised luminance grid as a halftone SVG.

    grid: {"cols": int, "rows": int, "cells": str} where `cells` is one
    character per cell, '0'-'9', row-major.
    """
    fg, _ = palette(theme)
    cols, rows = grid["cols"], grid["rows"]
    cells = grid["cells"]
    if cols <= 0 or rows <= 0 or len(cells) != cols * rows:
        raise ValueError(f"grid is {cols}x{rows} but carries {len(cells)} cells")

    pitch = (VIEW_W - 2 * MARGIN_X) / (cols - 1) if cols > 1 else 0.0
    view_h = round(MARGIN_X + (rows - 1) * pitch + MARGIN_X)

    # One path per bucket: every mark in a bucket shares a stroke width, so
    # the width is written once instead of once per mark.
    buckets: dict[int, list[str]] = {}
    for idx, ch in enumerate(cells):
        value = ord(ch) - 48
        if value < INK_FLOOR:
            continue
        x = round(MARGIN_X + (idx % cols) * pitch)
        y = round(MARGIN_X + (idx // cols) * pitch)
        buckets.setdefault(value, []).append(f"M{x} {y}h.01")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {view_h}" '
        f'width="{VIEW_W}" height="{view_h}" role="img" aria-label="{aria}">\n'
    ]
    for value in sorted(buckets):
        width = DOT_WIDTH[value]
        # Lighter cells also carry less opacity, which keeps the shoulder of a
        # gradient from banding into visible steps.
        opacity = 0.40 + 0.06 * (value - INK_FLOOR)
        parts.append(
            f'  <path d="{"".join(buckets[value])}" stroke="{fg}" '
            f'stroke-opacity="{min(opacity, 0.95):.2f}" stroke-width="{width:g}" '
            'stroke-linecap="round" fill="none"/>\n'
        )
    parts.append("</svg>\n")
    return "".join(parts)
