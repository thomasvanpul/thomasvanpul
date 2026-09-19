"""Ingest a committed product render into a small luminance grid.

This is the half of the showroom pipeline that touches the network and needs
Pillow. It runs only when a token-bearing build can reach the source image;
every other build reads the grid this one committed. See
generators/svg/halftone.py for why the split exists.

Nothing here is required for a build to succeed. If the source is
unreachable, or Pillow is not installed, ingest returns None and the build
falls back to the committed grid — and if there is no committed grid either,
the showroom is simply absent from the page. A profile build must never fail
because a picture was slow.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

UA = "thomasvanpul-profile-builder"
LEVELS = 10  # darkness buckets, written as the characters '0'-'9'


def _fetch(url: str, timeout: int = 45) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"warning: showroom source unreachable ({url}): {e}", file=sys.stderr)
        return None


def ingest(url: str, cols: int, crop: tuple[float, float, float, float] | None = None,
           source_bytes: bytes | None = None) -> dict | None:
    """Return {"cols", "rows", "cells", "source"} or None if unavailable.

    `crop` is (left, top, right, bottom) as fractions of the source, applied
    before the reduction so the grid's aspect ratio is the cropped one.
    """
    try:
        from PIL import Image
    except ImportError:
        print("warning: Pillow not installed, skipping showroom ingest", file=sys.stderr)
        return None

    raw = source_bytes if source_bytes is not None else _fetch(url)
    if not raw:
        return None

    try:
        img = Image.open(BytesIO(raw)).convert("L")
    except OSError as e:
        print(f"warning: showroom source is not a readable image: {e}", file=sys.stderr)
        return None

    if crop:
        w, h = img.size
        img = img.crop((int(w * crop[0]), int(h * crop[1]),
                        int(w * crop[2]), int(h * crop[3])))

    rows = max(1, round(cols * img.size[1] / img.size[0]))
    # BOX averages every source pixel into its cell. LANCZOS would sharpen
    # edges the dot screen cannot resolve anyway, and sharpening before a
    # heavy downsample is how you get ringing artefacts in the quiet areas.
    small = img.resize((cols, rows), Image.BOX)

    # Normalise against the observed range rather than 0-255: these renders
    # sit in a narrow mid-grey band, and stretching to the extremes is what
    # makes the silhouette read at this mark size.
    values = list(small.getdata())
    lo, hi = min(values), max(values)
    span = max(hi - lo, 1)

    cells = []
    for v in values:
        # Darkness, not luminance: the mark is the ink.
        darkness = 1.0 - (v - lo) / span
        cells.append(str(min(LEVELS - 1, int(darkness * LEVELS))))

    return {"source": url, "cols": cols, "rows": rows, "cells": "".join(cells)}


def read_cache(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        grid = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"warning: ignoring unreadable {path.name}: {e}", file=sys.stderr)
        return None
    if not all(k in grid for k in ("cols", "rows", "cells")):
        print(f"warning: {path.name} is missing grid keys", file=sys.stderr)
        return None
    return grid


def write_cache(path: Path, grid: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(grid) + "\n", encoding="utf-8")
