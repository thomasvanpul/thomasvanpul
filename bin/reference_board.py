#!/usr/bin/env python3
"""Photograph the reference board's sources so they can be looked at side by side.

Step 1 of the 19 Sep "way better" task. Every entry in
`design/reference-board/sources.tsv` is shot through the same headless Chrome
that `bin/directions.py` uses, at one width, so a GitHub profile and a
portfolio site are comparable rather than each being judged at its own scale.

Two deliberate differences from `bin/directions.py`:

* device scale is 1, not 2. These are reference photographs, not type
  measurements -- at scale 2 a 20-entry board is ~90MB and nothing is learned.
* `--virtual-time-budget=9000`, not 4000. Portfolio sites are JavaScript and a
  4s budget photographs a loading state, which looks exactly like a site that
  has no content.

Local files (the GMUNK frames) are copied and downscaled instead, since there
is no page to render.
"""
from __future__ import annotations

import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / "design" / "reference-board"
SHOTS = BOARD / "shots"
SOURCES = BOARD / "sources.tsv"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

WINDOW = (1280, 1500)
FRAME_WIDTH = 1200


def shoot(url: str, png: Path) -> bool:
    try:
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--window-size={WINDOW[0]},{WINDOW[1]}",
             "--screenshot=" + str(png),
             "--default-background-color=0d1117",
             "--force-device-scale-factor=1",
             "--virtual-time-budget=9000", url],
            check=True, capture_output=True, text=True, timeout=180)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"  FAILED {url}: {type(exc).__name__}")
        return False
    return png.exists() and png.stat().st_size > 8_000


def copy_frame(src: Path, png: Path) -> bool:
    if not src.exists():
        print(f"  MISSING {src}")
        return False
    shutil.copy(src, png.with_suffix(src.suffix))
    subprocess.run(["sips", "-Z", str(FRAME_WIDTH), "-s", "format", "png",
                    str(png.with_suffix(src.suffix)), "--out", str(png)],
                   check=True, capture_output=True)
    if png.with_suffix(src.suffix) != png:
        png.with_suffix(src.suffix).unlink()
    return png.exists()


KINDS = [("profile", "GitHub profile READMEs",
          "What a profile can look like when it is designed rather than "
          "assembled out of badges."),
         ("site", "Portfolio pages",
          "Where the bar actually is. None of these is a README, and that is "
          "the point: they are what the reader has seen before arriving."),
         ("frame", "Tron: Ares, GMUNK",
          "From `Atlas/Projects/Atrium/References/`. Atrium's own visual "
          "language, and the one reference here that is already Thomas's.")]


def index(rows: list[dict]) -> None:
    """Write the board's index page from the same table the shots came from."""
    out = ["# Reference board",
           "",
           "Shot on 2026-09-19 with `bin/reference_board.py`: headless Chrome, "
           "1280px wide, one screenshot each, device scale 1. Three sources "
           "were dropped because they did not render headless — "
           "`bruno-simon.com` and `cassie.codes` photographed as empty "
           "canvases, and `andyruwruw`'s generated now-playing card came back "
           "as grey placeholders. That is a fact about the screenshot, not "
           "about the site.",
           ""]
    for kind, title, blurb in KINDS:
        out += [f"## {title}", "", blurb, ""]
        for row in [r for r in rows if r["kind"] == kind]:
            png = f"shots/{row['slug']}.png"
            if not (BOARD / png).exists():
                continue
            src = row["url"] if not row["url"].startswith("file://") else None
            head = f"### [{row['slug']}]({src})" if src else f"### {row['slug']}"
            out += [head, "", row["note"], "",
                    f'<img alt="{row["slug"]}" src="{png}" width="820">', ""]
    (BOARD / "index.md").write_text("\n".join(out), encoding="utf-8")


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(SOURCES.open(encoding="utf-8"), delimiter="\t"))
    only = set(sys.argv[1:])
    ok = bad = 0
    for row in rows:
        slug = row["slug"]
        if only and slug not in only:
            continue
        png = SHOTS / f"{slug}.png"
        if png.exists() and png.stat().st_size > 8_000 and not only:
            ok += 1
            continue
        print(f"{slug:34} {row['url'][:70]}")
        got = (copy_frame(Path(row["url"][len("file://"):]), png)
               if row["url"].startswith("file://") else shoot(row["url"], png))
        ok, bad = (ok + 1, bad) if got else (ok, bad + 1)
    index(rows)
    print(f"\n{ok} shot, {bad} failed, {len(rows)} sources")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
