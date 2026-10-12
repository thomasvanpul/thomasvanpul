"""Safety tests for the profile builder."""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path
from unittest.mock import patch

import pytest

from generators import build
from generators import content
from generators import corridor
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
        tmp / "assets" / "anim-dark.deadbee.gif": "GIF89a previous",
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



def _contrib(days_spec: list[tuple[str, int]]) -> dict:
    return gh.summarise(sum(c for _d, c in days_spec),
                        [{"date": d, "count": c} for d, c in days_spec])




FAKE_HERO = {f"{key}-{theme}": ("png", f"\x89PNG {key} {theme}".encode())
             for key in content.CARDS for theme in ("dark", "light")}


def _fake_hero(tmp: Path) -> Path:
    """Every card still, tiny, under a hash the build must not trust, and the
    manifest `bin/cards.py` writes beside them."""
    d = tmp / "hero"
    d.mkdir()
    for stem, (ext, body) in FAKE_HERO.items():
        (d / f"{stem}.0000000.{ext}").write_bytes(body)
    manifest = {"_field": {"from": "2025-09-14", "to": "2026-09-19"}}
    manifest.update({key: {"commits": 1, "files_touched": 2, "weeks": 3}
                     for key in content.CARDS})
    (d / "cards.json").write_text(json.dumps(manifest), encoding="utf-8")
    return d


def _write_fixture(tmp: Path) -> Path:
    fixture = tmp / "fixture.json"
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
    return fixture


def test_hero_ships_under_its_content_hash_and_every_orphan_goes(tmp_path, monkeypatch):
    """The README names a file by the hash of what is in it, and nothing else
    stays in assets/.

    raw.githubusercontent caches by name, so a file that changed under a name
    that did not is the old file for as long as the cache likes. The hash is
    recomputed from the bytes rather than read off the source filename, which
    is what `_fake_hero` fakes with seven zeros. And the old page's SVGs, plus
    any earlier animation, are removed: the first orphan sweep only globbed
    `*.svg`, which would have left every superseded GIF on the branch forever.
    """
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    out_dir, _snapshot = _seed_out(tmp_path)
    build.build(fixture_path=_write_fixture(tmp_path), orbit_path=_write_orbit(tmp_path),
                out_dir=out_dir, token=None, hero_dir=_fake_hero(tmp_path))

    expected = {f"{stem}.{hashlib.sha256(body).hexdigest()[:7]}.{ext}"
                for stem, (ext, body) in FAKE_HERO.items()}
    assert {p.name for p in (out_dir / "assets").iterdir()} == expected
    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    for name in expected:
        assert f"/main/assets/{name}" in readme, f"{name} was written but never named"

    # A half-rebuilt set -- two stills for a card, or none -- must not ship.
    (tmp_path / "hero" / "atrium-dark.1111111.png").write_bytes(b"\x89PNG second")
    with pytest.raises(build.BuildError, match="expected one atrium-dark"):
        build.build(fixture_path=_write_fixture(tmp_path), orbit_path=_write_orbit(tmp_path),
                    out_dir=out_dir, token=None, hero_dir=tmp_path / "hero")


def test_tokenless_build_reproduces_the_tokened_one(tmp_path, monkeypatch):
    """`make build` with no token writes the page CI publishes, byte for byte.

    The page no longer draws anything from GitHub data, so this is now cheap
    to keep true and still worth pinning: the Stop-hook gate runs the build
    without a token, and a page that differed by token would leave every
    session's tree dirty. The tokened build must also still write the
    contributions cache, because that cache is what `bin/field_data.py` lays
    the corridor's substrate from.
    """
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    orbit = _write_orbit(tmp_path)
    fixture = _write_fixture(tmp_path)
    hero_dir = _fake_hero(tmp_path)

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
                    token="fake-token", hero_dir=hero_dir)
    tokened = (live / "README.md").read_text(encoding="utf-8")
    cache = json.loads((live / "data" / "contributions.json").read_text(encoding="utf-8"))
    assert len(cache["days"]) == 28, "the tokened build did not refresh the cache"

    build.build(fixture_path=fixture, orbit_path=orbit, out_dir=live, token=None,
                hero_dir=hero_dir)
    assert (live / "README.md").read_text(encoding="utf-8") == tokened


def _seed_real_build(tmp_path: Path) -> Path:
    """Build the page the repo actually ships, into a scratch directory.

    `data/` is copied rather than read in place: a tokenless build rewrites
    the contributions cache it loaded, and a test must not be able to touch
    the committed one. The hero is read from the committed finish under
    `design/hero/`, which is exactly what `make build` reads.
    """
    import shutil

    repo = Path(__file__).resolve().parent.parent
    out_dir = tmp_path / "out"
    (out_dir / "assets").mkdir(parents=True)
    shutil.copytree(repo / "data", out_dir / "data")
    build.build(fixture_path=out_dir / "data" / "repos.sample.json",
                orbit_path=out_dir / "data" / "orbit.json",
                out_dir=out_dir, token=None)
    return out_dir


def test_nothing_on_the_page_moves(tmp_path):
    """Thomas, 12 Oct 2026: "i dont want it to be animation i want it to be
    interactive".

    So every image the page ships is a PNG with no animation chunk (an APNG
    is a PNG with an `acTL` before its first `IDAT`), no GIF survives in
    assets/, and the snake, which moves, stays off.
    """
    out_dir = _seed_real_build(tmp_path)
    readme = (out_dir / "README.md").read_text(encoding="utf-8")

    assert "/output/" not in readme, "the snake is back, and it moves"
    assert "prefers-reduced-motion" not in readme, "there is motion to reduce"
    shipped = sorted((out_dir / "assets").iterdir())
    assert shipped, "the build shipped no images"
    for path in shipped:
        data = path.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a PNG"
        assert b"acTL" not in data[:data.index(b"IDAT")], f"{path.name} is an APNG"
        assert f"/main/assets/{path.name}" in readme, f"{path.name} shipped but unnamed"
    assert not list((out_dir / "assets").glob("*.svg")), (
        "an SVG from the old page survived the build")


def test_the_page_is_something_a_visitor_opens_and_clicks(tmp_path):
    """What "interactive" can mean on a README, pinned.

    GitHub runs no script on a profile and strips `style`, so the page's
    interaction is `<details>` a visitor opens and pictures that are links.
    Every project card is closed by default, every card still is inside an
    `<a>`, and the blank line after `</summary>` is there, because without it
    GitHub prints the card's markdown as literal text.
    """
    out_dir = _seed_real_build(tmp_path)
    readme = (out_dir / "README.md").read_text(encoding="utf-8")

    for banned in ("<script", "<style", "style=", "onclick", "<details open"):
        assert banned not in readme, f"{banned!r} is on the page; GitHub strips it"
    summaries = re.findall(r"<summary><b>([^<]+)</b>", readme)
    for card in content.CARDS.values():
        assert card["title"] in summaries, f"{card['title']} has no card"
    assert readme.count("<details>") == readme.count("</details>") == len(summaries)
    assert readme.count("</summary>\n\n") == len(summaries), (
        "a card has no blank line after its summary and will render as raw text")
    pictures = readme.count("<picture>")
    assert pictures == len(content.CARDS), "one still per card, the lead's at the top"
    assert len(re.findall(r'<a href="[^"]+">\n<picture>', readme)) == pictures, (
        "a picture is not a link")
    for card in content.CARDS.values():
        if card.get("repo"):
            assert f"https://github.com/thomasvanpul/{card['repo']}" in readme


def test_the_push_line_is_the_most_recent_featured_repo(tmp_path, monkeypatch):
    """The line the daily run rewrites names the newest push, from the repo
    list the build already fetched, and the tokened build caches it so a
    tokenless one prints the same line."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    older = {"name": "older", "html_url": "https://github.com/thomasvanpul/older",
             "default_branch": "main", "pushed_at": "2026-08-01T00:00:00Z",
             "topics": ["profile-feature"], "archived": False, "fork": False}
    newer = dict(older, name="newer", html_url="https://github.com/thomasvanpul/newer",
                 pushed_at="2026-10-11T09:00:00Z")
    out = tmp_path / "out"
    (out / "assets").mkdir(parents=True)
    hero_dir = _fake_hero(tmp_path)
    with patch.object(gh, "fetch_featured_repos", return_value=[older, newer]), \
         patch.object(gh, "fetch_profile_config", return_value=None), \
         patch.object(gh, "fetch_contributions",
                      return_value=_contrib([("2026-10-01", 1)])):
        build.build(fixture_path=_write_fixture(tmp_path),
                    orbit_path=_write_orbit(tmp_path),
                    out_dir=out, token="fake-token", hero_dir=hero_dir)
    readme = (out / "README.md").read_text(encoding="utf-8")
    line = '<a href="https://github.com/thomasvanpul/newer">newer</a>, 2026-10-11.'
    assert line in readme
    cached = json.loads((out / "data" / "activity.json").read_text(encoding="utf-8"))
    assert cached["name"] == "newer"

    build.build(fixture_path=_write_fixture(tmp_path), orbit_path=_write_orbit(tmp_path),
                out_dir=out, token=None, hero_dir=hero_dir)
    assert line in (out / "README.md").read_text(encoding="utf-8"), (
        "a tokenless build dropped the cached push line for the fixture's")


# GitHub's profile column, as `bin/page_preview.py` renders it: max-width
# minus its 16px padding either side.
PHONE_COLUMN = 390 - 32

# The smallest text GitHub itself renders on a page is <sub>, at 12px. A
# mark this page draws should not be smaller than the smallest mark GitHub
# draws, and 11px leaves a pixel of slack for a rasteriser's rounding.
MIN_APPARENT_PX = 11.0

# Ceiling per still. Each was a 1.5 MB GIF until 12 Oct; a still of the same
# plate is about 35 KB.
HERO_BUDGET_BYTES = 100 * 1024


def _png_size(data: bytes) -> tuple[int, int]:
    return struct.unpack(">II", data[16:24])


def _gif_size(data: bytes) -> tuple[int, int]:
    return struct.unpack("<HH", data[6:10])


def test_the_plate_reads_on_a_phone_and_fits_the_budget(tmp_path):
    """The defect the page was rejected for three times, as a number.

    A README image is a fixed-ratio image in a fluid column, so its type
    scales with the column and markdown's does not. The corridor is drawn at
    `corridor.WIDTH` units and lands in a 358px phone column, so every size
    it sets has to clear the 11px floor after that scale. `corridor._t`
    raises below `corridor.FLOOR` at draw time; this pins the two sizes it
    actually uses and the width the shipped files were really drawn at, so a
    plate rebuilt wider is caught the moment it ships.
    """
    out_dir = _seed_real_build(tmp_path)
    scale = PHONE_COLUMN / corridor.WIDTH
    for name, units in (("LABEL", corridor.LABEL), ("VALUE", corridor.VALUE)):
        assert units * scale >= MIN_APPARENT_PX, (
            f"corridor.{name} is {units:g} units, {units * scale:.1f}px on a phone")
    assert corridor.FLOOR * scale >= MIN_APPARENT_PX - 0.01

    for path in sorted((out_dir / "assets").iterdir()):
        data = path.read_bytes()
        width = (_gif_size(data) if data[:6] in (b"GIF87a", b"GIF89a")
                 else _png_size(data))[0]
        assert width == corridor.WIDTH, (
            f"{path.name} is {width} wide; the type floor was computed for "
            f"{corridor.WIDTH}")
        assert len(data) <= HERO_BUDGET_BYTES, (
            f"{path.name} is {len(data) / 1024:.0f} KB, over "
            f"{HERO_BUDGET_BYTES // 1024} KB")


def test_the_page_carries_its_text_as_text(tmp_path):
    """Everything a reader needs has to survive Ctrl-F and a screen reader.

    GitHub never sees text inside an image: not its own search, not the
    browser's find, not a copy-paste. A screen reader gets one `alt` string
    per plate. So the name, the line and the links are markdown, the alt
    carries every count the still draws, and the copy has no em dashes
    (Thomas's rule for anything written as him).
    """
    out_dir = _seed_real_build(tmp_path)
    readme = (out_dir / "README.md").read_text(encoding="utf-8")

    assert f"# {content.NAME}\n" in readme
    assert content.LINE in readme
    for link in ("https://thomasvp.com", "linkedin.com/in/vanpulthomas",
                 "vanpulthomas@gmail.com"):
        assert link in readme, f"{link!r} is not on the page"
    alts = re.findall(r'alt="([^"]+)"', readme)
    assert len(alts) == len(content.CARDS)
    for alt in alts:
        assert re.search(r"\d+ commits touching [\d,]+ files, in \d+ of 53 weeks", alt), alt
    assert "\u2014" not in readme, "an em dash is on the page"
    assert readme.count("\n# ") == 1, "more than one heading; cards are summaries, not headings"


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


