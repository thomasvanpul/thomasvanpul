"""Build README.md and the SVG assets from live GitHub data (or fixture).

Order of operations, deliberately strict so we never publish a half-built
profile:

  1. Load repo data (live via API when GITHUB_TOKEN is present, else fixture).
  2. Fetch per-repo .profile.yml for each featured repo.
  3. Validate we ended up with >= 1 featured repo. Otherwise raise BuildError.
  4. Render every SVG + README in memory.
  5. Only then touch disk: write assets, write README, delete orphans.

Any failure in steps 1-4 raises BuildError and leaves README.md and assets/
exactly as they were on disk.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from . import content
from . import github as gh
from .svg import THEMES, flow, hero, orbit, rule, stats

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPOS_FIXTURE = REPO_ROOT / "data" / "repos.sample.json"
DEFAULT_ORBIT_CONFIG = REPO_ROOT / "data" / "orbit.json"
DEFAULT_OUT = REPO_ROOT

# Profile repo coordinates (used to build raw.githubusercontent URLs in README).
PROFILE_OWNER = "thomasvanpul"
PROFILE_REPO = "thomasvanpul"
PROFILE_BRANCH = "main"


class BuildError(RuntimeError):
    pass


def _sha7(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:7]


def _flow_id(repo_name: str) -> str:
    """Derive a filesystem-safe flow id from a repo name."""
    return re.sub(r"[^a-z0-9]+", "-", repo_name.lower()).strip("-")


def _load_data(token: str | None, stats_token: str | None,
               fixture_path: Path, orbit_path: Path) -> dict:
    """Load the unified data dict. Raises BuildError on any failure."""
    orbit_cfg = json.loads(orbit_path.read_text(encoding="utf-8"))

    if token:
        try:
            raw = gh.fetch_featured_repos(token)
        except gh.GitHubError as e:
            raise BuildError(f"failed to fetch repos: {e}") from e
        featured = [_repo_from_api(r, token) for r in raw]
        data = {
            "owner": PROFILE_OWNER,
            "repo": PROFILE_REPO,
            "branch": PROFILE_BRANCH,
            "featured": featured,
            "orbit": orbit_cfg,
        }
    else:
        print("no GITHUB_TOKEN, loading fixture", file=sys.stderr)
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        data["orbit"] = orbit_cfg

    data["featured"] = _sort_featured(data["featured"])

    if stats_token:
        try:
            data["contributions"] = gh.fetch_contributions(stats_token)
        except gh.GitHubError as e:
            raise BuildError(f"failed to fetch contributions: {e}") from e
    else:
        # In CI the panel is required — the whole point of the split token
        # is to make CI output deterministic. Allowing a token-absent commit
        # would flip-flop the panel in and out of the README as the secret
        # gets added/removed. Local runs skip the panel so `make preview`
        # still works offline.
        if os.environ.get("GITHUB_ACTIONS") == "true":
            raise BuildError(
                "PROFILE_STATS_TOKEN not set in CI — refusing to publish a "
                "README without the contributions panel (would flip-flop). "
                "Add the secret or unset GITHUB_ACTIONS to skip locally."
            )
        print("no PROFILE_STATS_TOKEN, skipping contributions panel (local run)",
              file=sys.stderr)
        data["contributions"] = None

    return data


def _sort_featured(featured: list[dict]) -> list[dict]:
    """Sort by weight ascending, then pushed_at descending as a tie-break.

    Weight comes from each repo's .profile.yml. Repos with no weight sort
    after all weighted repos and are tie-broken by pushed_at desc, which
    matches the fetch order.
    """
    # Two passes leaning on the stable sort: establish pushed_at desc first,
    # then a stable weight-bucket sort preserves it within each bucket.
    by_pushed = sorted(featured, key=lambda e: e.get("pushed_at") or "", reverse=True)

    def bucket(entry: dict) -> tuple[int, int]:
        cfg = entry.get("profile_config") or {}
        weight = cfg.get("weight")
        if isinstance(weight, int):
            return (0, weight)
        return (1, 0)

    return sorted(by_pushed, key=bucket)


def _repo_from_api(api_repo: dict, token: str) -> dict:
    """Normalise a /user/repos entry and attach its .profile.yml, if any."""
    name = api_repo["name"]
    default_branch = api_repo.get("default_branch") or "main"
    try:
        cfg = gh.fetch_profile_config(token, PROFILE_OWNER, name, default_branch)
    except gh.GitHubError as e:
        raise BuildError(f"failed to fetch .profile.yml for {name}: {e}") from e
    return {
        "name": name,
        "description": api_repo.get("description"),
        "language": api_repo.get("language"),
        "topics": api_repo.get("topics") or [],
        "url": api_repo["html_url"],
        "default_branch": default_branch,
        "pushed_at": api_repo.get("pushed_at"),
        "profile_config": cfg,
    }


def _validate(data: dict) -> None:
    featured = data.get("featured") or []
    if not featured:
        raise BuildError("no featured repos (topic 'profile-feature' matched 0 repos)")


def _raw_url(owner: str, repo: str, branch: str, asset: str) -> str:
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/assets/{asset}"


def _picture(dark_url: str, light_url: str, alt: str) -> str:
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="{dark_url}">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="{light_url}">\n'
        f'  <img alt="{alt}" src="{dark_url}">\n'
        "</picture>"
    )


def _render_svgs_in_memory(data: dict) -> dict[str, dict[str, str]]:
    """Return {basename: {theme: svg_body}}. Pure function, no disk writes."""
    variants: dict[str, dict[str, str]] = {}

    variants["hero"] = {
        theme: hero.render(theme, content.HERO_NAME, content.HERO_SUBTITLES)
        for theme in THEMES
    }
    variants["rule"] = {theme: rule.render(theme) for theme in THEMES}
    variants["orbit"] = {
        theme: orbit.render(theme, data["orbit"]["rings"]) for theme in THEMES
    }
    contrib = data.get("contributions")
    if contrib is not None:
        variants["stats"] = {theme: stats.render(theme, contrib) for theme in THEMES}

    for entry in data["featured"]:
        cfg = entry.get("profile_config") or {}
        diagram = cfg.get("diagram", "none")
        if diagram != "flow":
            continue
        stages_raw = cfg.get("stages") or []
        if len(stages_raw) < 2:
            print(
                f"warning: {entry['name']} has diagram: flow but <2 stages, skipping diagram",
                file=sys.stderr,
            )
            continue
        stages = [tuple(s) for s in stages_raw]
        side_input = None
        si = cfg.get("side_input")
        if si and len(si) >= 2:
            side_input = {"label": si[0], "sublabel": si[1], "connects_to": 1}
        basename = f"flow-{_flow_id(entry['name'])}"
        variants[basename] = {
            theme: flow.render(theme, stages, None, side_input) for theme in THEMES
        }

    return variants


def _hash_variants(variants: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """Turn {basename: {theme: body}} into {basename: {theme: filename}}."""
    out: dict[str, dict[str, str]] = {}
    for basename, per_theme in variants.items():
        out[basename] = {}
        for theme, body in per_theme.items():
            digest = _sha7(body)
            out[basename][theme] = f"{basename}.{digest}-{theme}.svg"
    return out


def _plain_card(entry: dict) -> str:
    """Fallback card for a featured repo without a flow diagram."""
    prose = content.FEATURED.get(entry["name"])
    heading = prose["heading"] if prose else entry["name"]
    body = prose["body"] if prose else (entry.get("description") or "").strip()
    lines = [f"### {heading}\n"]
    if isinstance(body, list):
        for para in body:
            lines.append(para + "\n")
    elif body:
        lines.append(body + "\n")
    repo_line = f'Repo: [`{entry["name"]}`]({entry["url"]})'
    if prose and prose.get("repo_suffix"):
        repo_line += f' &nbsp;·&nbsp; {prose["repo_suffix"]}'
    lines.append(repo_line + "\n")
    return "\n".join(lines)


def _flow_card(entry: dict, filenames: dict[str, dict[str, str]], data: dict) -> str:
    prose = content.FEATURED.get(entry["name"])
    heading = prose["heading"] if prose else entry["name"]
    body = prose["body"] if prose else (entry.get("description") or "").strip()
    basename = f"flow-{_flow_id(entry['name'])}"
    dark = _raw_url(data["owner"], data["repo"], data["branch"], filenames[basename]["dark"])
    light = _raw_url(data["owner"], data["repo"], data["branch"], filenames[basename]["light"])

    stages = entry["profile_config"]["stages"]
    default_alt = f"{entry['name']} flow: " + " to ".join(s[0] for s in stages)
    alt = prose["flow_aria"] if prose else default_alt

    lines = [f"### {heading}\n"]
    if isinstance(body, list):
        lines.append(body[0] + "\n")
    elif body:
        lines.append(body + "\n")
    lines.append(_picture(dark, light, alt) + "\n")
    if isinstance(body, list) and len(body) > 1:
        for extra in body[1:]:
            lines.append(extra + "\n")
    repo_line = f'Repo: [`{entry["name"]}`]({entry["url"]})'
    if prose and prose.get("repo_suffix"):
        repo_line += f' &nbsp;·&nbsp; {prose["repo_suffix"]}'
    lines.append(repo_line + "\n")
    return "\n".join(lines)


def _render_readme(data: dict, filenames: dict[str, dict[str, str]]) -> str:
    owner, repo, branch = data["owner"], data["repo"], data["branch"]

    def url_pair(basename: str) -> tuple[str, str]:
        f = filenames[basename]
        return (
            _raw_url(owner, repo, branch, f["dark"]),
            _raw_url(owner, repo, branch, f["light"]),
        )

    hero_dark, hero_light = url_pair("hero")
    rule_dark, rule_light = url_pair("rule")
    orbit_dark, orbit_light = url_pair("orbit")
    rule_block = _picture(rule_dark, rule_light, "")

    lines: list[str] = []
    lines.append('<div align="center">\n')
    lines.append(_picture(hero_dark, hero_light, content.HERO_ARIA))
    lines.append("\n</div>\n")
    lines.append(content.INTRO + "\n")
    lines.append(rule_block + "\n")

    for entry in data["featured"]:
        cfg = entry.get("profile_config") or {}
        if cfg.get("diagram") == "flow" and cfg.get("stages"):
            lines.append(_flow_card(entry, filenames, data))
        else:
            lines.append(_plain_card(entry))
        lines.append(rule_block + "\n")

    lines.append(f"### {content.ALSO_RUNNING_HEADING}\n")
    for title, prose in content.ALSO_RUNNING:
        lines.append(f"**{title}** &nbsp;·&nbsp; {prose}\n")
    lines.append(rule_block + "\n")

    lines.append(f"### {content.STACK_HEADING}\n")
    lines.append('<div align="center">\n')
    lines.append(_picture(orbit_dark, orbit_light, content.STACK_ORBIT_ARIA))
    lines.append("\n</div>\n")
    lines.append(rule_block + "\n")

    lines.append('<div align="center">\n')
    if "stats" in filenames:
        stats_dark, stats_light = url_pair("stats")
        lines.append(_picture(stats_dark, stats_light, content.STATS_ARIA))
        lines.append("\n")
    lines.append(_picture(content.SNAKE_DARK_URL, content.SNAKE_LIGHT_URL, content.SNAKE_ARIA))
    lines.append("\n")
    lines.append(f"<sub>{content.FOOTER_SUB}</sub>\n")
    lines.append(content.FOOTER_LINKS + "\n")
    lines.append("</div>")

    return "\n".join(lines) + "\n"


def _write_all(out_dir: Path, variants: dict[str, dict[str, str]],
               filenames: dict[str, dict[str, str]], readme: str) -> tuple[list[Path], list[Path]]:
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    kept: set[Path] = set()
    for basename, per_theme in variants.items():
        for theme, body in per_theme.items():
            path = assets_dir / filenames[basename][theme]
            path.write_text(body, encoding="utf-8")
            kept.add(path)
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    removed = []
    for existing in assets_dir.glob("*.svg"):
        if existing not in kept:
            existing.unlink()
            removed.append(existing)
    return sorted(kept), sorted(removed)


def build(fixture_path: Path = DEFAULT_REPOS_FIXTURE,
          orbit_path: Path = DEFAULT_ORBIT_CONFIG,
          out_dir: Path = DEFAULT_OUT,
          token: str | None = None,
          stats_token: str | None = None) -> list[Path]:
    if token is None:
        token = os.environ.get("GITHUB_TOKEN") or None
    if stats_token is None:
        stats_token = os.environ.get("PROFILE_STATS_TOKEN") or None

    data = _load_data(token, stats_token, fixture_path, orbit_path)
    _validate(data)
    variants = _render_svgs_in_memory(data)
    filenames = _hash_variants(variants)
    readme = _render_readme(data, filenames)

    written, removed = _write_all(out_dir, variants, filenames, readme)
    for r in removed:
        print(f"removed  {r.relative_to(out_dir)}", file=sys.stderr)
    for w in written:
        print(f"wrote    {w.relative_to(out_dir)}", file=sys.stderr)
    print("wrote    README.md", file=sys.stderr)
    return written + [out_dir / "README.md"]


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture", type=Path, default=DEFAULT_REPOS_FIXTURE)
    p.add_argument("--orbit", type=Path, default=DEFAULT_ORBIT_CONFIG)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        build(args.fixture, args.orbit, args.out)
    except BuildError as e:
        print(f"build failed: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
