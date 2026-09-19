"""Safety tests for the profile builder."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from generators import build
from generators import content
from generators import github as gh


ORBIT_STUB = {
    "rings": [
        {"rx": 470, "ry": 116, "duration": 46, "items": ["Python"]},
        {"rx": 330, "ry": 82, "duration": 33, "items": ["Fusion 360"]},
        {"rx": 200, "ry": 50, "duration": 22, "items": ["TIG welding"]},
    ]
}


def _write_orbit(tmp: Path) -> Path:
    p = tmp / "orbit.json"
    p.write_text(json.dumps(ORBIT_STUB), encoding="utf-8")
    return p


def _seed_out(tmp: Path) -> tuple[Path, dict[Path, str]]:
    """Populate an out_dir with a pre-existing README + assets. Return snapshot."""
    (tmp / "assets").mkdir()
    files = {
        tmp / "README.md": "PREVIOUS README\n",
        tmp / "assets" / "hero.deadbee.svg": "<svg>previous</svg>",
        tmp / "assets" / "orbit.deadbee.svg": "<svg>previous orbit</svg>",
    }
    for p, body in files.items():
        p.write_text(body, encoding="utf-8")
    snapshot = {p: p.read_text(encoding="utf-8") for p in files}
    return tmp, snapshot


def _assert_unchanged(snapshot: dict[Path, str]) -> None:
    for path, body in snapshot.items():
        assert path.exists(), f"{path} was deleted"
        assert path.read_text(encoding="utf-8") == body, f"{path} was modified"


def test_zero_featured_repos_raises_and_leaves_disk_untouched(tmp_path):
    out_dir, snapshot = _seed_out(tmp_path)
    orbit = _write_orbit(tmp_path)
    fixture = tmp_path / "unused.json"

    with patch.object(gh, "fetch_featured_repos", return_value=[]):
        with pytest.raises(build.BuildError, match="no featured repos"):
            build.build(fixture_path=fixture, orbit_path=orbit,
                        out_dir=out_dir, token="fake-token")

    _assert_unchanged(snapshot)
    # And no new assets got written mid-build.
    assert sorted(p.name for p in (out_dir / "assets").iterdir()) == \
        sorted(p.name for p in snapshot if p.parent.name == "assets")


def test_api_failure_raises_and_leaves_disk_untouched(tmp_path):
    out_dir, snapshot = _seed_out(tmp_path)
    orbit = _write_orbit(tmp_path)
    fixture = tmp_path / "unused.json"

    def boom(_token, _owner=None):
        raise gh.GitHubError("HTTP 502 for /users/thomasvanpul/repos: bad gateway")

    with patch.object(gh, "fetch_featured_repos", side_effect=boom):
        with pytest.raises(build.BuildError, match="failed to fetch repos"):
            build.build(fixture_path=fixture, orbit_path=orbit,
                        out_dir=out_dir, token="fake-token")

    _assert_unchanged(snapshot)


def test_weight_sort_beats_pushed_at(tmp_path):
    """Lower weight wins; unweighted repos sort last, tie-broken by pushed_at."""
    entries = [
        {"name": "recent-unweighted", "pushed_at": "2026-09-01T00:00:00Z",
         "profile_config": {}},
        {"name": "heavy", "pushed_at": "2026-08-01T00:00:00Z",
         "profile_config": {"weight": 20}},
        {"name": "light", "pushed_at": "2026-01-01T00:00:00Z",
         "profile_config": {"weight": 10}},
        {"name": "older-unweighted", "pushed_at": "2026-05-01T00:00:00Z",
         "profile_config": None},
    ]
    from generators.build import _sort_featured
    ordered = [e["name"] for e in _sort_featured(entries)]
    assert ordered == ["light", "heavy", "recent-unweighted", "older-unweighted"]


def test_contributions_fetch_failure_leaves_disk_untouched(tmp_path):
    out_dir, snapshot = _seed_out(tmp_path)
    orbit = _write_orbit(tmp_path)
    fixture = tmp_path / "unused.json"

    api_repo = {
        "name": "some-repo",
        "html_url": "https://github.com/thomasvanpul/some-repo",
        "default_branch": "main",
        "description": "desc",
        "language": "Python",
        "topics": ["profile-feature"],
        "pushed_at": "2026-08-01T00:00:00Z",
        "archived": False,
        "fork": False,
    }

    def boom(_token, _owner=None):
        raise gh.GitHubError("GraphQL HTTP 502: bad gateway")

    with patch.object(gh, "fetch_featured_repos", return_value=[api_repo]), \
         patch.object(gh, "fetch_profile_config", return_value=None), \
         patch.object(gh, "fetch_contributions", side_effect=boom):
        with pytest.raises(build.BuildError, match="failed to fetch contributions"):
            build.build(fixture_path=fixture, orbit_path=orbit, out_dir=out_dir,
                        token="fake-token")

    _assert_unchanged(snapshot)


def test_streak_computation_with_gap():
    """Longest streak spans the pre-gap run; current streak reflects post-gap."""
    def days(spec: str) -> list[dict]:
        # spec is a string like "1101110" where each char is the day's count.
        return [{"date": f"2026-01-{i+1:02d}", "count": int(c)} for i, c in enumerate(spec)]

    # 5-day run, 2-day gap, 3-day run. Today (last char) is the tail of the
    # current run; longest should include the earlier 5.
    d = days("11111001110" + "11")  # 13 days total
    assert gh.longest_streak(d) == 5
    assert gh.current_streak(d) == 2

    # Trailing zero (today blank): grace period keeps the current streak alive.
    d2 = days("111100")
    assert gh.longest_streak(d2) == 4
    # Grace burns on the trailing zero, second zero terminates.
    assert gh.current_streak(d2) == 0

    # Trailing zero + previous run: grace burns, then run counts.
    d3 = days("11110")
    assert gh.current_streak(d3) == 4

    # Empty calendar.
    assert gh.longest_streak([]) == 0
    assert gh.current_streak([]) == 0


def test_missing_profile_yml_falls_back_to_plain_card(tmp_path):
    out_dir = tmp_path
    (out_dir / "assets").mkdir()
    orbit = _write_orbit(tmp_path)
    fixture = tmp_path / "unused.json"

    api_repo = {
        "name": "plain-repo",
        "html_url": "https://github.com/thomasvanpul/plain-repo",
        "default_branch": "main",
        "description": "A repo with no diagram config.",
        "language": "Rust",
        "topics": ["profile-feature"],
        "pushed_at": "2026-01-01T00:00:00Z",
        "archived": False,
        "fork": False,
    }
    contribs = {"total": 1000, "current_streak": 5, "longest_streak": 12}

    with patch.object(gh, "fetch_featured_repos", return_value=[api_repo]), \
         patch.object(gh, "fetch_profile_config", return_value=None), \
         patch.object(gh, "fetch_contributions", return_value=contribs):
        build.build(fixture_path=fixture, orbit_path=orbit,
                    out_dir=out_dir, token="fake-token")

    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    assert "### plain-repo" in readme
    assert "A repo with no diagram config." in readme
    # No flow SVG should have been emitted for the plain repo.
    assert not any(p.name.startswith("flow-plain-repo") for p in (out_dir / "assets").iterdir())


def _contrib(days_spec: list[tuple[str, int]]) -> dict:
    return gh.summarise(sum(c for _d, c in days_spec),
                        [{"date": d, "count": c} for d, c in days_spec])


def test_every_generated_svg_is_well_formed_xml(tmp_path):
    """The build happily wrote invalid XML once and the gate passed anyway.

    A double-quoted font family inside a style="..." attribute closed the
    attribute early. `python3 -m generators.build` cannot see that; only a
    parser can. Parse every asset the build emits.
    """
    import xml.etree.ElementTree as ET

    out_dir = tmp_path
    (out_dir / "assets").mkdir()
    orbit = _write_orbit(tmp_path)
    fixture = tmp_path / "unused.json"

    api_repo = {
        "name": "some-repo", "html_url": "https://github.com/thomasvanpul/some-repo",
        "default_branch": "main", "description": "desc", "language": "Python",
        "topics": ["profile-feature"], "pushed_at": "2026-08-01T00:00:00Z",
        "archived": False, "fork": False,
    }
    contribs = _contrib([("2026-07-%02d" % i, i) for i in range(1, 29)])

    with patch.object(gh, "fetch_featured_repos", return_value=[api_repo]), \
         patch.object(gh, "fetch_profile_config", return_value=None), \
         patch.object(gh, "fetch_contributions", return_value=contribs):
        build.build(fixture_path=fixture, orbit_path=orbit, out_dir=out_dir,
                    token="fake-token")

    written = sorted((out_dir / "assets").glob("*.svg"))
    assert written, "build emitted no SVGs to check"
    for path in written:
        try:
            ET.fromstring(path.read_text(encoding="utf-8"))
        except ET.ParseError as e:
            raise AssertionError(f"{path.name} is not well-formed XML: {e}") from e


def test_hero_plots_no_contribution_field_and_still_derives_the_figures():
    """The unit field is gone on purpose; this stops it coming back unnoticed.

    It drew one mark per contribution, shaded by calendar month. The encoding
    was real and illegible: two bands at 0.60 and 0.34 opacity with 1-unit
    month rules, on a 1200 viewBox that renders at 0.33x on a phone, which is
    2.0px of pitch. Thomas read it as "all the dots under my name doesn\'t make
    sense" on 2026-09-19 and it was removed rather than relabelled.

    This is not the old assertion loosened. The old one counted the marks and
    the marks are gone, so counting them can only be rewritten or deleted --
    and deleting it would leave nothing to notice a field quietly returning,
    which is the failure this file exists to catch. So it asserts the opposite
    fact, and separately that the record itself did *not* leave: the four
    figures are still derived here, and build.py sets them in markdown where
    they are legible at every width.
    """
    from generators.svg import hero

    spec = [("2026-07-%02d" % i, 3) for i in range(1, 11)] + \
           [("2026-08-%02d" % i, 5) for i in range(1, 11)]
    contrib = _contrib(spec)
    svg = hero.render("NAME", contrib)

    # Each mark was one "h.01" segment, and nothing else in the hero emits one.
    assert "h.01" not in svg, "the per-contribution field is back in the hero"
    # A field of 2,774 marks was most of the plate's height; 144 units is the
    # name, its rule and the planet, and nothing below them.
    assert 'viewBox="0 0 1200 144"' in svg

    figures = hero.readout_figures(contrib)
    assert [caption for _, caption in figures] == [
        "contributions", "days active", "busiest day", "longest streak"]
    assert figures[0][0] == "80" == f"{contrib['total']}"


def test_tokenless_build_reproduces_the_tokened_one(tmp_path, monkeypatch):
    """The contributions cache exists so `make build` is offline-reproducible.

    Before it, a build with no token silently dropped the contributions data
    and rewrote README.md without it, so every local run and every Stop-hook
    gate left the tree dirty against what CI publishes.
    """
    # build(token=None) means "read GITHUB_TOKEN from the environment", so
    # without this the second build picks up a real token when one is
    # exported and quietly goes to the network instead of to the cache.
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    orbit = _write_orbit(tmp_path)
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps({
        "owner": "thomasvanpul", "repo": "thomasvanpul", "branch": "main",
        "featured": [{
            "name": "some-repo", "description": "desc", "language": "Python",
            "topics": ["profile-feature"],
            "url": "https://github.com/thomasvanpul/some-repo",
            "default_branch": "main", "pushed_at": "2026-08-01T00:00:00Z",
            "profile_config": {},
        }],
    }), encoding="utf-8")

    api_repo = {
        "name": "some-repo", "html_url": "https://github.com/thomasvanpul/some-repo",
        "default_branch": "main", "description": "desc", "language": "Python",
        "topics": ["profile-feature"], "pushed_at": "2026-08-01T00:00:00Z",
        "archived": False, "fork": False,
    }
    contribs = _contrib([("2026-07-%02d" % i, i) for i in range(1, 29)])

    live = tmp_path / "live"
    (live / "assets").mkdir(parents=True)
    with patch.object(gh, "fetch_featured_repos", return_value=[api_repo]), \
         patch.object(gh, "fetch_profile_config", return_value=None), \
         patch.object(gh, "fetch_contributions", return_value=contribs):
        build.build(fixture_path=fixture, orbit_path=orbit, out_dir=live,
                    token="fake-token")
    tokened = (live / "README.md").read_text(encoding="utf-8")
    # That the contributions actually reached the render, checked without the
    # unit field, which used to be the proof and was removed on 2026-09-19.
    # What still encodes them in the hero is the planet: six rings, one per
    # month, each drawn for its share of the busiest of the six. So a hero
    # built with this data must differ from one built with none.
    hero_svg = next((live / "assets").glob("hero.*.svg")).read_text(encoding="utf-8")
    from generators.svg import hero as hero_mod
    assert hero_svg != hero_mod.render(content.HERO_NAME, None), (
        "the hero is identical with and without contributions, so nothing in "
        "it carries them any more")
    assert "stroke-dasharray" in hero_svg
    # The figures those marks added up to live in the README, because inside
    # the plate they rendered at 7.8px on a phone.
    assert "days active" in tokened

    # Second build, no token, reading the cache the first one committed.
    build.build(fixture_path=fixture, orbit_path=orbit, out_dir=live, token=None)
    assert (live / "README.md").read_text(encoding="utf-8") == tokened


def test_every_asset_paints_the_page_it_lands_on_before_it_draws():
    """A transparent asset is the defect this page was first rejected for; a
    plate in a colour the page is not is the defect it was rejected for next.

    `make build` and the XML check both pass on an SVG with no ground, so
    nothing in the suite could tell "paints a ground" from "paints nothing".
    This can, and it now also pins *which* ground. Every asset used to paint
    `field-light-edge`, Atrium's outer field tone, which measures 6.36 from
    GitHub's dark canvas in CIELAB at almost the same lightness -- close enough
    to look like a mistake and far enough to read as a brown slab on a
    blue-grey page. The ground is the canvas itself now, and it flips with the
    reader's theme.

    Checked here rather than by eye: the ground is painted, it is painted
    *first* (a ground after the marks hides them), it carries a light-scheme
    rule, and the ink is `currentColor` so one media query can move a whole
    asset.
    """
    import re

    from generators.svg import GROUND_DARK, GROUND_LIGHT, INK_LIGHT, field, figures, flow, halftone, hero, orbit, token

    ground = field().strip()
    first_mark = re.compile(r"<(path|circle|text|line|ellipse|g)\b")

    rendered = {
        "hero": hero.render("NAME", None),
        "orbit": orbit.render([{"items": ["a", "b"], "rx": 40, "ry": 10, "duration": 8.0}]),
        "figures": figures.render("1", "CAP", "aria"),
        "flow": flow.render([("A", "a"), ("B", "b")]),
        "halftone": halftone.render({"cols": 2, "rows": 2, "cells": "9090"}, "aria"),
    }
    for name, svg in rendered.items():
        assert ground in svg, f"{name} draws on no field at all"
        mark = first_mark.search(svg)
        assert mark, f"{name} drew nothing"
        assert svg.index(ground) < mark.start(), (
            f"{name} paints its field after its marks, which hides them")
        assert GROUND_DARK in svg and GROUND_LIGHT in svg, (
            f"{name} has no light scheme, so on a light page it is a black slab")
        assert "prefers-color-scheme: light" in svg, f"{name} never asks the reader"
        assert token(INK_LIGHT) in svg, f"{name} has no light-theme ink"
        assert 'fill="#' not in svg and 'stroke="#' not in svg, (
            f"{name} writes a colour into a mark; ink travels as currentColor so "
            f"that one media query can move the whole asset")


# The whole page gets one moving thing. Nine small ones is what "no
# animations" looked like: every animation on the rejected page was under 1%
# of its plate's width, so at a 358px phone column none of them was more than
# two pixels of travel.
MAX_ANIMATIONS_ON_THE_PAGE = 1


def test_the_page_moves_exactly_once_and_can_be_told_not_to(tmp_path):
    """One animation, in CSS, with the off switch somewhere it actually works.

    Two things are pinned here and the second one cost a rewrite. SMIL cannot
    be gated on `prefers-reduced-motion` -- it has no media query -- so every
    `<animate>` is a defect twice over, and this counts them.

    And a `@media (prefers-reduced-motion: reduce)` block *inside* an asset is
    not a guard at all. An `<img>`-referenced SVG is told the reader's colour
    scheme and is not told their motion preference: the same file under the
    same emulated `reduce` matches the rule when opened as a document and never
    matches it through an `<img>`, measured in Chromium both ways. So the
    switch is a `<source media>` in the README, where the page evaluates it,
    and the still it points at has to actually be still.
    """
    import re

    out_dir = _seed_real_build(tmp_path)
    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    smil, moving = [], []
    for asset in sorted((out_dir / "assets").glob("*.svg")):
        body = asset.read_text(encoding="utf-8")
        if re.search(r"<animate(Motion|Transform)?\b", body):
            smil.append(asset.name)
        moving += [asset.name] * len(re.findall(r"animation:\s*(?!none\b)\w", body))
        assert "prefers-reduced-motion" not in body, (
            f"{asset.name} guards itself with a query an <img> never evaluates; "
            f"the switch belongs in the README")

    assert not smil, (
        "SMIL animation cannot be stopped by prefers-reduced-motion: "
        + ", ".join(smil))
    assert len(moving) <= MAX_ANIMATIONS_ON_THE_PAGE, (
        f"{len(moving)} things move on this page: " + ", ".join(moving))
    assert moving, "nothing moves at all, which is the other half of the complaint"

    assert '<source media="(prefers-reduced-motion: reduce)"' in readme, (
        "the page moves and never offers a way out of it")
    still = [a for a in (out_dir / "assets").glob("hero-still.*.svg")]
    assert len(still) == 1, "no still hero for the reduced-motion source to point at"
    assert still[0].name in readme
    assert "animation:" not in still[0].read_text(encoding="utf-8"), (
        "the still hero animates, so reduce gets the same movement by another name")


def test_vendored_tokens_match_atrium_design_when_it_is_checked_out():
    """`data/atrium-tokens.json` is a copy, and a copy can go stale.

    It is vendored rather than imported so this repo builds in CI with no
    sibling checkout, which is the right trade — but it means the palette can
    drift from the Swift it claims to come from and nothing would say so.
    When `~/dev/atrium-design` is present, compare; when it is not, skip,
    because CI cannot see it and a test that fails on a missing sibling repo
    is a test that gets deleted.
    """
    import os
    from pathlib import Path

    import pytest

    upstream = Path(
        os.environ.get("ATRIUM_DESIGN", "~/dev/atrium-design")
    ).expanduser() / "tokens" / "tokens.json"
    if not upstream.is_file():
        pytest.skip(f"atrium-design not checked out at {upstream}")

    vendored = Path(__file__).resolve().parent.parent / "data" / "atrium-tokens.json"
    assert vendored.read_text(encoding="utf-8") == upstream.read_text(encoding="utf-8"), (
        "data/atrium-tokens.json has drifted from atrium-design; "
        "re-run `python3 bin/generate.py` there and copy tokens/tokens.json across"
    )


def _seed_real_build(tmp_path: Path) -> Path:
    """Build the page the repo actually ships, into a scratch directory.

    The caches in `data/` are copied rather than read in place: a tokenless
    build rewrites the contributions and showroom caches it loaded, and a test
    must not be able to touch the committed ones.
    """
    import shutil

    repo = Path(__file__).resolve().parent.parent
    out_dir = tmp_path / "out"
    (out_dir / "assets").mkdir(parents=True)
    shutil.copytree(repo / "data", out_dir / "data")
    shutil.copytree(repo / "showroom", out_dir / "showroom")
    build.build(fixture_path=out_dir / "data" / "repos.sample.json",
                orbit_path=out_dir / "data" / "orbit.json",
                out_dir=out_dir, token=None)
    return out_dir


# GitHub's profile column, as `bin/page_preview.py` renders it: max-width
# minus its 16px padding either side.
DESKTOP_COLUMN = 1012 - 32
PHONE_COLUMN = 390 - 32

# The smallest text GitHub itself renders on this page is <sub>, at 12px. A
# mark this page draws should not be smaller than the smallest mark GitHub
# draws, and 11px leaves a pixel of slack for a rasteriser's rounding.
MIN_APPARENT_PX = 11.0


def test_no_asset_sets_type_too_small_to_read_on_a_phone(tmp_path):
    """The defect the page was rejected for three times, as a number.

    A README asset is a fixed-ratio image inside a fluid column, so its type
    scales with the column and markdown's does not. At a 1200-unit viewBox in
    a 358px phone column that is 0.30x: the hero's readout row was set at 26px
    and read at 7.8px, its captions at 9px and read at 2.7px. Sixteen of the
    eighteen distinct type sizes on the rejected page rendered below 8px.

    Width is the divisor, so this cannot be fixed by "using a bigger font" --
    it is fixed by narrowing the plate or by moving the words out of it, and
    both happened. This pins the result: any text a generator draws has to be
    at least 3.07% of its own viewBox width, whatever width that plate is
    built at.

    It runs against the assets a real build emits, not against the generators,
    so a plate rendered at a new width is covered the moment it ships.
    """
    import re

    out_dir = _seed_real_build(tmp_path)
    font_px = re.compile(r"font:\s*\d+\s+([\d.]+)px")
    view_box = re.compile(r'viewBox="0 0 ([\d.]+) [\d.]+"')

    offenders = []
    checked = 0
    for asset in sorted((out_dir / "assets").glob("*.svg")):
        body = asset.read_text(encoding="utf-8")
        vb = view_box.search(body)
        assert vb, f"{asset.name} has no viewBox"
        width = float(vb.group(1))
        scale = min(1.0, PHONE_COLUMN / width)
        for size in {float(m) for m in font_px.findall(body)}:
            checked += 1
            apparent = size * scale
            if apparent < MIN_APPARENT_PX:
                offenders.append(
                    f"{asset.name}: {size:g}px in a {width:g} viewBox reads at "
                    f"{apparent:.1f}px in a {PHONE_COLUMN}px column "
                    f"({size / width * 100:.2f}% of the plate, floor is "
                    f"{MIN_APPARENT_PX / PHONE_COLUMN * 100:.2f}%)")

    assert checked, "found no type at all, so this test proved nothing"
    assert not offenders, "type too small to read on a phone:\n  " + "\n  ".join(offenders)


def test_the_page_carries_its_figures_as_text(tmp_path):
    """Every number a reader needs has to survive Ctrl-F and a screen reader.

    GitHub never sees text inside an <img>-referenced SVG: not its own search,
    not the browser's find, not a copy-paste. A screen reader gets one `alt`
    string for the whole plate, with no headings and no links inside it. So
    the line drawn here is that a plate carries marks and at most one large
    number, and every figure a reader is meant to *read* is markdown.

    This asserts the figures that moved out of the hero and out of the Atrium
    strip are in README.md and not only in an asset.
    """
    out_dir = _seed_real_build(tmp_path)
    readme = (out_dir / "README.md").read_text(encoding="utf-8")

    for figure in ("contributions", "longest streak",
                   "218,016", "10 MB", "418"):
        assert figure in readme, f"{figure!r} is only inside a plate"
