"""The instrument direction, finished: two variations of one page, both moving.

`generators/bold.py` built `instrument` as a sketch -- two plates and a
heading list, enough to judge the idea against two others. Thomas picked it
and said the page was still "severely under-made", and that he could see no
animation at all. Both are true of the sketch: it drew two plates on a page
whose other five sections were bare headings, and its one moving asset
belonged to a different direction.

So this module builds the same idea out. Every section carries something
real; the three animated plates in `generators/animate.py` carry the three
kinds of time this profile actually has -- a year of the record, a day of
Atrium's own light, and the five lanes the work was done in; and the static
plates are cut from the same lattice frame at the same pitch, so the field
appears to continue behind the words between them.

Two variations, one axis
------------------------
`quiet` and `dense` differ in how much chrome a plate carries and how many
plates the page has, and in nothing else. Both lead with Atrium, both hold
BlueBand at the same weight as Numeris, both keep the blue links and the dark
ground, and both set the same sentences. Choosing between them is choosing how
loud the instrument is, which is the only question the last round left open.

The type floor
--------------
`tests/test_build.py` holds every text element to 3.07% of its plate's own
viewBox and `bin/directions.py` to 11px apparent in GitHub's 358px phone
column; 3.07% of 1200 reads at 10.98px, so the two disagree by two hundredths
of a pixel. Everything here is set at or above 3.17%, which clears both, and
`_fits` refuses to draw a string wider than the room it has.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import svg
from . import animate, content
from .directions import _sha7, _url, grid
from .github import summarise
from .svg import lattice

ROOT = Path(__file__).resolve().parent.parent
CONTRIB_JSON = ROOT / "data" / "contributions.json"
FIELD_JSON = ROOT / "data" / "field.json"

VARIATIONS = ("quiet", "dense")

VIEW_W = 1200
MONO = lattice.MONO
# All four come from the token module, so this file carries no colour of its
# own. `conformance.py` reads literals, and a literal here is drift by
# definition: see `svg/__init__.py` for why dim is an alpha and why the link
# blue is the one exception.
GROUND = svg.GROUND_DARK
INK = svg.token(svg.INK_DARK)
DIM = svg.over(INK, GROUND, svg.DIM_ALPHA)
ACCENT = svg.ACCENT_LINK

# The raster plates are 980 units wide because that is GitHub's desktop
# column. These are 1200 and are scaled down to the same 980 by the column
# itself, so every measurement here is the raster one times 1200/980 -- which
# is what makes an SVG plate and a GIF plate look like the same instrument
# rather than two assets that happen to be stacked.
SCALE = VIEW_W / animate.WIDTH
PAD = animate.PAD * SCALE          # 41.6
LABEL = animate.LABEL * SCALE      # 38.0 -> 11.3px on a phone
VALUE = animate.VALUE * SCALE      # 50.2
LEDE = 132.0                       # 39.4px on a phone

ADVANCE = 0.60   # a monospaced advance, in every font in this repo's stack


def _fits(text: str, size: float, tracking: float, room: float,
          where: str) -> str:
    """Refuse a string wider than its slot, with the overflow measured.

    `letter-spacing` adds its tracking after every character including the
    last, so this is arithmetic. Written by eye it is not: the first
    instrument stills read `CONTRIBUTIOИDAYS ACTIVE` and `LINES OF
    SWIFTASSERTIONS`, and a caption cut at `2026-0`.
    """
    width = len(text) * size * (ADVANCE + tracking)
    if width > room:
        raise ValueError(
            f"{where}: {text!r} is {width:.0f} units wide at {size:.1f}px "
            f"with {tracking:g}em tracking, and there are {room:.0f}")
    return text


def _open(view_h: float, aria: str) -> list[str]:
    """Every asset paints the canvas first -- see the Makefile's note on -b."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} '
        f'{view_h:.0f}" width="{VIEW_W}" height="{view_h:.0f}" role="img" '
        f'aria-label="{aria}">\n',
        f'  <rect width="{VIEW_W}" height="{view_h:.0f}" fill="{GROUND}"/>\n',
    ]


def _type(x: float, y: float, s: str, size: float, fill: str,
          weight: int = 500, tracking: float = 0.0, anchor: str = "") -> str:
    a = f' text-anchor="{anchor}"' if anchor else ""
    track = f"; letter-spacing: {tracking:g}em" if tracking else ""
    return (f'  <text x="{x:.0f}" y="{y:.0f}" fill="{fill}"{a} style="font: '
            f'{weight} {size:.1f}px {MONO}{track}">{s}</text>\n')


# --- the plate -------------------------------------------------------------

def plate(g: dict, row0: int, rows: int, *, title: str, right: str,
          lede: tuple[str, str] | None, foot: list[tuple[str, str]],
          dense: bool, aria: str) -> str:
    """One static plate, in the same frame the animated ones use.

    A lockup top left, a readout top right, an optional dominant numeral, and
    three readouts along the foot. The first instrument pass put the numbers
    in two vertical rails either side of the field, which is what GMUNK's
    `interface.022` does; it does not survive the type floor, because a rail
    wide enough for `CONTRIBUTIONS` leaves 408 units of field between the two
    and the name needs 680. `interface.029` is the frame that does survive,
    because its rails are horizontal, and a 1200-unit plate has room across.
    """
    sl = lattice.band(g, row0, rows)
    marks, field_h = lattice._marks(sl, INK)
    top = 112.0
    foot_band = 168.0 if foot else 40.0
    view_h = top + field_h + 22 + foot_band

    body = _open(view_h, aria)
    body.append(f'  <g transform="translate(0 {top:.0f})">\n')
    body.extend(marks)
    body.append("  </g>\n")
    # A wash over the field so type sits on ground rather than on marks. The
    # marks are texture and may go under it; the words may not go under them.
    body.append(f'  <rect y="{top - 20:.0f}" width="{VIEW_W}" '
                f'height="{field_h + 44:.0f}" fill="{GROUND}" '
                f'fill-opacity="{0.42 if dense else 0.54:g}"/>\n')

    _fits(title, LABEL, 0.16, VIEW_W * 0.48, "plate title")
    body.append(_type(PAD, PAD + LABEL * 0.86, title, LABEL, INK, 700, 0.16))
    if right:
        # The room is what the title actually leaves, not a fixed fraction.
        # A fixed 42% reserved 504 units for a lockup that needs 404 and then
        # rejected a readout that fits, which is a check being wrong in the
        # safe direction -- still wrong.
        title_w = len(title) * LABEL * (ADVANCE + 0.16)
        _fits(right, LABEL, 0.10, VIEW_W - 2 * PAD - title_w - 24,
              "plate readout")
        body.append(_type(VIEW_W - PAD, PAD + LABEL * 0.86, right, LABEL, DIM,
                          500, 0.10, anchor="end"))
    if dense:
        body.append(f'  <path d="M{PAD:.0f} {PAD + LABEL + 14:.0f}h240" '
                    f'stroke="{ACCENT}" stroke-width="4"/>\n')
        for x in (PAD - 15, VIEW_W - PAD + 15):
            for y in (PAD - 22, view_h - PAD + 22):
                body.append(f'  <path d="M{x - 11:.0f} {y:.0f}h22M{x:.0f} '
                            f'{y - 11:.0f}v22" stroke="{DIM}" '
                            'stroke-width="2"/>\n')

    if lede:
        number, caption = lede
        _fits(number, LEDE, 0.0, VIEW_W - 2 * PAD, "lede")
        _fits(caption, LABEL, 0.10, VIEW_W - 2 * PAD, "lede caption")
        y = top + field_h * 0.62
        body.append(_type(PAD, y, number, LEDE, ACCENT, 700))
        body.append(_type(PAD, y + LABEL * 1.5, caption, LABEL, DIM, 500, 0.10))

    if foot:
        base = view_h - 44
        step = (VIEW_W - 2 * PAD) / len(foot)
        for i, (label, value) in enumerate(foot):
            x = PAD + i * step
            _fits(label, LABEL, 0.05, step - 40, f"foot label {i}")
            _fits(value, VALUE, 0.0, step - 40, f"foot value {i}")
            if dense:
                body.append(
                    f'  <path d="M{x:.0f} {base - VALUE - LABEL - 20:.0f}'
                    f'v{VALUE + LABEL + 30:.0f}" stroke="{INK}" '
                    'stroke-opacity="0.30" stroke-width="2"/>\n')
            body.append(_type(x + 20, base - VALUE - 12, label, LABEL, DIM,
                              500, 0.05))
            body.append(_type(x + 20, base, value, VALUE, INK, 600))
    body.append("</svg>\n")
    return "".join(body)


# --- what the page says ----------------------------------------------------

# Every line on the page, in one place, so the two variations cannot drift
# into saying different things. They differ in how much chrome they draw, not
# in what they claim.
STANDFIRST = ("**Design Engineering, Imperial College London.** I build "
              "hardware and the software that runs it.")
ATRIUM_LEDE = ("A spatial desktop for macOS, in Swift and Metal. It draws the "
               "machine's own record as a navigable field: every mark a real "
               "event, depth is recency.")
ATRIUM_COST = ("The acceptance harness has never passed — **11 criteria, all "
               "UNMEASURED**. Engineering depth, not delivery. Private repo.")
BLUEBAND = ("A wearable motion band — enclosure, board, firmware and app, one "
            "person doing the whole chain.")
NUMERIS = ("Plaid in, market data alongside it, normalised into Postgres, out "
           "through a typed API. Used daily, which is what makes it real.")
BLUEBAND_REPO = "[`blueband-concept`](https://github.com/thomasvanpul/blueband-concept)"
NUMERIS_REPO = "[`Finance-Tracker`](https://github.com/thomasvanpul/Finance-Tracker)"
ALSO = ("**Interstellar Sanctuary** a Malaysia property launch map, "
        "[password-gated](https://interstellarsanctuary.com) &nbsp;·&nbsp; "
        "**HFQ forming** with Dr Nan Li at the Dyson School &nbsp;·&nbsp; "
        "**Air defence economics** a self-directed paper &nbsp;·&nbsp; "
        "**IRIS** an always-on assistant daemon")
STACK = ("Python · TypeScript · React · Node · PostgreSQL &nbsp;·&nbsp; "
         "Fusion 360 · Ansys · SimScale · KiCad &nbsp;·&nbsp; TIG welding · "
         "FDM printing · composite layup")
FOOTER = f"<sub>{content.FOOTER_SUB}</sub>\n\n{content.FOOTER_LINKS}\n"

ATRIUM_TABLE = [
    ("Swift", "18,470 lines across 75 files"),
    ("Tests", "418 assertions, 38% of the code"),
    ("Events", "218,016 from 31 repositories"),
    ("Runtime", "10 MB resident, 0% idle CPU"),
    ("Interface", "3 of 19 designed elements built"),
]

# Slicing one grid rather than re-cropping is the whole mechanism: two plates
# cut at the same pitch have the same columns in the same places, so the field
# reads as continuing behind the words between them.
#
# Which rows, though, is a density question and not a page-order one. Measured
# over the 107-row grid in tens, mean ink runs 2.05 at the top to 5.40 at rows
# 80-90: the frame is genuinely much emptier at its upper left. The first pass
# gave the masthead rows 0-34 and it photographed as a name floating over
# nothing. So the page reads down the frame's density rather than down its
# rows -- masthead from the densest band, the two small plates from the middle
# -- and what the plates share is the pitch, which is what the eye reads.
MASTHEAD_ROWS = 22
MASTHEAD_AT = 68
SMALL_ROWS = 12
SMALL_AT = {"blueband": 52, "numeris": 38}


def _table(rows, head) -> str:
    out = [f"| {head[0]} | {head[1]} |", "| --- | --- |"]
    out.extend(f"| {a} | {b} |" for a, b in rows)
    return "\n".join(out)


def _picture(anim: str, still: str, alt: str) -> str:
    """The animation, with a still for a reader who asked for no motion.

    `prefers-reduced-motion` is the only one of these the page can honour,
    because GitHub strips script and CSS. A `<picture>` with a `source` on the
    media query is the whole mechanism, and it is the same one the live page
    already uses for the hero.
    """
    return "\n".join([
        "<picture>",
        f'  <source media="(prefers-reduced-motion: reduce)" srcset="{still}">',
        f'  <img alt="{alt}" src="{anim}">',
        "</picture>",
    ])


def _readme(f: dict, dense: bool) -> str:
    def img(key: str, alt: str) -> str:
        return f'<img alt="{alt}" src="{_url(f[key])}">'

    out = [
        img("masthead", "Thomas van Pul, Design Engineering at Imperial "
                        "College London, set in a region of the Atrium "
                        "lattice with 2,774 contributions, 15 of 53 weeks "
                        "active and a longest run of 45 days along its foot"),
        "",
        STANDFIRST,
        "",
        "### Atrium",
        "",
        _picture(_url(f["day"]), _url(f["day-still"]), animate.DAY_ALT),
        "",
        ATRIUM_LEDE,
        "",
        _table(ATRIUM_TABLE if dense else ATRIUM_TABLE[:3],
               ("Atrium", "measured 2026-09-16")),
        "",
        _picture(_url(f["year"]), _url(f["year-still"]), animate.YEAR_ALT),
        "",
        ATRIUM_COST,
        "",
    ]
    out += [] if dense else ["### BlueBand", ""]
    if dense:
        out += [img("blueband", "BlueBand, measured: 13 commits across 11 "
                                "files in one week of the last year"), ""]
    out += [f"{BLUEBAND} {BLUEBAND_REPO}", ""]
    out += [] if dense else ["### Numeris", ""]
    if dense:
        out += [img("numeris", "Numeris, measured: 712 commits across 1,062 "
                               "files in 12 weeks of the last year"), ""]
    out += [
        f"{NUMERIS} {NUMERIS_REPO}",
        "",
        "### The work behind all three",
        "",
        _picture(_url(f["work"]), _url(f["work-still"]), animate.WORK_ALT),
        "",
        "### Also running",
        "",
        ALSO,
        "",
        "### Stack",
        "",
        STACK,
        "",
        FOOTER,
    ]
    return "\n".join(out)


# --- build -----------------------------------------------------------------

def build(variation: str, out_dir: Path) -> dict:
    """Write one variation's assets and README, and report what it cost."""
    if variation not in VARIATIONS:
        raise ValueError(f"unknown variation {variation!r}; have {VARIATIONS}")
    dense = variation == "dense"
    g = grid()
    raw = json.loads(CONTRIB_JSON.read_text(encoding="utf-8"))
    c = summarise(raw["total"], raw["days"])
    field = json.loads(FIELD_JSON.read_text(encoding="utf-8"))
    active_weeks = sum(1 for w in field["weeks"] if w["count"])

    svgs = {
        "masthead": plate(
            g, MASTHEAD_AT, MASTHEAD_ROWS, title=content.HERO_NAME,
            right="IMPERIAL COLLEGE LONDON",
            lede=None, dense=dense,
            foot=[("CONTRIBUTIONS", f"{c['total']:,}"),
                  ("WEEKS ACTIVE", f"{active_weeks} / 53"),
                  ("LONGEST RUN", f"{c['longest_streak']} d")],
            aria="Thomas van Pul, Design Engineering at Imperial College "
                 "London, set in a region of the Atrium lattice frame with "
                 f"{c['total']:,} contributions, {active_weeks} of 53 weeks "
                 f"active and a longest run of {c['longest_streak']} days "
                 "along its foot"),
    }
    if dense:
        for key, region, label in (("blueband", "blueband-concept", "BLUEBAND"),
                                   ("numeris", "Finance-Tracker", "NUMERIS")):
            lanes = field["regions"][region]["lanes"]
            commits = sum(l["total"] for l in lanes)
            files = sum(l["files"] for l in lanes)
            wks = sum(1 for i in range(53)
                      if any(l["commits"][i] for l in lanes))
            svgs[key] = plate(
                g, SMALL_AT[key], SMALL_ROWS, title=label, right="MEASURED 2026-09-19",
                lede=None, dense=True,
                foot=[("COMMITS", f"{commits:,}"), ("FILES", f"{files:,}"),
                      ("WEEKS", f"{wks} / 53")],
                aria=f"{label.title()}, measured: {commits} commits across "
                     f"{files} files in {wks} weeks of the last year")

    blobs: dict[str, bytes] = {}
    plates = {}
    for name in ("year", "day", "work"):
        got = animate.build(name, dense)
        plates[name] = got
        blobs[f"{name}.{got['ext']}"] = got["data"]
        blobs[f"{name}-still.png"] = got["still"]

    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    names = {b: f"{b}.{_sha7(s)}.svg" for b, s in svgs.items()}
    for base, svg in svgs.items():
        (assets / names[base]).write_text(svg, encoding="utf-8")
    for fname, data in blobs.items():
        stem, ext = fname.rsplit(".", 1)
        out = f"{stem}.{hashlib.sha256(data).hexdigest()[:7]}.{ext}"
        (assets / out).write_bytes(data)
        names[stem] = out

    (out_dir / "README.md").write_text(_readme(names, dense), encoding="utf-8")
    return {"variation": variation, "plates": plates, "assets": names}
