"""Safety tests for the profile builder."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from generators import build
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
        tmp / "assets" / "hero.deadbee-dark.svg": "<svg>previous</svg>",
        tmp / "assets" / "orbit.deadbee-dark.svg": "<svg>previous orbit</svg>",
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

    def boom(_token):
        raise gh.GitHubError("GraphQL HTTP 502: bad gateway")

    with patch.object(gh, "fetch_featured_repos", return_value=[api_repo]), \
         patch.object(gh, "fetch_profile_config", return_value=None), \
         patch.object(gh, "fetch_contributions", side_effect=boom):
        with pytest.raises(build.BuildError, match="failed to fetch contributions"):
            build.build(fixture_path=fixture, orbit_path=orbit, out_dir=out_dir,
                        token="fake-token", stats_token="fake-stats-token")

    _assert_unchanged(snapshot)


def test_ci_without_stats_token_fails_loudly(tmp_path, monkeypatch):
    """In CI, missing PROFILE_STATS_TOKEN must fail rather than skip the panel.

    Otherwise the README would flip-flop between having the panel and not
    having it every time the secret was added/removed.
    """
    out_dir, snapshot = _seed_out(tmp_path)
    orbit = _write_orbit(tmp_path)
    fixture = tmp_path / "unused.json"

    monkeypatch.setenv("GITHUB_ACTIONS", "true")

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
    with patch.object(gh, "fetch_featured_repos", return_value=[api_repo]), \
         patch.object(gh, "fetch_profile_config", return_value=None):
        with pytest.raises(build.BuildError, match="PROFILE_STATS_TOKEN not set in CI"):
            build.build(fixture_path=fixture, orbit_path=orbit, out_dir=out_dir,
                        token="fake-token", stats_token=None)

    _assert_unchanged(snapshot)


def test_local_without_stats_token_skips_panel(tmp_path, monkeypatch):
    """Same conditions locally: build succeeds, panel is skipped."""
    out_dir = tmp_path
    (out_dir / "assets").mkdir()
    orbit = _write_orbit(tmp_path)
    fixture = tmp_path / "unused.json"

    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

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
    with patch.object(gh, "fetch_featured_repos", return_value=[api_repo]), \
         patch.object(gh, "fetch_profile_config", return_value=None):
        build.build(fixture_path=fixture, orbit_path=orbit, out_dir=out_dir,
                    token="fake-token", stats_token=None)

    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    assert "assets/stats." not in readme
    assert "output/github-contribution-grid-snake" in readme


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

    with patch.object(gh, "fetch_featured_repos", return_value=[api_repo]), \
         patch.object(gh, "fetch_profile_config", return_value=None):
        build.build(fixture_path=fixture, orbit_path=orbit,
                    out_dir=out_dir, token="fake-token")

    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    assert "### plain-repo" in readme
    assert "A repo with no diagram config." in readme
    # No flow SVG should have been emitted for the plain repo.
    assert not any(p.name.startswith("flow-plain-repo") for p in (out_dir / "assets").iterdir())
