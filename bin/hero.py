#!/usr/bin/env python3
"""Build the hero in both finishes, render it as GitHub does, and film it.

orhun's profile is the shape Thomas picked off the reference board: a paired
light/dark animated plate carrying the whole page, and a very short text block
under it. Nothing else is on the page, so nothing else is built here.

Two things this tool has to get right that the earlier runners did not.

The recording is twenty seconds, not seventeen. `bin/instrument.py` filmed a
long page and spent its time scrolling; this page is one image and three lines,
so scrolling is almost the whole page in three seconds and the rest of the time
is the animation looping. At 112 frames and 13fps the plate runs 8.6s, so a
twenty second film shows the loop join twice. That join is the thing to watch,
and it is why the film is longer than the page needs.

Both themes are shot at both widths. `bin/instrument.py` skipped light-phone
because light was a check and dark was the comparison. Here light is half the
deliverable -- orhun's page is a *pair* -- so it gets the same four shots.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bin.directions import WIDTHS, gfm_html, page, pick_theme, shoot  # noqa: E402
from bin.instrument import record  # noqa: E402
from generators import content, corridor  # noqa: E402
from generators.build import hero_picture  # noqa: E402

OUT = ROOT / "design" / "hero"

# Name, one line, links. The task's words, and the whole text block. They
# live in `generators/content.py` since the pick shipped, so a finish here
# previews exactly the text `generators/build.py` publishes.
NAME = content.NAME
LINE = content.LINE
LINKS = content.FOOTER_LINKS

RAW = "https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/"

# Twenty seconds, as the task asks, and split the way this page is shaped.
# The plate runs 8.6s, so the join between loop and loop lands inside the
# first hold and again inside the last one. The scroll in the middle is short
# because on a desktop this page does not scroll at all.
HOLD_TOP_MS = 8500
SCROLL_MS = 3000
HOLD_END_MS = 8500


def _name(stem: str, data: bytes, ext: str) -> str:
    return f"{stem}.{hashlib.sha256(data).hexdigest()[:7]}.{ext}"


def build_one(variant: str) -> dict:
    out_dir = OUT / variant
    shutil.rmtree(out_dir, ignore_errors=True)
    (out_dir / "page").mkdir(parents=True, exist_ok=True)
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    plates, names = {}, {}
    for theme in corridor.THEMES:
        got = corridor.build(variant, theme)
        plates[theme] = got
        for stem, blob, ext in (("anim", got["data"], got["ext"]),
                                ("still", got["still"], "png")):
            fname = _name(f"{stem}-{theme}", blob, ext)
            (assets / fname).write_bytes(blob)
            names[f"{stem}-{theme}"] = fname

    urls = {key: RAW + name for key, name in names.items()}
    readme = "\n".join([hero_picture(urls, plates["light"]["alt"]), "",
                        f"# {NAME}", "", LINE, "", LINKS, ""])
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    html = gfm_html(readme)
    heights, pages = {}, {}
    for theme in ("dark", "light"):
        body = pick_theme(html, theme).replace("../../assets/", "../assets/")
        for label, (column, window) in WIDTHS.items():
            dest = out_dir / "page" / f"{theme}-{label}.html"
            dest.write_text(page(body, theme, column), encoding="utf-8")
            heights[f"{theme}-{label}"] = shoot(
                dest, out_dir / "page" / f"{theme}-{label}.png", window)
            pages[f"{theme}-{label}"] = dest

    return {"variant": variant, "plates": plates, "assets": names,
            "dir": out_dir, "heights": heights, "pages": pages,
            "words": len(readme.split()),
            "prose": len(f"{NAME} {LINE}".split())}


def main() -> int:
    wanted = sys.argv[1:] or list(corridor.VARIANTS)
    for variant in wanted:
        got = build_one(variant)
        print(f"\n=== {variant} {'=' * (60 - len(variant))}")
        for theme in corridor.THEMES:
            p = got["plates"][theme]
            print(f"  plate {theme:5} {p['ext']:4} "
                  f"{len(p['data']) / 1024:7.1f} KB  "
                  f"(gif {p['sizes']['gif'] / 1024:.1f}, "
                  f"apng {p['sizes']['apng'] / 1024:.1f})  "
                  f"{p['frames']}f at {p['fps']}fps, {p['seconds']:.1f}s, "
                  f"{p['size'][0]}x{p['size'][1]}, "
                  f"still {len(p['still']) / 1024:.0f} KB "
                  f"(frame {p['still_frame']})")
        for key, h in sorted(got["heights"].items()):
            print(f"  page  {key:14} {h:5d}px tall")
        print(f"  words {got['words']} raw, {got['prose']} prose")
        scale = corridor.PHONE_COLUMN / corridor.WIDTH
        print(f"  type  smallest drawn label {corridor.LABEL:.0f} units in "
              f"{corridor.WIDTH} -> {corridor.LABEL * scale:.1f}px on a phone; "
              f"`_t` raises below {corridor.FLOOR:.1f} units "
              f"({corridor.MIN_APPARENT_PX:g}px)")

        for label, (w, h) in (("desktop", (1012, 860)), ("phone", (390, 844))):
            mp4 = got["dir"] / "page" / f"hero-{label}.mp4"
            shot = record(got["pages"][f"dark-{label}"], mp4, w, h,
                          HOLD_TOP_MS, SCROLL_MS, HOLD_END_MS)
            print(f"  video {label:8} {shot['seconds']:5.1f}s  "
                  f"{shot['bytes'] / 1024:7.1f} KB  "
                  f"{mp4.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
