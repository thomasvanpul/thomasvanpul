#!/usr/bin/env python3
"""Build the three bold directions, render each through GitHub's Markdown.

Same renderer, same Primer values, same two widths as `bin/directions.py`, so
these stills sit next to the ones in `.review/archive/` and in
`design/rejected/` without anything being re-scaled between them. The helpers
are imported from `bin/directions.py` rather than copied, so a fix to the
phone-width clamp or to the trim lands in both.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bin.directions import (MIN_APPARENT_PX, WIDTHS, page, gfm_html,  # noqa: E402
                            pick_theme, shoot, snake, type_floor)
from generators import bold  # noqa: E402

OUT = ROOT / "design" / "directions"


def main() -> int:
    wanted = sys.argv[1:] or list(bold.PLANS)
    for name in wanted:
        out_dir = OUT / name
        shutil.rmtree(out_dir, ignore_errors=True)
        (out_dir / "page").mkdir(parents=True, exist_ok=True)
        bold.build(name, out_dir)
        snake(out_dir / "page")

        html = gfm_html((out_dir / "README.md").read_text(encoding="utf-8"))
        for theme in ("dark", "light"):
            body = pick_theme(html, theme).replace("../../assets/", "../assets/")
            for label, (column, window) in WIDTHS.items():
                if theme == "light" and label == "phone":
                    continue          # light is a check, not a comparison
                dest = out_dir / "page" / f"{theme}-{label}.html"
                dest.write_text(page(body, theme, column), encoding="utf-8")
                height = shoot(dest, out_dir / "page" / f"{theme}-{label}.png",
                               window)
                print(f"{name:11} {theme:5} {label:8} {height:5d}px tall")

        rows = type_floor(out_dir)
        offenders = [r for r in rows if r[3] < MIN_APPARENT_PX]
        smallest = min((r[3] for r in rows), default=float("nan"))
        print(f"{name:11} type: {len(rows)} sizes, smallest reads at "
              f"{smallest:.1f}px on a phone, {len(offenders)} under "
              f"{MIN_APPARENT_PX:g}px")
        for asset, size, width, apparent in rows:
            print(f"              {asset:28} {size:6.1f}px in {width:g} "
                  f"-> {apparent:5.1f}px  ({size / width * 100:.2f}%)")
        words = len((out_dir / "README.md").read_text(encoding="utf-8").split())
        print(f"{name:11} README {words} words\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
