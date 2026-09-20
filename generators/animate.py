"""Three animated plates, each one real data moving through real time.

Round 3 shipped one animation and Thomas saw none of it, because the only
evidence offered was a PNG. A still of a moving image is a picture of a thing
standing still. So this module is the motion, and `bin/instrument.py` is the
proof that it moves -- it records the page playing, as video.

GitHub's Markdown pipeline strips script and CSS animation. An image is the
only thing on a profile README that is allowed to move, which means GIF or
APNG and nothing else. Both are produced for every plate here and the smaller
one is shipped; `encode()` reports the pair so the choice is a measurement.

What each plate is, and why it is honest
----------------------------------------
* **the year** -- the real lattice frame held still, with the year's 53 real
  weekly contribution counts swept through it one week at a time. The sweep
  lights the field column it passes, because the claim of the image is that
  the record and the scene are one object.
* **the day** -- the same lattice region, repainted once per hour in the
  colours Atrium itself would paint it. `data/atrium-tokens.json` carries the
  DayCurve's eight real anchors out of `Sources/AtriumSurface/DayCurve.swift`
  and the seven-step density ramp out of `LatticeRenderer.swift`; feeding the
  curve's hue and lightness through the ramp reproduces the published
  `density-0..6` hexes exactly at the resting point, which is the check that
  this is Atrium's palette and not a palette that looks like it.
* **the work** -- the five real lanes of `data/field.json` (Atrium's surface,
  host and design repositories, `blueband-concept`, `Finance-Tracker`) built
  up a week at a time across the same 53 weeks, with each lane's running
  total counting as it goes.

Keeping them small
------------------
A GIF of a field that changes everywhere every frame costs megabytes, because
there is nothing to delta. Two of the three plates hold the field still and
move one line or one row through it, which is what makes them ~100-200 KB.
`the day` cannot do that -- recolouring is the point, so every dot changes --
so it is the shortest plate, the coarsest screen and the fewest frames, and it
is the one whose size has to be watched.

Type inside a moving image
--------------------------
`bin/directions.py` holds every drawn word to 11px as it renders in GitHub's
358px phone column. These plates are 980 units wide, the width of the desktop
column, so the same floor is 30.1 units here. `_text` refuses to draw below
it rather than leaving it to a screenshot to notice.
"""
from __future__ import annotations

import colorsys
import json
from io import BytesIO
from pathlib import Path

from . import svg

ROOT = Path(__file__).resolve().parent.parent
LATTICE_PNG = ROOT / "showroom" / "atrium-lattice.png"
CONTRIB_JSON = ROOT / "data" / "contributions.json"
FIELD_JSON = ROOT / "data" / "field.json"
TOKENS_JSON = ROOT / "data" / "atrium-tokens.json"

# The desktop profile column: GitHub's 1012px page less its 2x16px padding.
# Matching it exactly is what stops a raster plate sitting narrower than the
# SVG plates around it, which is the single most obvious way a page of mixed
# assets reads as assembled rather than designed.
WIDTH = 980
PHONE_COLUMN = 358
MIN_APPARENT_PX = 11.0
FLOOR = MIN_APPARENT_PX * WIDTH / PHONE_COLUMN   # 30.1 units

# Raster plates cannot inherit `currentColor`, so they bake what the SVG
# plates inherit. Taken from the token module rather than typed, so the two
# paths cannot drift apart: that drift is invisible to `conformance.py`, which
# reads hex literals and never saw these tuples.
GROUND = svg.rgb(svg.GROUND_DARK)
INK = svg.rgb(svg.token(svg.INK_DARK))
DIM = svg.rgb(svg.over(svg.token(svg.INK_DARK), svg.GROUND_DARK, svg.DIM_ALPHA))
ACCENT = svg.rgb(svg.ACCENT_LINK)      # the link blue Thomas kept on 19 Sep

MONO = "/System/Library/Fonts/Menlo.ttc"
REGULAR, BOLD = 0, 1

# Measured, not chosen. The earlier crop was searched for the highest mean
# ink at the lowest spread and gave a field whose right tenth fell under the
# ink gate and photographed as an unfinished edge. This one is searched for
# *coverage* instead -- the most vertical twelfths whose mean ink clears 0.12,
# tie-broken on mean and spread -- and is the only window of any size tried
# that fills all twelve: mean 0.369, spread 0.071 across them.
CROP = (1080, 800, 1530, 940)

# Below this a cell is ground rather than a mark. It is the one number that
# decides how far the field reaches: at 0.06 the crop's faintest twelfth fell
# out entirely and the plate photographed with an unfinished right edge.
INK_GATE = 0.04


# --- drawing -----------------------------------------------------------------

def _font(size: float, bold: bool = False):
    from PIL import ImageFont
    return ImageFont.truetype(MONO, int(round(size)),
                              index=BOLD if bold else REGULAR)


def _text(d, x: float, y: float, s: str, size: float, fill, *,
          bold: bool = False, tracking: float = 0.0, where: str = "") -> float:
    """One tracked monospaced string, top-left anchored. Returns its width.

    Tracking is drawn character by character because Pillow has no
    `letter-spacing`, and the tracked capitals are the whole reason these
    plates read as instrument chrome rather than as captions.
    """
    if size < FLOOR:
        raise ValueError(
            f"{where or s!r}: {size:.1f} units is {size * PHONE_COLUMN / WIDTH:.1f}px "
            f"in a {PHONE_COLUMN}px phone column, under the {MIN_APPARENT_PX:g}px floor")
    font = _font(size, bold)
    advance = font.getlength("0") + size * tracking
    for i, ch in enumerate(s):
        d.text((x + i * advance, y), ch, font=font, fill=fill)
    return len(s) * advance


def _width_of(s: str, size: float, tracking: float = 0.0) -> float:
    return len(s) * (_font(size).getlength("0") + size * tracking)


def _hairline(d, x0, y0, x1, y1, fill, w=2):
    d.line([x0, y0, x1, y1], fill=fill, width=w)


def _mix(a, b, t: float):
    return tuple(int(round(a[k] + t * (b[k] - a[k]))) for k in range(3))


# --- the real lattice, as a dot screen ---------------------------------------

def _screen(np, Image, cols: int, height: int):
    """The measured crop reduced to a `cols`-wide dot screen.

    Rendering the crop pixel for pixel photographs as television static: 85%
    of that region is above mid-grey, so it comes back a uniform light
    rectangle with no structure in it. Letting dot *area* carry darkness, the
    way a halftone does, brings the structure back and keeps the ground ground.
    Returns the per-cell ink in 0..1 and the geometry the caller draws with.
    """
    src = Image.open(LATTICE_PNG).convert("L").crop(CROP)
    rows = max(1, round(cols * (height / WIDTH)))
    small = src.resize((cols, rows), Image.BOX)
    ink = 255 - np.asarray(small).astype(float)
    ink = np.clip((ink - 128) / 127, 0, 1) ** 1.25
    px, py = WIDTH / cols, height / rows
    return ink, (cols, rows, px, py, min(px, py) * 0.62)


def _paint_screen(d, ink, geom, top: float, tone, ground=GROUND):
    cols, rows, px, py, rmax = geom
    for j in range(rows):
        for i in range(cols):
            v = float(ink[j, i])
            if v < INK_GATE:
                continue
            r = rmax * v ** 0.55
            cx, cy = (i + 0.5) * px, top + (j + 0.5) * py
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tone(v))


def _ink_tone(v: float, colour=INK):
    return _mix(GROUND, colour, min(1.0, 0.22 + 0.78 * v))


# --- real data ---------------------------------------------------------------

def weeks() -> list[dict]:
    """The 53 real weeks, oldest first, each with its start date and count."""
    doc = json.loads(FIELD_JSON.read_text(encoding="utf-8"))
    return doc["weeks"]


def lanes() -> list[tuple[str, str, list[int], int, int]]:
    """Every real lane in `data/field.json`: (region, lane, weekly, commits, files)."""
    doc = json.loads(FIELD_JSON.read_text(encoding="utf-8"))
    out = []
    for region, body in doc["regions"].items():
        for lane in body["lanes"]:
            out.append((region, lane["name"], lane["commits"],
                        lane["total"], lane["files"]))
    return out


def day_curve() -> dict:
    return json.loads(TOKENS_JSON.read_text(encoding="utf-8"))


def _at_hour(curve: dict, hour: float) -> tuple[float, float]:
    """The DayCurve's hue and lightness at any hour, between its anchors."""
    anchors = curve["day_curve"]["anchors"]
    for a, b in zip(anchors, anchors[1:]):
        if a["hour"] <= hour <= b["hour"]:
            span = b["hour"] - a["hour"] or 1.0
            t = (hour - a["hour"]) / span
            return (a["hue_deg"] + t * (b["hue_deg"] - a["hue_deg"]),
                    a["lightness"] + t * (b["lightness"] - a["lightness"]))
    last = anchors[-1]
    return last["hue_deg"], last["lightness"]


def ramp_at(curve: dict, hue_deg: float) -> list[tuple[int, int, int]]:
    """Atrium's seven density colours at a given hue.

    Checked against the published tokens: at the resting point's hue this
    returns `#080302 #450d0a #78140f #b81d14 #e84552 #f6eaec #ffffff`, which
    is `density-0..6` in `data/atrium-tokens.json` exactly.
    """
    out = []
    for step in curve["density_ramp"]["steps"]:
        h = ((hue_deg + step["d_hue_deg"]) % 360) / 360.0
        r, g, b = colorsys.hls_to_rgb(h, step["lightness"], step["saturation"])
        out.append((round(r * 255), round(g * 255), round(b * 255)))
    return out


def ground_at(curve: dict, hue_deg: float, lightness: float):
    r, g, b = colorsys.hls_to_rgb((hue_deg % 360) / 360.0, lightness, 0.37)
    return (round(r * 255), round(g * 255), round(b * 255))


# --- encoding ----------------------------------------------------------------

def encode(frames, fps: int, colours: int = 64) -> tuple[bytes, str, dict]:
    """The animation as the smaller of GIF and APNG, with both sizes reported.

    One shared palette and `disposal=1` are what make a GIF of this kind
    ~170KB instead of 5.8MB: quantising each frame on its own gives every
    frame a different palette, which forces a full frame into the file each
    time, while sharing one lets the encoder store only the rectangle that
    changed. The palette is built from a strip sampled across the whole run,
    not from frame zero, because `the day` ends on colours frame zero has
    never seen.
    """
    from PIL import Image

    step = max(1, len(frames) // 12)
    sample = frames[::step]
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, i * frames[0].height))
    pal = strip.convert("P", palette=Image.ADAPTIVE, colors=colours)

    gif = BytesIO()
    quantised = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    quantised[0].save(gif, format="GIF", save_all=True,
                      append_images=quantised[1:], duration=int(1000 / fps),
                      loop=0, optimize=True, disposal=1)

    png = BytesIO()
    frames[0].save(png, format="PNG", save_all=True, append_images=frames[1:],
                   duration=int(1000 / fps), loop=0, optimize=True)

    sizes = {"gif": gif.tell(), "apng": png.tell()}
    if sizes["gif"] <= sizes["apng"]:
        return gif.getvalue(), "gif", sizes
    return png.getvalue(), "png", sizes


def _png(frame) -> bytes:
    buf = BytesIO()
    frame.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# --- plate chrome ------------------------------------------------------------

LABEL = 31.0          # 11.3px in a 358px phone column
FOOT_TRACK = 0.05     # see `_foot`: .08 overruns `CONTRIBUTIONS` by nine units
VALUE = 41.0
PAD = 34
TOP = 104.0           # where the chrome band ends and a field may start


def _chrome(d, title: str, right: str, height: float, dense: bool) -> None:
    """The lockup and the top-right readout every plate carries.

    Drawn per frame rather than once onto the base, because on two of the
    three plates the top-right readout is the thing that moves -- the week
    being swept, the hour being painted. It is the only number on the plate a
    reader can use to check that what they are watching is real.

    `dense` is the one axis the two finished variations differ on. Quiet draws
    the lockup and nothing else; dense adds the corner ticks and the accent
    rule under it, which is GMUNK's `interface.029` frame and the reason that
    plate reads as an instrument rather than as a picture.
    """
    _text(d, PAD, PAD - 6, title, LABEL, INK, bold=True, tracking=0.16,
          where="plate title")
    if right:
        w = _width_of(right, LABEL, 0.10)
        room = WIDTH - 2 * PAD - _width_of(title, LABEL, 0.16) - 24
        if w > room:
            raise ValueError(
                f"plate readout: {right!r} is {w:.0f} units wide beside "
                f"{title!r} and there are {room:.0f}")
        _text(d, WIDTH - PAD - w, PAD - 6, right, LABEL, DIM, tracking=0.10,
              where="plate readout")
    if dense:
        _hairline(d, PAD, PAD + LABEL + 12, PAD + 196, PAD + LABEL + 12, ACCENT, 3)
        for x in (PAD - 12, WIDTH - PAD + 12):
            for y in (PAD - 18, height - PAD + 18):
                _hairline(d, x - 9, y, x + 9, y, DIM, 2)
                _hairline(d, x, y - 9, x, y + 9, DIM, 2)


def _foot(d, items: list[tuple[str, str]], baseline: float, dense: bool) -> None:
    """Three horizontal readouts along the foot, never more.

    A slot is (980-68)/n units and a label costs 18.6 units per character at
    the floor plus its tracking, so four slots give 194 units of room for
    `CONTRIBUTIONS`, which needs 242 -- the first instrument stills read
    `CONTRIBUTIOИDAYS`. Three slots give 270, and the label tracking is .05
    rather than the .08 the chrome uses because .08 costs 279 and overruns by
    nine units. This is arithmetic, not taste, which is why `_foot` raises
    with the measurement rather than trusting a screenshot to catch it.
    """
    step = (WIDTH - 2 * PAD) / len(items)
    for i, (label, value) in enumerate(items):
        x = PAD + i * step
        room = step - 34
        for text, size, track in ((label, LABEL, FOOT_TRACK), (value, VALUE, 0.0)):
            if _width_of(text, size, track) > room:
                raise ValueError(
                    f"foot {i}: {text!r} is {_width_of(text, size, track):.0f} "
                    f"units wide and there are {room:.0f}")
        if dense:
            _hairline(d, x, baseline - VALUE - LABEL - 16, x,
                      baseline + VALUE * 0.2, _mix(GROUND, INK, 0.30), 2)
        _text(d, x + 16, baseline - VALUE - LABEL - 10, label, LABEL, DIM,
              tracking=FOOT_TRACK, where=f"foot label {i}")
        _text(d, x + 16, baseline - VALUE - 2, value, VALUE, INK, bold=True,
              where=f"foot value {i}")


# The height a foot rail needs under whatever slot ends above it: the value's
# baseline sits 8 units off the bottom and the label sits a value and a label
# above that, with air. Written down once so three plates cannot disagree.
FOOT_BAND = 150


# --- plate one: the year -----------------------------------------------------

YEAR_FIELD = 168
YEAR_GAP = 16
YEAR_STRIP = 104
YEAR_BASE = TOP + YEAR_FIELD + YEAR_GAP + YEAR_STRIP
YEAR_FPS = 13

YEAR_ALT = ("One real region of the Atrium lattice frame, reduced to a dot "
            "screen, with the year's 53 real weekly contribution counts drawn "
            "beneath it and a line sweeping through the field and the counts "
            "together, one week at a time")


def _year_frames(dense: bool):
    import numpy as np
    from PIL import Image, ImageDraw

    wk = weeks()
    counts = [w["count"] for w in wk]
    peak = max(counts) or 1
    height = int(YEAR_BASE + (FOOT_BAND if dense else 44))
    ink, geom = _screen(np, Image, 124, YEAR_FIELD)

    base = Image.new("RGB", (WIDTH, height), GROUND)
    d = ImageDraw.Draw(base)
    _paint_screen(d, ink, geom, TOP, _ink_tone)
    # A wash over the field so type sits on ground and not on marks. The marks
    # are texture and may go under it; the words may not go under them.
    base = Image.blend(base, Image.new("RGB", (WIDTH, height), GROUND),
                       0.42 if dense else 0.52)
    d = ImageDraw.Draw(base)
    if dense:
        # Not `CONTRIBUTIONS` and not `WEEKS ACTIVE`: the masthead already
        # sets both, and a page that prints the same number twice inside one
        # screen is the clump this round exists to remove. These three are
        # facts the page does not otherwise carry.
        best = max(range(len(counts)), key=counts.__getitem__)
        first = next(w["start"] for w in wk if w["count"])
        _foot(d, [("BUSIEST WEEK", f"{peak}"),
                  ("ITS WEEK", wk[best]["start"]),
                  ("FIRST WEEK", first)], height - 8, dense)

    step = (WIDTH - 2 * PAD) / len(counts)
    frames = []
    for i in range(len(counts)):
        im = base.copy()
        dd = ImageDraw.Draw(im)
        _chrome(dd, "THE YEAR",
                f"{wk[i]['start']} · WEEK {i + 1:02d}/53 · {counts[i]:>3}",
                height, dense)
        for j, count in enumerate(counts):
            x = PAD + j * step
            h = 4 + (count / peak) ** 0.5 * (YEAR_STRIP - 26)
            near = abs(j - i)
            colour = ACCENT if near == 0 else INK
            alpha = 1.0 if near == 0 else (0.58 if near < 3 else 0.30)
            dd.rectangle([x, YEAR_BASE - h, x + step - 3.6, YEAR_BASE],
                         fill=_mix(GROUND, colour, alpha))
        x = PAD + i * step + (step - 3.6) / 2
        # The sweep lights the field column it passes through, not only the
        # week beneath it. That is the claim of the image -- the record and
        # the scene are the same object -- and a line travelling over the
        # field without touching it says the opposite.
        cols, rows, px, py, rmax = geom
        for ci in range(max(0, int((x - 15) / px)),
                        min(cols, int((x + 15) / px) + 1)):
            for rj in range(rows):
                v = float(ink[rj, ci])
                if v < INK_GATE:
                    continue
                r = rmax * v ** 0.55
                cx, cy = (ci + 0.5) * px, TOP + (rj + 0.5) * py
                dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
        dd.line([x, TOP - 14, x, YEAR_BASE + 10], fill=ACCENT, width=2)
        frames.append(im)
    return frames


# --- plate two: the day ------------------------------------------------------

DAY_FIELD = 150
DAY_FPS = 6

DAY_ALT = ("The same region of the Atrium lattice repainted once an hour in "
           "Atrium's own colours, following the eight real anchors of its "
           "DayCurve through a full day: the hue and the lightness of the "
           "ground and of all seven density steps move with the hour")


def _day_frames(dense: bool):
    import numpy as np
    from PIL import Image, ImageDraw

    curve = day_curve()
    # Coarser than the other two plates on purpose. Recolouring is the point
    # here, so every dot changes in every frame and there is nothing to delta;
    # this is the one plate whose size is set by how much of it moves.
    ink, geom = _screen(np, Image, 92, DAY_FIELD)
    cols, rows, px, py, rmax = geom
    swatch_y = TOP + DAY_FIELD + 22
    swatch_h = 46 if dense else 32
    height = int(swatch_y + swatch_h + (74 if dense else 30))

    frames = []
    for hour in range(24):
        hue, light = _at_hour(curve, float(hour))
        ramp = ramp_at(curve, hue)
        im = Image.new("RGB", (WIDTH, height), GROUND)
        d = ImageDraw.Draw(im)
        d.rectangle([0, TOP - 16, WIDTH, TOP + DAY_FIELD + 4],
                    fill=ground_at(curve, hue, light * 0.42))
        for j in range(rows):
            for i in range(cols):
                v = float(ink[j, i])
                if v < INK_GATE:
                    continue
                r = rmax * v ** 0.55
                cx, cy = (i + 0.5) * px, TOP + (j + 0.5) * py
                # The ramp is a seven-step spec, so a mark takes the step its
                # own density falls in rather than a blend of two -- that is
                # how LatticeRenderer bands it, and why the field looks banded
                # in Atrium and banded here.
                d.ellipse([cx - r, cy - r, cx + r, cy + r],
                          fill=ramp[min(6, int(v * 6.999))])
        _chrome(d, "THE DAY", f"{hour:02d}:00 · HUE {hue:+.1f}° · L {light:.3f}",
                height, dense)
        sw = (WIDTH - 2 * PAD) / 7
        for k, colour in enumerate(ramp):
            d.rectangle([PAD + k * sw, swatch_y, PAD + (k + 1) * sw - 6,
                         swatch_y + swatch_h], fill=colour)
        if dense:
            _text(d, PAD, swatch_y + swatch_h + 14,
                  "DENSITY 0 → 6 · LatticeRenderer.swift", LABEL, DIM,
                  tracking=0.06, where="day ramp caption")
        # The hour hand: a day is a line across the plate, and the plate is
        # one day long.
        x = PAD + (hour / 23.0) * (WIDTH - 2 * PAD)
        d.line([x, TOP - 16, x, TOP + DAY_FIELD + 4], fill=INK, width=2)
        frames.append(im)
    return frames


# --- plate three: the work ---------------------------------------------------

WORK_NAME_COL = 470       # see `_work_frames`: the longest lane name is 328
WORK_FPS = 13

WORK_ALT = ("The five real lanes of work behind this profile -- Atrium's "
            "surface, host and design repositories, blueband-concept and "
            "Finance-Tracker -- built up one week at a time across the same "
            "53 weeks, each lane's running commit total counting as it goes")


def _work_frames(dense: bool):
    from PIL import Image, ImageDraw

    rows = lanes()
    wk = weeks()
    row_h = 56.0 if dense else 62.0
    height = int(TOP + 12 + row_h * len(rows) + 60
                 + (FOOT_BAND if dense else 24))
    peak = max(max(r[2]) for r in rows) or 1
    step = (WIDTH - PAD - WORK_NAME_COL) / len(wk)

    frames = []
    for i in range(len(wk)):
        im = Image.new("RGB", (WIDTH, height), GROUND)
        d = ImageDraw.Draw(im)
        _chrome(d, "THE WORK", f"WEEK {i + 1:02d} / 53 · {wk[i]['start']}",
                height, dense)
        for k, (region, lane, weekly, total, files) in enumerate(rows):
            y = TOP + 12 + k * row_h
            name = (lane if lane == region else f"{region}/{lane}").upper()
            _text(d, PAD, y, name, LABEL, DIM, tracking=0.06, where=f"lane {k}")
            run = f"{sum(weekly[:i + 1]):>4}"
            _text(d, WORK_NAME_COL - _width_of(run, LABEL) - 30, y, run, LABEL,
                  ACCENT if weekly[i] else _mix(GROUND, INK, 0.55),
                  bold=True, where=f"lane total {k}")
            # A zero week is a week with no commits in it, not a week with no
            # data. Without the rule under the whole span, four of the five
            # lanes read as a bar chart missing its left-hand side; with it
            # they read as what they are, which is work that started late.
            _hairline(d, WORK_NAME_COL, y + row_h - 12, WIDTH - PAD,
                      y + row_h - 12, _mix(GROUND, INK, 0.22), 1)
            for j in range(i + 1):
                if not weekly[j]:
                    continue
                x = WORK_NAME_COL + j * step
                h = 6 + (weekly[j] / peak) ** 0.5 * (row_h - 24)
                colour = ACCENT if j == i else INK
                alpha = 1.0 if j == i else 0.46
                d.rectangle([x, y + row_h - 13 - h, x + step - 2.2,
                             y + row_h - 13], fill=_mix(GROUND, colour, alpha))
        axis_y = TOP + 12 + row_h * len(rows) + 6
        # The axis carries its two ends rather than a tick per week: 53 ticks
        # at this width is 9 units apart, which is a texture, and the two
        # dates are the only thing a reader needs to know the span is a year.
        _hairline(d, WORK_NAME_COL, axis_y, WIDTH - PAD, axis_y,
                  _mix(GROUND, INK, 0.30), 2)
        _text(d, WORK_NAME_COL, axis_y + 12, wk[0]["start"], LABEL, DIM,
              tracking=0.04, where="work axis start")
        end = wk[-1]["start"]
        _text(d, WIDTH - PAD - _width_of(end, LABEL, 0.04), axis_y + 12, end,
              LABEL, DIM, tracking=0.04, where="work axis end")
        if dense:
            done = sum(sum(r[2][:i + 1]) for r in rows)
            _foot(d, [("COMMITS", f"{done:,}"), ("LANES", f"{len(rows)}"),
                      ("FILES TOUCHED", f"{sum(r[4] for r in rows):,}")],
                  height - 8, dense)
        else:
            x = WORK_NAME_COL + i * step
            d.line([x, TOP - 6, x, TOP + 12 + row_h * len(rows) - 6],
                   fill=_mix(GROUND, ACCENT, 0.60), width=2)
        frames.append(im)
    return frames


# --- the three, built --------------------------------------------------------

# The last element is which frame becomes the `prefers-reduced-motion` still.
# For two of the three that is the last frame, because frame zero of each is
# an empty instrument -- one week lit, nothing built -- and a reader who asked
# for no motion should be handed the finished readout rather than the moment
# before it starts. `the day` has no finished state: its last frame is 23:00,
# the darkest hour on the curve, so its still is the brightest instead, which
# is the hour the DayCurve's own lightness range peaks at.
BRIGHTEST_HOUR = 13          # lightness 0.195, the top of `lightness_range`

PLATES = {
    "year": (_year_frames, YEAR_FPS, YEAR_ALT, 64, -1),
    "day": (_day_frames, DAY_FPS, DAY_ALT, 96, BRIGHTEST_HOUR),
    "work": (_work_frames, WORK_FPS, WORK_ALT, 48, -1),
}


def build(name: str, dense: bool) -> dict:
    """One plate: the animation, a still for `prefers-reduced-motion`, sizes."""
    frames_of, fps, alt, colours, still_at = PLATES[name]
    frames = frames_of(dense)
    data, ext, sizes = encode(frames, fps, colours)
    return {"data": data, "ext": ext, "sizes": sizes, "alt": alt,
            "still": _png(frames[still_at]), "still_at": still_at,
            "frames": len(frames), "fps": fps, "seconds": len(frames) / fps}


if __name__ == "__main__":
    out = ROOT / "preview"
    out.mkdir(exist_ok=True)
    for plate in PLATES:
        for dense in (False, True):
            got = build(plate, dense)
            tag = "dense" if dense else "quiet"
            (out / f"{plate}-{tag}.{got['ext']}").write_bytes(got["data"])
            print(f"{plate:5} {tag:5} {got['ext']:4} "
                  f"{len(got['data']) / 1024:7.1f} KB  "
                  f"gif {got['sizes']['gif'] / 1024:7.1f}  "
                  f"apng {got['sizes']['apng'] / 1024:8.1f}  "
                  f"{got['frames']} frames, {got['seconds']:.1f}s")
