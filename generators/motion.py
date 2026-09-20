"""The lattice as a moving image: one real frame, played back a week at a time.

Step 2's animated direction. GitHub renders Markdown, sanitised HTML and
images, and an image is allowed to move -- a GIF or an APNG is the only motion
this page can have, since script and CSS animation are both stripped.

What moves, and why it is honest
--------------------------------
The field does not move. It is one real region of
`showroom/atrium-lattice.png` -- the same frame every other asset on this page
is cut from -- reduced to a 120-column dot screen, and panning it would only
be a camera move. What moves is the
**record**: 53 real weekly contribution counts out of `data/contributions.json`
are drawn as a row along the bottom, and a line sweeps left to right, lighting
each week as it reaches it. One pass is one year. Atrium's own rule is that
depth is recency, so a plane travelling through the record is the scene's
grammar, not a decoration laid over it.

Keeping it small
----------------
A GIF of a panning noise field is 3.7MB, because every pixel changes in every
frame and there is nothing to delta. Holding the field still and moving one
2px line drops the same 53 frames to ~160KB, which is why the field is still.

No words are inside this image. `generators/directions.py` gives the reason at
length: GitHub's search, the browser's find and a screen reader all see one
`alt` string. Every number this animation implies is printed in the Markdown
beside it.
"""
from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from . import svg

ROOT = Path(__file__).resolve().parent.parent
LATTICE_PNG = ROOT / "showroom" / "atrium-lattice.png"
CONTRIB_JSON = ROOT / "data" / "contributions.json"

VIEW_W, VIEW_H = 900, 380
FIELD_H = 268
# Measured, not chosen: a search over 560/640/720-wide windows for the highest
# mean ink at the lowest spread across a 4x4 tiling returned this region
# (mean 150.6 of 255, spread 21.0). Taken at half size and doubled with
# NEAREST so every source pixel is an exact 2x2 block -- a fractional upscale
# smears the dot screen into grey.
CROP = (1100, 780, 1550, 923)
# As in `animate.py`: baked from the tokens, not typed. The ink here had
# drifted furthest of the four files -- it was Tailwind's slate-200, which is
# neither Primer's fg.default nor anything Atrium has ever issued.
GROUND = svg.rgb(svg.GROUND_DARK)
INK = svg.rgb(svg.token(svg.INK_DARK))
ACCENT = svg.rgb(svg.ACCENT_LINK)      # the link blue Thomas kept on 19 Sep
FPS = 14
STRIP_H = 112
SIDE = 30


def _weeks() -> list[int]:
    """370 real days folded into 53 weeks, oldest first."""
    days = json.loads(CONTRIB_JSON.read_text(encoding="utf-8"))["days"]
    counts = [d["count"] for d in days]
    return [sum(counts[i:i + 7]) for i in range(0, len(counts), 7)]


def _field(np, Image, ImageDraw):
    """The crop, reduced to a halftone dot screen on the dark ground.

    The first pass upscaled the crop's pixels with NEAREST, which photographs
    as television static: 85% of that region is above mid-grey, so a
    pixel-for-pixel rendering is a uniform light rectangle with no structure
    in it. The showroom asset this page already ships does not do that -- it
    reduces the frame to a dot screen and lets dot *area* carry darkness, the
    way a halftone does. Same here: 120 columns, one dot per cell, radius by
    value. The structure in the frame comes back and the ground stays ground.
    """
    src = Image.open(LATTICE_PNG).convert("L")
    cols = 120
    crop = src.crop(CROP)
    rows = max(1, round(cols * (FIELD_H / VIEW_W)))
    cell = Image.new("RGB", (VIEW_W, FIELD_H), GROUND)
    d = ImageDraw.Draw(cell)
    small = crop.resize((cols, rows), Image.BOX)
    ink = 255 - np.asarray(small).astype(float)
    ink = np.clip((ink - 130) / 125, 0, 1) ** 1.35
    px, py = VIEW_W / cols, FIELD_H / rows
    rmax = min(px, py) * 0.62
    for j in range(rows):
        for i in range(cols):
            v = float(ink[j, i])
            if v < 0.06:
                continue
            r = rmax * v ** 0.55
            cx, cy = (i + 0.5) * px, (j + 0.5) * py
            tone = tuple(int(GROUND[k] + min(1.0, 0.22 + 0.78 * v)
                             * (INK[k] - GROUND[k])) for k in range(3))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tone)
    return cell, ink, (cols, rows, px, py, rmax)


def render() -> bytes:
    """The animation, as GIF bytes. Raises if Pillow is missing."""
    import numpy as np
    from PIL import Image, ImageDraw

    weeks = _weeks()
    peak = max(weeks) or 1
    base = Image.new("RGB", (VIEW_W, VIEW_H), GROUND)
    field, ink, geom = _field(np, Image, ImageDraw)
    base.paste(field, (0, 0))

    frames = []
    step = (VIEW_W - 2 * SIDE) / len(weeks)
    for i in range(len(weeks)):
        im = base.copy()
        d = ImageDraw.Draw(im)
        for j, count in enumerate(weeks):
            x = SIDE + j * step
            h = 5 + (count / peak) ** 0.5 * (STRIP_H - 24)
            near = abs(j - i)
            target = ACCENT if near == 0 else INK
            alpha = 1.0 if near == 0 else (0.62 if near < 3 else 0.34)
            fill = tuple(int(GROUND[k] + alpha * (target[k] - GROUND[k]))
                         for k in range(3))
            d.rectangle([x, VIEW_H - 14 - h, x + step - 3.5, VIEW_H - 14],
                        fill=fill)
        x = SIDE + i * step + (step - 3.5) / 2
        # The sweep lights the field column it is passing through, not just
        # the week under it. That is the whole claim of the image -- the
        # record and the scene are the same object -- and a line that travels
        # over the field without touching it says the opposite.
        cols, rows, px, py, rmax = geom
        lo = max(0, int((x - 14) / px))
        hi = min(cols, int((x + 14) / px) + 1)
        for ci in range(lo, hi):
            for rj in range(rows):
                v = float(ink[rj, ci])
                if v < 0.06:
                    continue
                r = rmax * v ** 0.55
                cx, cy = (ci + 0.5) * px, (rj + 0.5) * py
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
        d.line([x, 0, x, VIEW_H - 8], fill=ACCENT, width=2)
        frames.append(im)

    # One shared palette and `disposal=1` are what make this 189KB instead of
    # 5.8MB. Quantising each frame on its own gives every frame a different
    # palette, which forces a full frame into the file each time; sharing one
    # palette lets Pillow store only the rectangle that changed, and between
    # two frames of this animation that rectangle is one sweep line and two
    # columns.
    pal = frames[0].convert("P", palette=Image.ADAPTIVE, colors=48)
    quantised = [f.quantize(palette=pal, dither=Image.Dither.NONE)
                 for f in frames]

    buf = BytesIO()
    quantised[0].save(buf, format="GIF", save_all=True,
                      append_images=quantised[1:],
                      duration=int(1000 / FPS), loop=0, optimize=True,
                      disposal=1)
    return buf.getvalue()


ALT = ("One real region of the Atrium lattice frame, reduced to a 120-column "
       "dot screen, with the year's 53 weekly contribution counts drawn along "
       "the bottom and a line sweeping through the field and the counts "
       "together, one week at a time")

if __name__ == "__main__":
    data = render()
    (ROOT / "preview" / "lattice-motion.gif").write_bytes(data)
    print(f"{len(data) / 1024:.0f} KB")


def still() -> bytes:
    """Frame zero, as PNG, for `prefers-reduced-motion`.

    The live page already pairs `hero.svg` with `hero-still.svg` this way. An
    animation with no still is a page that moves at a reader who asked it not
    to.
    """
    import numpy as np
    from PIL import Image, ImageDraw

    weeks = _weeks()
    peak = max(weeks) or 1
    im = Image.new("RGB", (VIEW_W, VIEW_H), GROUND)
    im.paste(_field(np, Image, ImageDraw)[0], (0, 0))
    d = ImageDraw.Draw(im)
    step = (VIEW_W - 2 * SIDE) / len(weeks)
    for j, count in enumerate(weeks):
        x = SIDE + j * step
        h = 5 + (count / peak) ** 0.5 * (STRIP_H - 24)
        fill = tuple(int(GROUND[k] + 0.62 * (INK[k] - GROUND[k]))
                     for k in range(3))
        d.rectangle([x, VIEW_H - 14 - h, x + step - 3.5, VIEW_H - 14], fill=fill)
    buf = BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
