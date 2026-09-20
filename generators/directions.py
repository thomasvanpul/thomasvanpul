"""Three ways the page could be an Atrium interface, built so they can be judged.

This module does not ship a page. It builds each direction into its own
directory so `bin/directions.py` can render all three through GitHub's own
Markdown and photograph them at desktop and phone width. `generators/build.py`
is untouched and still emits the page that is live.

The three, and the axis between them
------------------------------------
They differ in one variable: **how much of the page is field.** All three are
cut from the same grid, at the same pitch, in the same order, so a band in one
direction is the same region of the same frame as the band in the next.

* **continuous** -- every section stands in the field. Six bands, contiguous
  rows, 87 of the grid's 107. The most literal reading of "the page is one
  continuous field, sections are regions of it".
* **quoted** -- the masthead and Atrium stand in the field; every other
  section gets a thin band of it carrying only that project's measurement.
  The field is present the whole way down and dominant only twice.
* **docked** -- the field appears where it carries data and nowhere else:
  the masthead and Atrium. Everything below is Markdown with one measurement
  rule under each heading. The most readable, and the least Atrium.

What is the same in all three
-----------------------------
Every word is Markdown. Nothing a reader has to read is inside an image, for
the reason `svg/lattice.py` gives at length: GitHub's search, the browser's
find and a screen reader all see one `alt` string and nothing else, and a
1200-unit plate renders at 0.30x in a phone column. The micro-labels that make
the page read as an instrument are `<sub>` rows of real counts out of
`data/field.json`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import content
from .svg import figures, hero, lattice
from .github import summarise
from .showroom import ingest

ROOT = Path(__file__).resolve().parent.parent
LATTICE_PNG = ROOT / "showroom" / "atrium-lattice.png"
GRID_CACHE = ROOT / "data" / "field-grid.json"
FIELD_JSON = ROOT / "data" / "field.json"
CONTRIB_JSON = ROOT / "data" / "contributions.json"

OWNER, REPO, BRANCH = "thomasvanpul", "thomasvanpul", "main"


# --- data ------------------------------------------------------------------

def grid() -> dict:
    """The one grid the whole page is cut from, reduced once and cached."""
    if GRID_CACHE.exists():
        return json.loads(GRID_CACHE.read_text(encoding="utf-8"))
    got = ingest("file://" + str(LATTICE_PNG), lattice.FIELD_COLS,
                 crop=lattice.FIELD_CROP,
                 source_bytes=LATTICE_PNG.read_bytes())
    if not got:
        raise RuntimeError("could not reduce the lattice frame; is Pillow installed?")
    got["source"] = f"showroom/atrium-lattice.png crop={lattice.FIELD_CROP}"
    GRID_CACHE.write_text(json.dumps(got) + "\n", encoding="utf-8")
    return got


def _field() -> dict:
    return json.loads(FIELD_JSON.read_text(encoding="utf-8"))


def _weeks_for(field_doc: dict, region: str) -> list[int]:
    lanes = field_doc["regions"][region]["lanes"]
    n = len(lanes[0]["commits"])
    return [sum(lane["commits"][i] for lane in lanes) for i in range(n)]


def _counts_for(field_doc: dict, region: str) -> tuple[int, int, int]:
    lanes = field_doc["regions"][region]["lanes"]
    return (sum(l["total"] for l in lanes), sum(l["files"] for l in lanes), len(lanes))


# --- the regions -----------------------------------------------------------

def _regions(field_doc: dict) -> list[dict]:
    """Every section of the page, in the order `content.DOMINANT` sets."""
    out = []
    for name in content.LAYOUT[content.DOMINANT]["order"]:
        commits, files, repos = _counts_for(field_doc, name)
        weeks = _weeks_for(field_doc, name)
        if name == "atrium":
            a = content.ATRIUM
            out.append({
                "key": "atrium", "heading": a["heading"], "weeks": weeks,
                "micro": (f"SCN·01 &nbsp; {commits} COMMITS &nbsp; {files} FILES "
                          f"&nbsp; {repos} REPOSITORIES &nbsp; 218,016 EVENTS"),
                "lede": (a["lede_number"], a["lede_caption"]),
                "body": a["body"], "table": (a["table_head"], a["table"]),
                "repo_line": a["repo_line"],
                "aria": ("Atrium's region of the field: a frame of the lattice "
                         f"with {commits} commits across {repos} repositories "
                         "drawn over it, one cell per week"),
            })
            continue
        prose = content.FEATURED[name]
        body = prose["body"]
        out.append({
            "key": name, "heading": prose["heading"], "weeks": weeks,
            "micro": (f"SCN·0{len(out) + 1} &nbsp; {commits} COMMITS "
                      f"&nbsp; {files} FILES &nbsp; "
                      f"{sum(1 for c in lattice._periods(weeks) if c)} "
                      f"OF {lattice.PERIODS} PERIODS"),
            "lede": (f"{commits:,}", "COMMITS"),
            "body": body if isinstance(body, list) else [body],
            "table": None,
            "repo_line": (f'Repo: [`{name}`](https://github.com/{OWNER}/{name})'
                          + (f' &nbsp;·&nbsp; {prose["repo_suffix"]}'
                             if prose.get("repo_suffix") else "")),
            "aria": (f"{prose['heading']}'s region of the field: {commits} "
                     f"commits drawn as one cell per week over the lattice"),
        })
    return out


# --- plans -----------------------------------------------------------------
# rows out of the one grid, in page order. Sum stays inside the grid's 107.
PLANS = {
    # Every section stands in the field, and every project's own record is
    # drawn over its own region. 99 of the grid's 107 rows.
    "continuous": {
        "masthead": 24, "atrium": 28, "blueband-concept": 16,
        "Finance-Tracker": 16, "also": 8, "stack": 7,
        "measure_projects": True, "lede_in_field": True,
        "figures_plate": False,
    },
    # The field runs the whole page and the instrument does not. Atrium is
    # the only region drawn as a measurement; the others are a quotation of
    # the same frame with their counts in the Markdown micro-label under
    # them. 65 rows.
    "quoted": {
        "masthead": 20, "atrium": 27, "blueband-concept": 5,
        "Finance-Tracker": 5, "also": 4, "stack": 4,
        "measure_projects": False, "lede_in_field": True,
        "figures_plate": False,
    },
    # `continuous` with its two texture-only bands cut, which is what the
    # stills argue for: "Also running" and "Stack" got 64 and 55 units of
    # field carrying no measurement, and on a phone those are 19px and 16px
    # of grey strip. A region with nothing to measure should be empty, so
    # they are. 84 rows.
    "trimmed": {
        "masthead": 24, "atrium": 28, "blueband-concept": 16,
        "Finance-Tracker": 16, "also": 0, "stack": 0,
        "measure_projects": True, "lede_in_field": True,
        "figures_plate": False,
    },
    # The field appears exactly where it carries data and nowhere else: under
    # the name, and as Atrium's own region. 36 rows.
    "docked": {
        "masthead": 16, "atrium": 20, "blueband-concept": 0,
        "Finance-Tracker": 0, "also": 0, "stack": 0,
        "measure_projects": False, "lede_in_field": False,
        "figures_plate": True,
    },
}


def _sha7(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:7]


def _url(asset: str) -> str:
    return (f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/"
            f"assets/{asset}")


def _img(url: str, alt: str) -> str:
    return f'<img alt="{alt}" src="{url}">'


def _table(rows, head=None) -> str:
    cols = head or ("", "")
    out = [f"| {cols[0]} | {cols[1]} |", "| --- | --- |"]
    out.extend(f"| {a} | {b} |" for a, b in rows)
    return "\n".join(out)


def build(name: str, out_dir: Path) -> Path:
    """Write one direction's assets and README into `out_dir`."""
    plan = PLANS[name]
    g = grid()
    field_doc = _field()
    # `summarise` is what turns the two committed fields into the figures the
    # page prints. Reading the cache raw gives total and days and nothing
    # else, and the first stills said "0 of 370 days active" under the name.
    raw = json.loads(CONTRIB_JSON.read_text(encoding="utf-8"))
    contrib = summarise(raw["total"], raw["days"])
    regions = _regions(field_doc)

    variants: dict[str, str] = {}
    cursor = 0

    def take(rows: int) -> dict:
        nonlocal cursor
        sl = lattice.band(g, cursor, rows)
        cursor += rows
        return sl

    # The masthead, and the contribution months the planet still encodes.
    months = contrib.get("months") or []
    variants["masthead"] = lattice.masthead(
        take(plan["masthead"]), content.HERO_NAME, months, content.HERO_ARIA)
    # The same band with the pip parked. It re-reads rows 0..n rather than
    # taking from the cursor: the still is the same region of the field, not
    # the next one.
    variants["masthead-still"] = lattice.masthead(
        lattice.band(g, 0, plan["masthead"]), content.HERO_NAME, months,
        content.HERO_ARIA, animate=False)

    for region in regions:
        rows = plan[region["key"]]
        if rows <= 0:
            region["band"] = None
            continue
        sl = take(rows)
        # One dominant readout for the whole page, not one per region.
        # Primitive 9 in the design note is singular -- "one readout
        # everything else responds to" -- and three of them competing is how
        # the first pass ended up with a 72px number over every band and none
        # of them dominant. It goes on the region the page is built around.
        wants_lede = plan["lede_in_field"] and region["key"] == content.DOMINANT
        wants_measure = (region["key"] == content.DOMINANT
                         or plan["measure_projects"])
        variants[f"band-{_slug(region['key'])}"] = lattice.render(
            sl, region["aria"],
            weeks=region["weeks"] if wants_measure else None,
            lede=region["lede"] if wants_lede else None,
            pad_bottom=10.0)
        region["band"] = f"band-{_slug(region['key'])}"

    tails = {}
    for key, rows in (("also", plan["also"]), ("stack", plan["stack"])):
        if rows <= 0:
            tails[key] = None
            continue
        sl = take(rows)
        aria = ("A quieter region of the same lattice frame, carrying no "
                "measurement: nothing on this page counts these")
        variants[f"band-{key}"] = lattice.render(sl, aria)
        tails[key] = f"band-{key}"

    if plan["figures_plate"]:
        a = content.ATRIUM
        variants["atrium-figures"] = figures.render(
            a["lede_number"], a["lede_caption"], a["figures_aria"], view_w=900)

    filenames = {b: f"{b}.{_sha7(body)}.svg" for b, body in variants.items()}
    readme = _readme(name, plan, regions, tails, filenames, contrib)

    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for base, body in variants.items():
        (assets / filenames[base]).write_text(body, encoding="utf-8")
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    return out_dir


def _slug(name: str) -> str:
    return name.lower().replace("_", "-")


def _readme(name: str, plan: dict, regions: list[dict], tails: dict,
            filenames: dict, contrib: dict) -> str:
    lines = [
        "<picture>\n"
        f'  <source media="(prefers-reduced-motion: reduce)" '
        f'srcset="{_url(filenames["masthead-still"])}">\n'
        f'  <img alt="{content.HERO_ARIA}" '
        f'src="{_url(filenames["masthead"])}">\n'
        "</picture>\n",
    ]

    figs = hero.readout_figures(contrib)
    if figs:
        lines.append(" &nbsp;·&nbsp; ".join(f"**{n}** {c}" for n, c in figs) + "\n")
    lines.append(content.HERO_STANDFIRST + "\n")
    lines.append(content.INTRO + "\n")

    for region in regions:
        if region.get("band"):
            lines.append(_img(_url(filenames[region["band"]]), region["aria"]) + "\n")
        lines.append(f"### {region['heading']}\n")
        lines.append(f"<sub>{region['micro']}</sub>\n")
        if region["key"] == "atrium" and plan["figures_plate"]:
            a = content.ATRIUM
            lines.append(_img(_url(filenames["atrium-figures"]),
                              a["figures_aria"]) + "\n")
        if region["table"]:
            head, rows = region["table"]
            lines.append(_table(rows, head) + "\n")
        lines.extend(p + "\n" for p in region["body"])
        lines.append(region["repo_line"] + "\n")

    if tails.get("also"):
        lines.append(_img(_url(filenames[tails["also"]]),
                          "A quieter region of the same lattice frame") + "\n")
    lines.append(f"### {content.ALSO_RUNNING_HEADING}\n")
    for title, prose in content.ALSO_RUNNING:
        lines.append(f"**{title}** &nbsp;·&nbsp; {prose}\n")

    if tails.get("stack"):
        lines.append(_img(_url(filenames[tails["stack"]]),
                          "A quieter region of the same lattice frame") + "\n")
    lines.append(f"### {content.STACK_HEADING}\n")
    lines.append(_table(content.STACK_TABLE) + "\n")

    lines.append('<div align="center">\n')
    lines.append(
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="{content.SNAKE_DARK_URL}">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="{content.SNAKE_LIGHT_URL}">\n'
        f'  <img alt="{content.SNAKE_ARIA}" src="{content.SNAKE_DARK_URL}">\n'
        "</picture>")
    lines.append("\n")
    lines.append(f"<sub>{content.FOOTER_SUB}</sub>\n")
    lines.append(content.FOOTER_LINKS + "\n")
    lines.append("</div>")
    return "\n".join(lines) + "\n"
