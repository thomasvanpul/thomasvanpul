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

    def boom(_token):
        raise gh.GitHubError("HTTP 502 for /user/repos: bad gateway")

    with patch.object(gh, "fetch_featured_repos", side_effect=boom):
        with pytest.raises(build.BuildError, match="failed to fetch repos"):
            build.build(fixture_path=fixture, orbit_path=orbit,
                        out_dir=out_dir, token="fake-token")

    _assert_unchanged(snapshot)


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
