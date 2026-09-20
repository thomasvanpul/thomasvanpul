#!/usr/bin/env python3
"""Each direction beside the three references it borrows from.

Step 3 of the 19 Sep task. A direction shown on its own can only be liked or
disliked; shown next to what it was taken from, the *intent* is visible too,
and a borrowing that did not survive the trip is obvious.

One sheet per direction: the rendered page at 1012px on the left, the three
references stacked down the right, each captioned with the one thing it was
taken for.
"""
from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / "design" / "reference-board"
SHOTS = BOARD / "shots"
DIRECTIONS = ROOT / "design" / "directions"
OUT = ROOT / "design" / "comparisons"

GROUND = (13, 17, 23)
INK = (230, 237, 243)
DIM = (139, 148, 158)
MONO = "/System/Library/Fonts/SFNSMono.ttf"

BORROWS = {
    "index": ["gh-antfu", "gh-caneco", "gh-natemoo-re"],
    "playback": ["gh-platane", "gh-orhun", "gmunk-process-047"],
    "instrument": ["gmunk-interface-029", "gmunk-interface-022",
                   "web-anandchowdhary"],
}

LEFT_W, REF_W, PAD = 860, 520, 28
CAP_H = 66


def notes() -> dict[str, str]:
    rows = csv.DictReader((BOARD / "sources.tsv").open(encoding="utf-8"),
                          delimiter="\t")
    return {r["slug"]: r["note"] for r in rows}


def wrap(draw, text: str, font, width: int) -> list[str]:
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = f"{line} {w}".strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def sheet(name: str, note: dict[str, str]) -> Path:
    title = ImageFont.truetype(MONO, 26)
    body = ImageFont.truetype(MONO, 16)

    page = Image.open(DIRECTIONS / name / "page" / "dark-desktop.png")
    page = page.convert("RGB")
    page.thumbnail((LEFT_W, 4000))

    refs = []
    for slug in BORROWS[name]:
        im = Image.open(SHOTS / f"{slug}.png").convert("RGB")
        im.thumbnail((REF_W, 460))
        refs.append((slug, im))

    right_h = sum(im.height + CAP_H + PAD for _, im in refs)
    H = max(page.height, right_h) + 96
    W = LEFT_W + REF_W + 3 * PAD
    out = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(out)
    d.text((PAD, 26), f"{name.upper()}  ·  and what it is taken from",
           font=title, fill=INK)
    out.paste(page, (PAD, 84))

    y = 84
    x = LEFT_W + 2 * PAD
    for slug, im in refs:
        out.paste(im, (x, y))
        d.text((x, y + im.height + 8), slug, font=body, fill=INK)
        for i, line in enumerate(wrap(d, note[slug], body, REF_W)):
            d.text((x, y + im.height + 30 + i * 20), line, font=body, fill=DIM)
        y += im.height + CAP_H + PAD
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.png"
    out.save(path)
    return path


if __name__ == "__main__":
    note = notes()
    for name in BORROWS:
        p = sheet(name, note)
        print(f"{p.relative_to(ROOT)}  {Image.open(p).size}")
