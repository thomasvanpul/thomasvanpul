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




FAKE_HERO = {
    "still-dark": ("png", b"\x89PNG dark still"),
    "still-light": ("png", b"\x89PNG light still"),
    "anim-dark": ("gif", b"GIF89a dark"),
    "anim-light": ("gif", b"GIF89a light"),
}


def _fake_hero(tmp: Path) -> Path:
    """A finish's four files, tiny, under a hash the build must not trust."""
    d = tmp / "hero"
    d.mkdir()
    for stem, (ext, body) in FAKE_HERO.items():
        (d / f"{stem}.0000000.{ext}").write_bytes(body)
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

    # A half-rebuilt finish -- two animations, or none -- must not ship.
    (tmp_path / "hero" / "anim-dark.1111111.gif").write_bytes(b"GIF89a second")
    with pytest.raises(build.BuildError, match="expected one anim-dark"):
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


def test_the_page_moves_exactly_once_and_can_be_told_not_to(tmp_path):
    """One animation, with the off switch somewhere it actually works.

    A `@media (prefers-reduced-motion: reduce)` block *inside* an asset is
    not a guard: an `<img>`-referenced file is told the reader's colour scheme
    and is not told their motion preference, measured in Chromium both ways on
    2026-09-19. So the switch is a `<source media>` in the README, it comes
    before the colour-scheme sources so it wins, and the still it points at
    is a PNG, which cannot move. And the snake is gone with the old page: the
    corridor is the one thing that moves, in either theme.
    """
    out_dir = _seed_real_build(tmp_path)
    readme = (out_dir / "README.md").read_text(encoding="utf-8")

    assert readme.count("<picture>") == 1 and readme.count("<img ") == 1, (
        "the page shows more than one image")
    assert "/output/" not in readme, "the snake is back, so two things move"
    sources = re.findall(r'<source media="([^"]+)" srcset="[^"]*/assets/([^"]+)">',
                         readme)
    assert [m for m, _ in sources][:2] == [
        "(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)",
        "(prefers-reduced-motion: reduce)",
    ], "reduced motion has to be offered before a colour scheme, or it loses"
    for _media, name in sources[:2]:
        assert name.endswith(".png"), f"the reduced-motion source {name} can move"
        assert (out_dir / "assets" / name).is_file()
    assert not list((out_dir / "assets").glob("*.svg")), (
        "an SVG from the old page survived the build")


# GitHub's profile column, as `bin/page_preview.py` renders it: max-width
# minus its 16px padding either side.
PHONE_COLUMN = 390 - 32

# The smallest text GitHub itself renders on a page is <sub>, at 12px. A
# mark this page draws should not be smaller than the smallest mark GitHub
# draws, and 11px leaves a pixel of slack for a rasteriser's rounding.
MIN_APPARENT_PX = 11.0

# The task's ceiling for each animated file. A README image is fetched on
# every visit and raw.githubusercontent does not stream a GIF, so the plate
# is paid for in full before a frame shows.
HERO_BUDGET_BYTES = 1500 * 1024


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
        if path.name.startswith("anim-"):
            assert len(data) <= HERO_BUDGET_BYTES, (
                f"{path.name} is {len(data) / 1024:.0f} KB, over "
                f"{HERO_BUDGET_BYTES // 1024} KB")


def test_the_page_carries_its_text_as_text(tmp_path):
    """Everything a reader needs has to survive Ctrl-F and a screen reader.

    GitHub never sees text inside an image: not its own search, not the
    browser's find, not a copy-paste. A screen reader gets one `alt` string
    for the whole plate. So the name, the line and the links are markdown,
    and the alt says what the plate shows rather than naming it.
    """
    out_dir = _seed_real_build(tmp_path)
    readme = (out_dir / "README.md").read_text(encoding="utf-8")

    assert f"# {content.NAME}\n" in readme
    assert content.LINE in readme
    for link in ("https://thomasvp.com", "linkedin.com/in/vanpulthomas",
                 "vanpulthomas@gmail.com"):
        assert link in readme, f"{link!r} is not on the page"
    assert f'alt="{corridor.ALT[content.HERO_PICK]}"' in readme
    assert readme.count("\n#") == 1, "more than one heading on a page of three lines"


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


