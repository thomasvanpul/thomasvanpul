#!/usr/bin/env python3
"""Photograph a README the way a visitor sees it: 390px and 1280px, both
themes, every card closed and every card open.

    python3 bin/page_shots.py                     # README.md -> design/interactive/after/
    python3 bin/page_shots.py --rev HEAD~1 --out design/interactive/before

How close this is to GitHub
---------------------------
The markdown goes through `gh api /markdown` when that works. When it does
not (a cloud session is refused that endpoint) it goes through cmark-gfm, the
C library GitHub's renderer is built on, with the same extensions, and then
through a sanitiser that does the part of GitHub's that matters here: it
drops `<script>`, `<style>` and every `style=` and `on*=` attribute. Which one
ran is printed and written to `render.txt` beside the shots.

The colour scheme is set on the browser, not faked in the HTML, so each
`<picture>` picks its own source exactly as it would for a reader. The
surrounding page is Primer's published colours and widths, not a scrape:
the 1280 shot puts the README in a 900px column, which is roughly what
github.com gives a profile README beside its sidebar at that window width.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bin.page_preview import THEME_CSS  # noqa: E402

RAW = "https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/"
SIZES = {"phone": (390, 390), "desktop": (1280, 900)}


def render(markdown: str) -> tuple[str, str]:
    try:
        out = subprocess.run(
            ["gh", "api", "--method", "POST", "/markdown", "-f", "mode=gfm",
             "-f", f"text={markdown}"],
            check=True, capture_output=True, text=True, timeout=60).stdout
        return out, "GitHub markdown API (gh api /markdown)"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        import cmarkgfm
        from cmarkgfm.cmark import Options
        html = cmarkgfm.github_flavored_markdown_to_html(
            markdown, options=Options.CMARK_OPT_UNSAFE)
        return sanitise(html), ("cmark-gfm (GitHub's markdown library) plus a sanitiser "
                                "for script, style and on* attributes; the GitHub API "
                                "was not reachable")


def sanitise(html: str) -> str:
    html = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S | re.I)
    html = re.sub(r'\s(style|on\w+)="[^"]*"', "", html, flags=re.I)
    return html


def localise(html: str) -> str:
    """Point every published asset URL at the copy of that file in the repo."""
    def find(m: re.Match) -> str:
        name = m.group(1)
        for hit in sorted(ROOT.glob(f"**/{name}")):
            if ".git" not in hit.parts:
                return hit.as_uri()
        return m.group(0)
    return re.sub(re.escape(RAW) + r"([\w.-]+)", find, html)


def page(body: str, theme: str, column: int) -> str:
    canvas, fg, border, code_bg, muted, link = THEME_CSS[theme]
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="color-scheme" content="{theme}">
<style>
  html {{ background: {canvas}; }}
  body {{ margin: 0 auto; padding: 32px 16px 64px; max-width: {column}px;
         box-sizing: border-box; background: {canvas}; color: {fg};
         font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans",
               Helvetica, Arial, sans-serif; }}
  img {{ max-width: 100%; height: auto; box-sizing: content-box; }}
  h1 {{ font-size: 2em; font-weight: 600; margin: 24px 0 16px; padding-bottom: .3em;
        border-bottom: 1px solid {border}; }}
  p, ul, table, details {{ margin: 0 0 16px; }}
  summary {{ cursor: pointer; }}
  sub {{ font-size: 12px; color: {muted}; }}
  a {{ color: {link}; text-decoration: none; }}
  table {{ border-collapse: collapse; display: block; width: max-content;
          max-width: 100%; overflow: auto; }}
  th, td {{ padding: 6px 13px; border: 1px solid {border}; }}
  tr:nth-child(2n) {{ background: {code_bg}; }}
  code {{ background: {code_bg}; padding: .2em .4em; font-size: 85%; border-radius: 6px;
         font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
</style></head><body class="markdown-body">{body}</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", help="photograph README.md as of this git revision")
    ap.add_argument("--out", type=Path, default=ROOT / "design" / "interactive" / "after")
    args = ap.parse_args()
    args.out = args.out.resolve()

    md = (subprocess.run(["git", "show", f"{args.rev}:README.md"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout
          if args.rev else (ROOT / "README.md").read_text(encoding="utf-8"))
    html, how = render(md)
    body = localise(html)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "render.txt").write_text(how + "\n", encoding="utf-8")
    print(f"rendered with {how}")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        for theme in ("dark", "light"):
            for label, (window, column) in SIZES.items():
                src = args.out / f"{theme}-{label}.html"
                src.write_text(page(body, theme, column), encoding="utf-8")
                ctx = browser.new_context(viewport={"width": window, "height": 900},
                                          color_scheme=theme, device_scale_factor=1)
                tab = ctx.new_page()
                tab.goto(src.as_uri())
                tab.wait_for_load_state("networkidle")
                states = ["closed"]
                if tab.locator("details").count():
                    states.append("open")
                for state in states:
                    if state == "open":
                        tab.evaluate("document.querySelectorAll('details')"
                                     ".forEach(d => d.open = true)")
                        tab.wait_for_load_state("networkidle")
                    shot = args.out / f"{theme}-{label}-{state}.png"
                    tab.screenshot(path=str(shot), full_page=True)
                    h = tab.evaluate("document.documentElement.scrollHeight")
                    w = tab.evaluate("document.documentElement.scrollWidth")
                    print(f"wrote {shot.relative_to(ROOT)}  {w}x{h}"
                          + ("  OVERFLOWS" if w > window else ""))
                ctx.close()
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
