#!/usr/bin/env python3
"""Build every direction, render each through GitHub's Markdown, photograph it.

`make page` answers "does this page hold together" for the page that is live.
This answers it for pages that are not, so two or three of them can be put
side by side before one is chosen. Same renderer, same Primer values, same
widths, so the stills are comparable with the ones already in
`.review/archive/`.

Headless Chrome on macOS clamps the viewport to a 500px minimum. Asking for
`--window-size=390` renders at 500 and then crops the shot to 390, which cuts
110px off the right of a centred body and looks exactly like text overflowing
the page. The 2026-09-19 16:03 session nearly filed a phone-width layout bug
that did not exist. So the window is 1044 and 500, and the page's own
`max-width` does the narrowing -- 1012 and 390, GitHub's two column widths.

It also re-runs this repo's type floor over each direction's assets, because
`tests/test_build.py` only ever sees a default build and would not notice a
direction that set type too small to read.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bin.page_preview import THEME_CSS, gfm_html, page, pick_theme  # noqa: E402
from generators import directions  # noqa: E402

OUT = ROOT / "preview" / "directions"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# bin/page_preview.py, verbatim: GitHub's profile column minus its padding.
PHONE_COLUMN = 390 - 32
MIN_APPARENT_PX = 11.0

WIDTHS = {"desktop": (1012, 1044), "phone": (390, 500)}
FONT_PX = re.compile(r"font:\s*\d+\s+([\d.]+)px")
VIEW_BOX = re.compile(r'viewBox="0 0 ([\d.]+) [\d.]+"')


def snake(dest: Path) -> None:
    """Reuse the recoloured snake `make page` already fetched."""
    src = ROOT / "preview" / "page"
    for theme in ("dark", "light"):
        name = f"snake-{theme}.svg"
        if (src / name).exists():
            shutil.copy(src / name, dest / name)


def type_floor(out_dir: Path) -> list[str]:
    """Every text element, as it renders in a 358px phone column."""
    rows = []
    for asset in sorted((out_dir / "assets").glob("*.svg")):
        body = asset.read_text(encoding="utf-8")
        vb = VIEW_BOX.search(body)
        width = float(vb.group(1))
        scale = min(1.0, PHONE_COLUMN / width)
        for size in sorted({float(m) for m in FONT_PX.findall(body)}):
            rows.append((asset.name, size, width, size * scale))
    return rows


# Headless Chrome shoots the window, not the document, and there is no flag
# that asks it for the whole page. So the window is made taller than any page
# this repo will produce and the dead canvas underneath is trimmed off
# afterwards, which also gives the rendered page height as a measurement
# rather than as an estimate.
TALL = 7000


def shoot(html: Path, png: Path, window: int) -> int:
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--window-size={window},{TALL}", "--screenshot=" + str(png),
         "--default-background-color=0d1117", "--force-device-scale-factor=2",
         "--virtual-time-budget=4000", html.as_uri()],
        check=True, capture_output=True, text=True, timeout=300)
    return trim(png)


def trim(png: Path, pad: int = 48) -> int:
    """Cut the empty canvas under the page, and return its height in CSS px."""
    from PIL import Image
    import numpy as np

    im = Image.open(png).convert("RGB")
    a = np.asarray(im)
    ground = a[a.shape[0] - 1, a.shape[1] // 2]
    rows = np.any(np.abs(a.astype(int) - ground.astype(int)).sum(axis=2) > 6, axis=1)
    last = int(np.max(np.nonzero(rows))) if rows.any() else a.shape[0] - 1
    bottom = min(a.shape[0], last + pad)
    im.crop((0, 0, a.shape[1], bottom)).save(png)
    return bottom // 2  # shot at device-scale-factor 2


def main() -> int:
    wanted = sys.argv[1:] or list(directions.PLANS)
    for name in wanted:
        out_dir = OUT / name
        shutil.rmtree(out_dir, ignore_errors=True)
        (out_dir / "page").mkdir(parents=True, exist_ok=True)
        directions.build(name, out_dir)
        snake(out_dir / "page")

        html = gfm_html((out_dir / "README.md").read_text(encoding="utf-8"))
        # Dark is what the task asks to be judged on. Light is shot once, for
        # the direction that is being recommended, because every asset here
        # flips with `prefers-color-scheme` and a direction that only works in
        # one theme is not shippable.
        # pick_theme rewrites the raw.githubusercontent URLs to
        # ../../assets/, which is right for preview/page/ and one level too
        # far up from preview/directions/<name>/page/. Without this every
        # image is a broken link, and a page of broken links renders at a
        # plausible height and photographs without an error -- all three
        # directions came back exactly 1992px tall before this line existed.
        body = pick_theme(html, "dark").replace("../../assets/", "../assets/")
        if name == "trimmed":
            light = pick_theme(html, "light").replace("../../assets/", "../assets/")
            dest = out_dir / "page" / "light-desktop.html"
            dest.write_text(page(light, "light", 1012), encoding="utf-8")
            shoot(dest, out_dir / "page" / "light-desktop.png", 1044)
        for label, (column, window) in WIDTHS.items():
            dest = out_dir / "page" / f"dark-{label}.html"
            dest.write_text(page(body, "dark", column), encoding="utf-8")
            height = shoot(dest, out_dir / "page" / f"dark-{label}.png", window)
            print(f"{name:11} {label:8} {height:5d}px tall  "
                  f"{dest.relative_to(ROOT)}")

        offenders = [r for r in type_floor(out_dir) if r[3] < MIN_APPARENT_PX]
        rows = type_floor(out_dir)
        smallest = min((r[3] for r in rows), default=float("nan"))
        print(f"{name:11} type: {len(rows)} sizes, smallest reads at "
              f"{smallest:.1f}px on a phone, {len(offenders)} under "
              f"{MIN_APPARENT_PX:g}px")
        for asset, size, width, apparent in rows:
            print(f"              {asset:34} {size:6.1f}px in {width:g} "
                  f"-> {apparent:5.1f}px  ({size / width * 100:.2f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
