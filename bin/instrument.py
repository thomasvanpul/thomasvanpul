#!/usr/bin/env python3
"""Build both instrument variations, render them as GitHub does, and film them.

Round 3 handed back PNGs of a page whose whole argument was that it moves, and
Thomas answered "I do not see any animations at all". A still cannot carry
that, so this tool ends with video: each variation is driven through a real
Chrome, scrolled at reading speed, and recorded to MP4 at desktop and phone
width. The stills are still produced, because they are what a side-by-side
comparison needs, but they are no longer the evidence.

Everything upstream of the recording is the pipeline the earlier rounds used
and is imported rather than copied -- `gh api /markdown` for the HTML, Primer's
published values for the chrome, 1012 and 390 for the two column widths -- so
these pages sit beside the ones in `design/directions/` and in
`.review/archive/` without anything being rescaled between them.

Headless Chrome on macOS clamps the viewport to a 500px minimum, so a 390px
window renders at 500 and crops, which looks exactly like text overflowing the
page. The window is 1044 and 500 and the page's own `max-width` does the
narrowing. The recording does not have this problem: Playwright sets a real
viewport, so the phone capture is filmed at 390 and is a true 390.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bin.directions import (MIN_APPARENT_PX, WIDTHS, gfm_html, page,  # noqa: E402
                            pick_theme, shoot, snake, type_floor)
from generators import animate, instrument  # noqa: E402

OUT = ROOT / "design" / "instrument"

# Long enough to read the page rather than to flick past it, and short enough
# that Thomas will watch both. The hold at the top is what makes the first
# animation visibly an animation before anything scrolls.
HOLD_TOP_MS = 2600
SCROLL_MS = 12000
HOLD_END_MS = 2600

SCROLL_JS = """
(ms) => new Promise(done => {
  const max = Math.max(0, document.body.scrollHeight - window.innerHeight);
  const t0 = performance.now();
  const ease = p => p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
  function step(t) {
    const p = Math.min(1, (t - t0) / ms);
    window.scrollTo(0, max * ease(p));
    p < 1 ? requestAnimationFrame(step) : done(max);
  }
  requestAnimationFrame(step);
})
"""


def record(html: Path, mp4: Path, width: int, height: int,
           hold_top: int = HOLD_TOP_MS, scroll: int = SCROLL_MS,
           hold_end: int = HOLD_END_MS) -> dict:
    """Film one page scrolling, in a real Chrome, and convert it to MP4.

    Playwright records WebM. GitHub will not be showing anyone a WebM, but
    Thomas will be watching this on a Mac, where MP4 opens in Quick Look and
    WebM does not -- so the conversion is not a detail, it is the difference
    between evidence he can look at and a file he has to find a player for.

    The three timings default to the ones this page wants and are arguments
    because `bin/hero.py` films a page that barely scrolls: there the time
    belongs to the animation looping, not to the scroll.
    """
    from playwright.sync_api import sync_playwright

    raw = mp4.parent / f".{mp4.stem}-raw"
    shutil.rmtree(raw, ignore_errors=True)
    raw.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        ctx = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=2,
            record_video_dir=str(raw),
            record_video_size={"width": width, "height": height},
        )
        pg = ctx.new_page()
        pg.goto(html.as_uri())
        pg.wait_for_load_state("networkidle")
        pg.wait_for_timeout(hold_top)
        travelled = pg.evaluate(SCROLL_JS, scroll)
        pg.wait_for_timeout(hold_end)
        ctx.close()
        browser.close()

    webm = next(raw.glob("*.webm"))
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(webm), "-c:v", "libx264", "-preset", "slow",
         "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         str(mp4)],
        check=True, capture_output=True, timeout=600)
    shutil.rmtree(raw, ignore_errors=True)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=width,height", "-of", "json", str(mp4)],
        check=True, capture_output=True, text=True).stdout
    meta = json.loads(probe)
    return {"path": mp4, "bytes": mp4.stat().st_size,
            "seconds": float(meta["format"]["duration"]),
            "scrolled": travelled}


PROSE_TAG = re.compile(r"<[^>]+>")
PROSE_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def prose_words(markdown: str) -> int:
    """Words a reader actually reads: no tags, no alt text, no table rules.

    The raw `split()` count the earlier rounds reported is not comparable
    across these pages, because three `<picture>` blocks carry about 130 words
    of alt text that nobody sees. Both numbers are printed; this is the one
    that answers "is there less prose than last time".
    """
    body = PROSE_LINK.sub(r"\1", PROSE_TAG.sub("", markdown))
    body = body.replace("&nbsp;", " ")
    skip = {"|", "---", "·", "###", "#"}
    return len([w for w in body.split() if w not in skip])


def build_one(variation: str) -> dict:
    out_dir = OUT / variation
    shutil.rmtree(out_dir, ignore_errors=True)
    (out_dir / "page").mkdir(parents=True, exist_ok=True)
    got = instrument.build(variation, out_dir)
    snake(out_dir / "page")

    html = gfm_html((out_dir / "README.md").read_text(encoding="utf-8"))
    heights, pages = {}, {}
    for theme in ("dark", "light"):
        body = pick_theme(html, theme).replace("../../assets/", "../assets/")
        for label, (column, window) in WIDTHS.items():
            if theme == "light" and label == "phone":
                continue          # light is a check, not a comparison
            dest = out_dir / "page" / f"{theme}-{label}.html"
            dest.write_text(page(body, theme, column), encoding="utf-8")
            heights[f"{theme}-{label}"] = shoot(
                dest, out_dir / "page" / f"{theme}-{label}.png", window)
            pages[f"{theme}-{label}"] = dest

    rows = type_floor(out_dir)
    got.update({
        "dir": out_dir, "heights": heights, "pages": pages, "svg_type": rows,
        "words": len((out_dir / "README.md").read_text().split()),
        "prose": prose_words((out_dir / "README.md").read_text()),
    })
    return got


def main() -> int:
    wanted = sys.argv[1:] or list(instrument.VARIATIONS)
    built = []
    for variation in wanted:
        got = build_one(variation)
        built.append(got)
        print(f"\n=== {variation} "
              f"{'=' * (60 - len(variation))}")
        for key, h in got["heights"].items():
            print(f"  page  {key:14} {h:5d}px tall")
        print(f"  words {got['words']} raw, {got['prose']} prose")
        for name, plate in got["plates"].items():
            print(f"  anim  {name:5} {plate['ext']:4} "
                  f"{len(plate['data']) / 1024:7.1f} KB  "
                  f"(gif {plate['sizes']['gif'] / 1024:.1f}, "
                  f"apng {plate['sizes']['apng'] / 1024:.1f})  "
                  f"{plate['frames']} frames at {plate['fps']}fps, "
                  f"{plate['seconds']:.1f}s")
        smallest = min(r[3] for r in got["svg_type"])
        under = [r for r in got["svg_type"] if r[3] < MIN_APPARENT_PX]
        print(f"  type  svg: {len(got['svg_type'])} sizes, smallest reads at "
              f"{smallest:.1f}px on a phone, {len(under)} under "
              f"{MIN_APPARENT_PX:g}px")
        for asset, size, width, apparent in got["svg_type"]:
            print(f"        {asset:30} {size:6.1f}px in {width:g} "
                  f"-> {apparent:5.1f}px  ({size / width * 100:.2f}%)")
        # The SVG floor above is read back off the files. The raster plates
        # cannot be measured that way -- their type is pixels by the time
        # anything can look at it -- so the check lives at the point of
        # drawing, and what is printed here is what that check permits.
        scale = animate.PHONE_COLUMN / animate.WIDTH
        print(f"  type  raster: smallest drawn label {animate.LABEL:.0f} units "
              f"in {animate.WIDTH} -> {animate.LABEL * scale:.1f}px on a phone "
              f"({animate.LABEL / animate.WIDTH * 100:.2f}%); `_text` raises "
              f"below {animate.FLOOR:.1f} units "
              f"({animate.MIN_APPARENT_PX:g}px)")

        for label, (w, h) in (("desktop", (1012, 860)), ("phone", (390, 844))):
            mp4 = got["dir"] / "page" / f"scroll-{label}.mp4"
            shot = record(got["pages"][f"dark-{label}" if label == "desktop"
                                       else "dark-phone"], mp4, w, h)
            print(f"  video {label:8} {shot['seconds']:5.1f}s  "
                  f"{shot['bytes'] / 1024:7.1f} KB  "
                  f"{shot['scrolled']:.0f}px scrolled  "
                  f"{mp4.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
