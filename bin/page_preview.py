#!/usr/bin/env python3
"""Render the whole README the way GitHub will, so the page can be judged.

`make preview` rasterises the assets one at a time, which answers "is this
asset right" and not "does this page hold together". The second question is
the one that has failed twice, and it cannot be answered from a folder of
PNGs — the thing being judged is how the assets sit against GitHub's own
chrome, and against each other, down the length of the page.

How much of this is real
------------------------
The markdown is converted by GitHub itself, through `gh api /markdown`, so
the HTML structure, heading sizes, code spans and `<picture>` handling are
not an approximation. The surrounding page is: canvas colour, text colour
and content width are Primer's published values written out below, not
scraped, and the profile column is a little narrower than a repo's. Read the
output as "very close", not "pixel exact".

Both themes are written as separate files with the matching `<source>`
already selected, rather than relying on a headless browser to honour
`prefers-color-scheme` during a screenshot.

The snake is not built here. It is published to the `output` branch twice a
day by `.github/workflows/snake.yml`, so the copy on that branch is still in
whatever palette the workflow had last time it ran. This script fetches it
and substitutes the colours the workflow *now* asks for, which is what the
next run will publish.
"""
from __future__ import annotations

import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "preview" / "page"

# Primer, canvas.default / fg.default / border.default / neutral.muted.
# Primer, canvas.default / fg.default / border.default / neutral.muted / accent.fg.
# The last one is the link colour, and it is not the same in the two themes:
# GitHub serves #4493f8 on dark and #0969da on light. Hard-coding the dark one
# for both is how a light-theme preview quietly lies about the one colour on
# this page that is not ours to choose.
THEME_CSS = {
    "dark": ("#0d1117", "#e6edf3", "#3d444d", "rgba(101,108,118,0.2)", "#9198a1", "#4493f8"),
    "light": ("#ffffff", "#1f2328", "#d1d9e0", "rgba(212,217,223,0.32)", "#59636e", "#0969da"),
}

# What is on the `output` branch right now, mapped to what the workflow now
# asks for. The branch was last deployed at 04:06 UTC on 2026-09-19 and
# snake.yml was restyled at 11:59 UTC the same day, so the published copy is
# still Platane's stock ramp with a purple snake; the next scheduled run is
# the first that will carry the profile's own colours. Re-read `--c0`..`--c4`
# and `--cs` off the published SVG if this stops substituting.
SNAKE_SUBS = {
    "dark": [("#161b22", "#080302"), ("#01311f", "#450d0a"), ("#034525", "#78140f"),
             ("#0f6d31", "#b81d14"), ("#00c647", "#e84552"), ("purple", "#f6eaec")],
    "light": [("#ebedf0", "#f6eaec"), ("#9be9a8", "#e84552"), ("#40c463", "#b81d14"),
              ("#30a14e", "#78140f"), ("#216e39", "#450d0a"), ("purple", "#080302")],
}

RAW = "https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/"
PICTURE = re.compile(r"<picture>(.*?)</picture>", re.S)
SOURCE = re.compile(r'<source media="\(prefers-color-scheme: (dark|light)\)" srcset="([^"]+)"')


def gfm_html(markdown: str) -> str:
    return subprocess.run(
        ["gh", "api", "--method", "POST", "/markdown", "-f", "mode=gfm",
         "-f", f"text={markdown}"],
        check=True, capture_output=True, text=True,
    ).stdout


def local_snake(theme: str) -> Path:
    """Fetch the published snake and recolour it to what the workflow now asks."""
    name = "github-contribution-grid-snake-dark.svg" if theme == "dark" \
        else "github-contribution-grid-snake.svg"
    dest = OUT / f"snake-{theme}.svg"
    if not dest.exists():
        with urllib.request.urlopen(RAW + "output/" + name, timeout=30) as r:
            body = r.read().decode("utf-8")
        for old, new in SNAKE_SUBS[theme]:
            body = body.replace(old, new).replace(old.upper(), new)
        dest.write_text(body, encoding="utf-8")
    return dest


def pick_theme(html: str, theme: str) -> str:
    """Collapse every <picture> to the one <img> this theme would load."""
    def one(m: re.Match) -> str:
        chosen = {t: u for t, u in SOURCE.findall(m.group(1))}.get(theme)
        img = re.search(r"<img[^>]*>", m.group(1)).group(0)
        return re.sub(r'src="[^"]*"', f'src="{chosen}"', img) if chosen else img
    html = PICTURE.sub(one, html)
    html = html.replace(RAW + "main/assets/", "../../assets/")
    html = html.replace(RAW + "output/github-contribution-grid-snake-dark.svg",
                        "snake-dark.svg")
    html = html.replace(RAW + "output/github-contribution-grid-snake.svg",
                        "snake-light.svg")
    return html


def page(body: str, theme: str, width: int) -> str:
    canvas, fg, border, code_bg, muted, link = THEME_CSS[theme]
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="color-scheme" content="{theme}">
<style>
  html {{ background: {canvas}; }}
  body {{ margin: 0 auto; padding: 32px 16px 64px; max-width: {width}px;
         background: {canvas}; color: {fg};
         font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans",
               Helvetica, Arial, sans-serif; }}
  img, svg {{ max-width: 100%; height: auto; }}
  h3 {{ font-size: 1.25em; font-weight: 600; margin: 24px 0 16px; }}
  p {{ margin: 0 0 16px; }}
  hr {{ height: .25em; border: 0; background: {border}; margin: 24px 0; }}
  sub {{ font-size: 12px; color: {muted}; }}
  a {{ color: {link}; text-decoration: none; }}
  table {{ border-collapse: collapse; margin: 0 0 16px; display: block;
          width: max-content; max-width: 100%; overflow: auto; }}
  th, td {{ padding: 6px 13px; border: 1px solid {border}; }}
  tr:nth-child(2n) {{ background: {code_bg}; }}
  code {{ background: {code_bg}; padding: .2em .4em; margin: 0; font-size: 85%;
         border-radius: 6px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .markdown-body div[align="center"] {{ text-align: center; }}
</style></head><body class="markdown-body">{body}</body></html>"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    html = gfm_html((ROOT / "README.md").read_text(encoding="utf-8"))
    for theme in ("dark", "light"):
        local_snake(theme)
        body = pick_theme(html, theme)
        for label, width in (("desktop", 1012), ("phone", 390)):
            dest = OUT / f"{theme}-{label}.html"
            dest.write_text(page(body, theme, width), encoding="utf-8")
            print(f"wrote {dest.relative_to(ROOT)}  ({width}px)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
