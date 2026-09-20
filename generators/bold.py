"""Three directions that differ in kind, built so they can be judged.

`generators/directions.py` holds four directions that differ in *degree* --
they vary only in how much of the page is lattice field. Thomas looked at all
four on 19 September and said "not really what I am going for, I want it to
look way way better", which is a verdict on the bar rather than on the point
chosen along that one axis. So these three move the axis:

* **index** -- nearly imageless. Type, rhythm and one hairline rule per
  section, where the rule is a single row of the real lattice grid. The page
  is a list of things that are true, set well. Borrowed from `antfu`,
  `caneco`, `natemoo-re` and GMUNK's title-and-rails lockup.
* **playback** -- one animated image carries the page. A 2x magnification of
  the real frame with the year's 53 real weeks swept through beneath it,
  and almost no words. Borrowed from `Platane`, `orhun`, `jh3y` and GMUNK's
  near-black frames.
* **instrument** -- the page as an Atrium readout: a field held between two
  docked rails of real counts, with one dominant numeral. Borrowed from
  GMUNK's `interface.022` and `029`, `lowlighter` and `anandchowdhary`.

All three keep what Thomas has already decided: blue links, dark ground,
Atrium leading, BlueBand at the same weight as the rest, no dot strip under
his name, far fewer words than the page that is live.

The type floor
--------------
`tests/test_build.py` holds every text element to 3.07% of its plate width,
which is 11px in GitHub's 358px phone column. On a 1200-unit plate that is
36.8px and on a 900-unit plate 27.6px. It is the reason `instrument` has four
rail labels rather than the twenty a GMUNK frame carries: a rail of 14px
labels is a texture on a desktop and an unreadable smudge on a phone, and this
page has been rejected three times for exactly that.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import svg
from . import content, motion
from .directions import grid, _field, _regions, _url, _sha7
from .github import summarise
from .svg import lattice

ROOT = Path(__file__).resolve().parent.parent
CONTRIB_JSON = ROOT / "data" / "contributions.json"

PLANS = ("index", "playback", "instrument")

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

# The floor, with the gap between the repo's two of them closed. The test in
# `tests/test_build.py` asserts >= 3.07% of the plate's own viewBox, and
# `bin/directions.py` asserts >= 11px apparent in GitHub's 358px phone column.
# They are not the same number: 3.07% of 1200 is 36.8 units, which reads at
# 10.98px, so a plate set exactly at the test's floor fails the preview tool's
# by two hundredths of a pixel. 3.12% clears both and is the smaller change.
FLOOR = 0.0312

# A monospaced advance is 0.60em in every font in the stack this repo uses
# (SF Mono, Menlo, Consolas), and `letter-spacing` adds its tracking to every
# character including the last. Both stills of the first instrument pass ran
# text off the plate or into the next column -- "CONTRIBUTIOИDAYS ACTIVE",
# "LINES OF SWIFTASSERTIONS", a caption cut at "2026-0" -- because the
# strings were written by eye. `_fits` turns that into a build failure.
ADVANCE = 0.60


def _fits(text: str, size: float, tracking: float, room: float,
          where: str) -> str:
    width = len(text) * size * (ADVANCE + tracking)
    if width > room:
        raise ValueError(
            f"{where}: {text!r} is {width:.0f} units wide at {size:.1f}px "
            f"with {tracking:g}em tracking, and there are {room:.0f}")
    return text


def _open(view_w: float, view_h: float, aria: str) -> list[str]:
    """Every asset paints the canvas first -- see the Makefile's note on -b."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '
        f'{view_w:.0f} {view_h:.0f}" width="{view_w:.0f}" '
        f'height="{view_h:.0f}" role="img" aria-label="{aria}">\n',
        f'  <rect width="{view_w:.0f}" height="{view_h:.0f}" fill="{GROUND}"/>\n',
    ]


# --- index: the page as a set list ----------------------------------------

def rule(g: dict, row: int) -> str:
    """One row of the real grid, drawn as a hairline.

    The thinnest honest expression of "this page is cut from one frame": a
    section break that is still real data. Each rule takes a different row, so
    reading down the page is still reading down the frame.
    """
    sl = lattice.band(g, row, 1)
    cols, cells = sl["cols"], sl["cells"]
    pitch = VIEW_W / (cols - 1)
    marks = []
    for idx, ch in enumerate(cells):
        value = ord(ch) - 48
        if value < lattice.INK_FLOOR:
            continue
        marks.append((round(idx * pitch), value))
    body = _open(VIEW_W, 8, "A single row of the Atrium lattice frame, "
                            "drawn as a rule")
    buckets: dict[int, list[str]] = {}
    for x, value in marks:
        buckets.setdefault(value, []).append(f"M{x} 4h.01")
    for value in sorted(buckets):
        opacity = min(0.35 + 0.07 * (value - lattice.INK_FLOOR), 0.95)
        body.append(
            f'  <path d="{"".join(buckets[value])}" stroke="{INK}" '
            f'stroke-opacity="{opacity:.2f}" stroke-width="'
            f'{lattice.DOT_WIDTH[value]:.2f}" stroke-linecap="round" '
            'fill="none"/>\n')
    body.append("</svg>\n")
    return "".join(body)


# --- instrument: a field between two docked rails --------------------------

def instrument_plate(g: dict, row0: int, rows: int, name: str,
                     caption: list[str], readouts: list[tuple[str, str]],
                     numeral: str | None, numeral_caption: str | None,
                     aria: str) -> str:
    """One plate: a field, a lockup at the top left, readouts along the foot.

    The first pass put the readouts in two vertical rails either side of the
    field, which is what GMUNK's `interface.022` does. It does not survive the
    type floor. A rail label is 37.4 units on a 1200 plate, and "CONTRIBUTIONS"
    at that size is 291 units wide, so a rail wide enough to hold it leaves
    408 units of field between the two -- and the name, at 14 monospaced
    characters, is 524 units and will not fit in that gap. Both stills showed
    "BUTIONS" and "ASSERTI" running off the plate edges.

    `interface.029` is the frame that does survive: the lockup is top left,
    a small caption block is top right, and the numbers are *horizontal* rails
    across the frame rather than vertical ones beside it. Horizontal is what
    a 1200-unit plate has room for, so that is the composition.
    """
    sl = lattice.band(g, row0, rows)
    marks, view_h = lattice._marks(sl, INK)
    size = VIEW_W * FLOOR
    body = _open(VIEW_W, view_h, aria)
    body.extend(marks)
    # A wash over the field so type sits on ground rather than on marks. The
    # marks are texture and may go under it; the words may not go under them.
    body.append(f'  <rect width="{VIEW_W}" height="{view_h:.0f}" '
                f'fill="{GROUND}" fill-opacity="0.52"/>\n')

    # Explicit vertical slots, because the first pass placed everything as a
    # fraction of the band height and the caption, the accent rule and the
    # readout labels all landed within 20 units of each other on a 220-unit
    # plate. The plate is now tall enough to have slots at all.
    lockup = 96.0
    caption_y = lockup + size * 1.30
    foot = view_h - 34
    if name:
        _fits(name, VIEW_W * 0.052, 0.18, VIEW_W - 80, "lockup")
        body.append(
            f'  <text x="40" y="{lockup:.0f}" fill="{INK}" style="font: 700 '
            f'{VIEW_W * 0.052:.1f}px {MONO}; letter-spacing: .18em">'
            f'{name}</text>\n')
        body.append(f'  <path d="M40 {lockup + 26:.0f}h240" stroke="{ACCENT}" '
                    'stroke-width="3"/>\n')
    if numeral:
        body.append(
            f'  <text x="40" y="{lockup + 14:.0f}" fill="{ACCENT}" '
            f'style="font: 700 {VIEW_W * 0.088:.1f}px {MONO}">'
            f'{numeral}</text>\n')
    for i, line in enumerate(caption):
        _fits(line, size, 0.10, VIEW_W - 80, "caption")
        body.append(
            f'  <text x="40" y="{caption_y + 26 + i * size * 1.45:.0f}" '
            f'fill="{DIM}" style="font: 500 {size:.1f}px '
            f'{MONO}; letter-spacing: .10em">{line}</text>\n')

    # Three readouts, not four. A slot is (1200-80)/n units wide and a label
    # is 22.4 units per monospaced character at the floor, so four slots give
    # 264 units of room for "CONTRIBUTIONS", which needs 291 -- the first
    # stills read "CONTRIBUTIOИDAYS ACTIVE". Three slots give 373.
    step = (VIEW_W - 80) / len(readouts)
    for i, (label, value) in enumerate(readouts):
        x = 40 + i * step
        _fits(label, size, 0.08, step - 18 - 20, f"readout {i}")
        _fits(value, size * 1.34, 0.0, step - 18 - 20, f"readout {i} value")
        body.append(f'  <path d="M{x:.0f} {foot - size * 2.5:.0f}'
                    f'v{size * 2.5:.0f}" stroke="{INK}" stroke-opacity="0.30" '
                    'stroke-width="2"/>\n')
        body.append(
            f'  <text x="{x + 18:.0f}" y="{foot - size * 1.45:.0f}" '
            f'fill="{DIM}" style="font: 500 {size:.1f}px {MONO}; '
            f'letter-spacing: .08em">{label}</text>\n')
        body.append(
            f'  <text x="{x + 18:.0f}" y="{foot:.0f}" fill="{INK}" '
            f'style="font: 600 {size * 1.34:.1f}px {MONO}">{value}</text>\n')
    body.append("</svg>\n")
    return "".join(body)


# --- the three READMEs -----------------------------------------------------

def _img(url: str, alt: str, width: int | None = None) -> str:
    w = f' width="{width}"' if width else ""
    return f'<img alt="{alt}" src="{url}"{w}>'


ATRIUM_LINE = ("A spatial desktop for macOS, in Swift and Metal. It draws the "
               "machine's own record as a navigable field: every mark a real "
               "event, depth is recency.")
ATRIUM_FIGURES = ("**218,016** events from **31** repositories &nbsp;·&nbsp; "
                  "**18,470** lines of Swift &nbsp;·&nbsp; **418** assertions "
                  "over **38%** &nbsp;·&nbsp; **10 MB** resident")
ATRIUM_COST = ("Acceptance has never passed: **11 criteria, all UNMEASURED**. "
               "Engineering depth, not delivery.")
FOOTER = (f"<sub>{content.FOOTER_SUB}</sub>\n\n{content.FOOTER_LINKS}\n")
ALSO_ONE_LINE = (
    "**Interstellar Sanctuary** a Malaysia property launch map, "
    "[password-gated](https://interstellarsanctuary.com) &nbsp;·&nbsp; "
    "**HFQ forming** with Dr Nan Li at the Dyson School &nbsp;·&nbsp; "
    "**Air defence economics** a self-directed paper &nbsp;·&nbsp; "
    "**IRIS** an always-on assistant daemon")
STACK_ONE_LINE = (
    "Python · TypeScript · React · Node · PostgreSQL &nbsp;·&nbsp; "
    "Fusion 360 · Ansys · SimScale · KiCad &nbsp;·&nbsp; "
    "TIG welding · FDM printing · composite layup")
BLUEBAND = ("A wearable motion band — enclosure, board, firmware and app, one "
            "person doing the whole chain.")
NUMERIS = ("Plaid in, market data alongside it, normalised into Postgres, out "
           "through a typed API. Used daily, which is what makes it real.")
BLUEBAND_REPO = "[`blueband-concept`](https://github.com/thomasvanpul/blueband-concept)"
NUMERIS_REPO = "[`Finance-Tracker`](https://github.com/thomasvanpul/Finance-Tracker)"


def _index_readme(f: dict) -> str:
    """Nearly imageless. Six hairline rules and nothing else drawn."""
    def r(n: int) -> str:
        return _img(_url(f[f"rule-{n}"]), "A single row of the Atrium lattice "
                                          "frame, drawn as a rule") + "\n"
    return "\n".join([
        "# Thomas van Pul",
        "",
        "**Design Engineering, Imperial College London.** "
        "I build hardware and the software that runs it.",
        "",
        r(0),
        "### Atrium &nbsp;<sub>private</sub>",
        "",
        ATRIUM_LINE,
        "",
        ATRIUM_FIGURES,
        "",
        ATRIUM_COST,
        "",
        r(1),
        "### BlueBand",
        "",
        BLUEBAND,
        "",
        BLUEBAND_REPO,
        "",
        r(2),
        "### Numeris",
        "",
        NUMERIS,
        "",
        NUMERIS_REPO,
        "",
        r(3),
        "### Also running",
        "",
        ALSO_ONE_LINE,
        "",
        r(4),
        "### Stack",
        "",
        STACK_ONE_LINE,
        "",
        r(5),
        FOOTER,
    ])


def _playback_readme(f: dict, motion_name: str, still_name: str) -> str:
    """One animated image carries the page, and the words get out of its way."""
    gif = _url(motion_name)
    still = _url(still_name)
    return "\n".join([
        "<picture>",
        f'  <source media="(prefers-reduced-motion: reduce)" srcset="{still}">',
        f'  <img alt="{motion.ALT}" src="{gif}">',
        "</picture>",
        "",
        "<sub>**Atrium** &nbsp;·&nbsp; one real region of the lattice frame, "
        "and the year's 53 real weeks, swept together one week at a time. "
        "218,016 events, 31 repositories.</sub>",
        "",
        "**Thomas van Pul** &nbsp;·&nbsp; Design Engineering, Imperial College "
        "London. I build hardware and the software that runs it.",
        "",
        f"**Atrium** &nbsp;·&nbsp; {ATRIUM_LINE} Private repo.",
        "",
        ATRIUM_FIGURES,
        "",
        ATRIUM_COST,
        "",
        f"**BlueBand** &nbsp;·&nbsp; {BLUEBAND} {BLUEBAND_REPO}",
        "",
        f"**Numeris** &nbsp;·&nbsp; {NUMERIS} {NUMERIS_REPO}",
        "",
        ALSO_ONE_LINE,
        "",
        STACK_ONE_LINE,
        "",
        FOOTER,
    ])


def _instrument_readme(f: dict) -> str:
    """Two plates, both readouts, and Markdown in the gap between them."""
    head = _img(_url(f["masthead"]),
                "Thomas van Pul, Design Engineering at Imperial College "
                "London, set in a region of the Atrium lattice between two "
                "docked rails of counts")
    plate = _img(_url(f["atrium"]),
                 "Atrium, measured: 218,016 events from 31 repositories, "
                 "18,470 lines of Swift, 418 assertions over 38% of the code, "
                 "10 MB resident")
    return "\n".join([
        head,
        "",
        "### Atrium",
        "",
        plate,
        "",
        ATRIUM_LINE,
        "",
        ATRIUM_COST + " Private repo.",
        "",
        f"### BlueBand\n\n{BLUEBAND} {BLUEBAND_REPO}",
        "",
        f"### Numeris\n\n{NUMERIS} {NUMERIS_REPO}",
        "",
        f"### Also running\n\n{ALSO_ONE_LINE}",
        "",
        f"### Stack\n\n{STACK_ONE_LINE}",
        "",
        FOOTER,
    ])


# --- build -----------------------------------------------------------------

# Two rows per rail, not the twenty a GMUNK frame carries. At the type floor
# a label is 36.8 units on a 1200 plate and a pair is 96 units tall, so four
# numbers is what a 230-unit plate holds without the rails running into the
# field. Restraint here is arithmetic, not taste.
MASTHEAD_ROWS = 40
ATRIUM_ROWS = 40
RULE_ROWS = (6, 21, 38, 55, 72, 96)


def build(name: str, out_dir: Path) -> Path:
    """Write one direction's assets and README into `out_dir`."""
    if name not in PLANS:
        raise ValueError(f"unknown direction {name!r}; have {PLANS}")
    g = grid()
    raw = json.loads(CONTRIB_JSON.read_text(encoding="utf-8"))
    contrib = summarise(raw["total"], raw["days"])

    svgs: dict[str, str] = {}
    blobs: dict[str, bytes] = {}

    if name == "index":
        for i, row in enumerate(RULE_ROWS):
            svgs[f"rule-{i}"] = rule(g, row)
    elif name == "playback":
        blobs["lattice-motion.gif"] = motion.render()
        blobs["lattice-still.png"] = motion.still()
    else:
        svgs["masthead"] = instrument_plate(
            g, 0, MASTHEAD_ROWS, content.HERO_NAME,
            ["DESIGN ENGINEERING · IMPERIAL COLLEGE"],
            [("CONTRIBUTIONS", f"{contrib['total']:,}"),
             ("DAYS ACTIVE", f"{contrib['active_days']} / "
                             f"{len(contrib['days'])}"),
             ("LONGEST RUN", f"{contrib['longest_streak']} d")],
            None, None,
            "Thomas van Pul, Design Engineering at Imperial College London, "
            "set in a region of the Atrium lattice with four counts along "
            "its foot: 2,774 contributions, 78 of 370 days active, a busiest "
            "day of 151 and a longest run of 45 days")
        svgs["atrium"] = instrument_plate(
            g, MASTHEAD_ROWS + 4, ATRIUM_ROWS, "",
            ["EVENTS · 31 REPOSITORIES · 2026-09-16"],
            [("SWIFT LINES", "18,470"), ("ASSERTIONS", "418"),
             ("COVERED", "38%")],
            "218,016", None,
            "Atrium measured: 218,016 events from 31 repositories, 18,470 "
            "lines of Swift across 75 files, 418 assertions over 38%")

    filenames = {b: f"{b}.{_sha7(body)}.svg" for b, body in svgs.items()}
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for base, body in svgs.items():
        (assets / filenames[base]).write_text(body, encoding="utf-8")
    for fname, data in blobs.items():
        stem, ext = fname.rsplit(".", 1)
        out = f"{stem}.{hashlib.sha256(data).hexdigest()[:7]}.{ext}"
        (assets / out).write_bytes(data)
        filenames[stem] = out

    if name == "index":
        readme = _index_readme(filenames)
    elif name == "playback":
        readme = _playback_readme(filenames, filenames["lattice-motion"],
                                  filenames["lattice-still"])
    else:
        readme = _instrument_readme(filenames)
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    return out_dir
