"""The page's palette, and the one ground every asset paints before it draws.

Where the colours come from
---------------------------
`data/atrium-tokens.json` is a verbatim copy of `tokens/tokens.json` from
`~/dev/atrium-design`, which generates it from the Swift that actually runs:
`DayCurve.swift`, `FieldRenderer.swift` and `LatticeRenderer.swift`. No ink on
this page is hand-picked, which is the point -- `atrium-design/bin/consumers.py`
names this exact module as a downstream consumer and audits it for stray
literals, including the ones in this docstring.

Why the ground is GitHub's and not Atrium's
-------------------------------------------
Every asset used to paint `field-light-edge`, Atrium's outer field tone. That
is a warm near-black, and GitHub's dark canvas is a cool one. Measured in
CIELAB they are **6.36 apart** at almost the same lightness (L* 3.84 against
4.95) with their chroma pointing opposite ways, which is the worst possible
arrangement: too close to read as a deliberate panel, too far to disappear.
The page came back as "a mixture of poor colours" and this was most of it --
nine plates, each a brown slab on a blue-grey page, with GitHub's own link
blue running between them.

The obvious repair is to cool the plate by moving down Atrium's ramp, and the
measurement says it does not work: `density-0`, the darkest token there is,
sits **6.44** from the canvas -- no closer than the tone it replaces. There is
no colour in this palette that reads as page rather than as panel, because
none of them is the page's colour.

So the ground is the page's own canvas, and the two values below are the two
Primer serves. They are the only non-token colours in this repo and they are
listed in `atrium-design`'s `EXCEPTIONS` for the same reason Chrome's tab
colours are listed there: a plate drawn on GitHub's canvas has to *be* GitHub's
canvas, or it is not on the page, it is a rectangle lying on top of it.

What that buys, beyond the slab going away: the plates now respond to the
reader's theme. An `<img>`-referenced SVG carries its own CSS and honours
`prefers-color-scheme` -- verified in Chromium, not assumed -- so the ground
flips with the page and the ink flips with it, `density-5` on the dark canvas
and `density-0` on the light one. Both ends of the ink are still Atrium's ramp.
A browser that ignores the query gets the dark pair, which is exactly what
every reader got before, so the fallback is the status quo and not a defect.

Ink travels as `currentColor`
-----------------------------
The ink is set once, as `color` on the root `<svg>`, and every mark asks for
`currentColor`. That is what makes one media query enough for a whole asset:
nothing downstream of here writes a colour at all.

What is deliberately not used
-----------------------------
`density-1` to `density-3` carry hue, and hue in Atrium is reserved for state.
`density-4` is the page's single accent and appears exactly once, on the one
mark that moves -- see `hero.py`. The contribution snake is the other coloured
thing on the page and its five steps map to a measured count, which is what
the ramp is for; that mapping lives in `.github/workflows/snake.yml`.
"""
from __future__ import annotations

import json
from pathlib import Path

TOKENS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "atrium-tokens.json"

_DOC = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
TOKENS: dict[str, str] = {name: v["hex"] for name, v in _DOC["tokens"].items()}

# The resting point the whole set is taken at, kept so a reader of this module
# can see the one judgement call without opening another repo.
RESTING_HUE_DEG: float = _DOC["resting_point"]["hue_deg"]
RESTING_LIGHTNESS: float = _DOC["resting_point"]["lightness"]
DAY_CURVE_HUE_RANGE_DEG: list[float] = _DOC["day_curve"]["hue_range_deg"]


def token(name: str) -> str:
    """The hex for a token name, e.g. `token("density-5")`."""
    try:
        return TOKENS[name]
    except KeyError:
        raise KeyError(f"unknown token: {name}") from None


# Ink: both ends of Atrium's own ramp, one per theme.
INK_DARK = "density-5"
INK_LIGHT = "density-0"

# Accent: one step of the ramp, used on one mark on the whole page.
ACCENT = "density-4"

# Ground: Primer's `canvas.default`, dark and light. Not tokens, on purpose,
# and listed as exceptions upstream. See the docstring.
GROUND_DARK = "#0d1117"
GROUND_LIGHT = "#ffffff"

# Every mark in this repo is painted in this, so the ink is set in one place.
FG = "currentColor"


def palette() -> tuple[str, str]:
    """(ink, ground) as paint values, not as colours.

    The ink is `currentColor` and the ground is a class, because both have to
    be able to change with the reader's theme and an SVG can only do that from
    a stylesheet. Callers that need the ground put `class="ground"` on the
    element rather than writing a fill.
    """
    return FG, "var(--ground)"


def field() -> str:
    """The ground every asset paints before it draws anything, and its theme.

    GitHub strips CSS from a README, so the page's own background is not ours
    to set -- but each SVG is a document of its own, carries its own
    stylesheet, and is told the reader's colour scheme. So each asset paints
    the canvas GitHub is about to put it on, and flips with it.
    """
    return (
        "  <style>\n"
        f"    svg {{ color: {token(INK_DARK)}; --ground: {GROUND_DARK}; }}\n"
        "    .ground { fill: var(--ground); }\n"
        "    @media (prefers-color-scheme: light) {\n"
        f"      svg {{ color: {token(INK_LIGHT)}; --ground: {GROUND_LIGHT}; }}\n"
        "    }\n"
        "  </style>\n"
        '  <rect class="ground" width="100%" height="100%"/>\n'
    )
