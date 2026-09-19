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
from . import showroom
from .svg import THEMES, figures, flow, halftone, hero, orbit

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


def _read_contrib_cache(cache_path: Path) -> dict | None:
    """Rebuild the contributions payload from the committed day series.

    Returns None when the cache is missing or unreadable — the caller then
    builds without a contributions panel, which is what happened on every
    tokenless build before this cache existed.
    """
    if not cache_path.exists():
        return None
    try:
        raw = json.loads(cache_path.read_text(encoding="utf-8"))
        return gh.summarise(raw["total"], raw["days"])
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"warning: ignoring unreadable {cache_path.name}: {e}", file=sys.stderr)
        return None


def _write_contrib_cache(cache_path: Path, contributions: dict) -> None:
    """Store only the two irreducible fields; everything else is derived.

    Storing the derived figures too would let the cache disagree with itself
    if `summarise` ever changes, and a cache that can lie is worse than no
    cache.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"total": contributions["total"], "days": contributions["days"]},
                   indent=1) + "\n",
        encoding="utf-8",
    )


def _load_showrooms(token: str | None, data_dir: Path) -> dict[str, dict]:
    """Load one luminance grid per configured showroom.

    Same rule as the contributions cache: a token-bearing build re-ingests
    from source and rewrites the cache, a tokenless one replays what is
    committed. The token is not needed to *reach* the images — they are
    public — it is used as the signal for "this is the authoritative build",
    so a local preview never silently produces a page CI would not.
    """
    grids: dict[str, dict] = {}
    for name, cfg in content.SHOWROOMS.items():
        cache = data_dir / f"showroom-{_flow_id(name)}.json"
        grid = None
        local = cfg.get("path")
        # A local source needs no token: the gate on `token` exists because the
        # original showroom fetched from the network, and an offline build had
        # to fall back to the cached grid. A committed still is always readable.
        if local or token:
            if local:
                # A showroom whose source lives in this repo. Private repos
                # cannot be fetched, so the still is committed here instead.
                src = (REPO_ROOT / local).read_bytes() if (REPO_ROOT / local).exists() else None
                grid = showroom.ingest("", cfg["cols"], cfg.get("crop"), source_bytes=src)
            else:
                grid = showroom.ingest(cfg["url"], cfg["cols"], cfg.get("crop"))
        if grid is None:
            grid = showroom.read_cache(cache)
        if grid is not None:
            grids[name] = grid
    return grids


def _load_data(token: str | None, fixture_path: Path, orbit_path: Path,
               cache_path: Path) -> dict:
    """Load the unified data dict. Raises BuildError on any failure.

    Both repo discovery and the contributions GraphQL call now run against
    GITHUB_TOKEN — the discovery endpoint is /users/{owner}/repos (public,
    installation-token-friendly) and the contributions query targets
    user(login:) rather than viewer, so it too works with the installation
    token. This is why the previous PROFILE_STATS_TOKEN split is gone.

    If token is absent (local `make preview` without an exported token) the
    build loads the repo fixture and replays the contributions day series
    from data/contributions.json, which the last tokened build committed.

    That cache is the reason `make build` now reproduces the committed page
    offline. Before it existed, a tokenless build silently dropped the
    contributions panel and rewrote README.md without it, so every local
    session — and the Stop-hook gate, which runs without a token — left the
    tree dirty with a page that did not match what CI publishes.
    """
    orbit_cfg = json.loads(orbit_path.read_text(encoding="utf-8"))

    if token:
        try:
            raw = gh.fetch_featured_repos(token, PROFILE_OWNER)
        except gh.GitHubError as e:
            raise BuildError(f"failed to fetch repos: {e}") from e
        # Short-circuit the empty-discovery case before spending a GraphQL
        # call on contributions — _validate would raise anyway, and this
        # keeps the "no featured repos" test independent of contributions
        # mocking.
        if not raw:
            raise BuildError("no featured repos (topic 'profile-feature' matched 0 repos)")
        featured = [_repo_from_api(r, token) for r in raw]
        try:
            contributions = gh.fetch_contributions(token, PROFILE_OWNER)
        except gh.GitHubError as e:
            raise BuildError(f"failed to fetch contributions: {e}") from e
        data = {
            "owner": PROFILE_OWNER,
            "repo": PROFILE_REPO,
            "branch": PROFILE_BRANCH,
            "featured": featured,
            "orbit": orbit_cfg,
            "contributions": contributions,
        }
    else:
        cached = _read_contrib_cache(cache_path)
        print("no GITHUB_TOKEN, loading fixture (contributions from cache)"
              if cached else
              "no GITHUB_TOKEN and no contributions cache (panel skipped)",
              file=sys.stderr)
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        data["orbit"] = orbit_cfg
        data["contributions"] = cached

    data["featured"] = _sort_featured(data["featured"])
    data["showrooms"] = _load_showrooms(token, cache_path.parent)
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
        theme: hero.render(theme, content.HERO_NAME, content.HERO_SUBTITLES,
                           data.get("contributions"))
        for theme in THEMES
    }
    variants["orbit"] = {
        theme: orbit.render(theme, data["orbit"]["rings"]) for theme in THEMES
    }
    variants["atrium-figures"] = {
        theme: figures.render(theme, content.ATRIUM["lede_number"],
                              content.ATRIUM["lede_caption"],
                              content.ATRIUM["figures"],
                              content.ATRIUM["figures_aria"])
        for theme in THEMES
    }

    featured_names = {e["name"] for e in data["featured"]}
    for name, grid in (data.get("showrooms") or {}).items():
        # Atrium is its own section rather than a featured repo, so it is not in
        # featured_names and would be skipped. Its showroom is still wanted.
        if name not in featured_names and name != "atrium":
            continue
        variants[f"showroom-{_flow_id(name)}"] = {
            theme: halftone.render(theme, grid, content.SHOWROOMS[name]["aria"])
            for theme in THEMES
        }

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


def _body_paragraphs(entry: dict) -> tuple[str, list[str], str]:
    """Return (heading, paragraphs, repo_line) for a featured repo."""
    prose = content.FEATURED.get(entry["name"])
    heading = prose["heading"] if prose else entry["name"]
    body = prose["body"] if prose else (entry.get("description") or "").strip()
    paras = list(body) if isinstance(body, list) else ([body] if body else [])
    repo_line = f'Repo: [`{entry["name"]}`]({entry["url"]})'
    if prose and prose.get("repo_suffix"):
        repo_line += f' &nbsp;·&nbsp; {prose["repo_suffix"]}'
    return heading, paras, repo_line


def _flow_picture(entry: dict, filenames: dict[str, dict[str, str]], data: dict) -> str | None:
    cfg = entry.get("profile_config") or {}
    if cfg.get("diagram") != "flow" or not cfg.get("stages"):
        return None
    basename = f"flow-{_flow_id(entry['name'])}"
    if basename not in filenames:
        return None
    prose = content.FEATURED.get(entry["name"])
    stages = cfg["stages"]
    alt = prose["flow_aria"] if prose else (
        f"{entry['name']} flow: " + " to ".join(st[0] for st in stages))
    dark, light = _url_pair(data, filenames, basename)
    return _picture(dark, light, alt)


def _url_pair(data: dict, filenames: dict[str, dict[str, str]], basename: str) -> tuple[str, str]:
    f = filenames[basename]
    return (
        _raw_url(data["owner"], data["repo"], data["branch"], f["dark"]),
        _raw_url(data["owner"], data["repo"], data["branch"], f["light"]),
    )


def _showroom_card(entry: dict, filenames: dict[str, dict[str, str]], data: dict) -> str:
    """Shape one: the object first.

    A repo whose whole point is a physical thing should show the thing before
    it explains itself. The render carries more than the first paragraph does,
    so it goes above the fold of the section and the prose follows it.
    """
    heading, paras, repo_line = _body_paragraphs(entry)
    cfg = content.SHOWROOMS[entry["name"]]
    dark, light = _url_pair(data, filenames, f"showroom-{_flow_id(entry['name'])}")
    lines = [f"### {heading}\n", '<div align="center">\n',
             _picture(dark, light, cfg["aria"]),
             f'\n<sub>{cfg["caption"]}</sub>\n', "</div>\n"]
    lines.extend(para + "\n" for para in paras)
    flow = _flow_picture(entry, filenames, data)
    if flow:
        lines.append(flow + "\n")
    lines.append(repo_line + "\n")
    return "\n".join(lines)


def _prose_card(entry: dict, filenames: dict[str, dict[str, str]], data: dict) -> str:
    """Shape two: the argument first, the diagram as evidence.

    Numeris is interesting because of what daily use did to it, and that is a
    claim in words. The flow diagram is the supporting exhibit, so it sits
    between the claim and the consequence rather than at the top.
    """
    heading, paras, repo_line = _body_paragraphs(entry)
    lines = [f"### {heading}\n"]
    if paras:
        lines.append(paras[0] + "\n")
    flow = _flow_picture(entry, filenames, data)
    if flow:
        lines.append(flow + "\n")
    lines.extend(para + "\n" for para in paras[1:])
    lines.append(repo_line + "\n")
    return "\n".join(lines)


def _plain_card(entry: dict) -> str:
    """Fallback for a featured repo with neither a showroom nor a diagram."""
    heading, paras, repo_line = _body_paragraphs(entry)
    lines = [f"### {heading}\n"]
    lines.extend(para + "\n" for para in paras)
    lines.append(repo_line + "\n")
    return "\n".join(lines)


def _atrium_card(filenames: dict[str, dict[str, str]], data: dict) -> str:
    """Shape three: the measurement first.

    Atrium has no public repo to link and no diagram worth drawing at this
    size. What it has is figures, so the section opens with them and the prose
    explains what they are. The third paragraph is the honest-state paragraph
    and is not optional — see Atlas/Projects/Atrium/Verified-Record.md.
    """
    a = content.ATRIUM
    show_dark, show_light = _url_pair(data, filenames, "showroom-atrium")
    dark, light = _url_pair(data, filenames, "atrium-figures")
    cfg = content.SHOWROOMS.get("atrium", {})
    lines = [f"### {a['heading']}\n", '<div align="center">\n',
             _picture(show_dark, show_light, cfg.get("aria", "")),
             f'\n<sub>{cfg.get("caption", "")}</sub>\n', "</div>\n",
             _picture(dark, light, a["figures_aria"]) + "\n"]
    lines.extend(para + "\n" for para in a["body"])
    lines.append(a["repo_line"] + "\n")
    return "\n".join(lines)


def _render_readme(data: dict, filenames: dict[str, dict[str, str]]) -> str:
    hero_dark, hero_light = _url_pair(data, filenames, "hero")
    orbit_dark, orbit_light = _url_pair(data, filenames, "orbit")

    lines: list[str] = []
    lines.append('<div align="center">\n')
    lines.append(_picture(hero_dark, hero_light, content.HERO_ARIA))
    lines.append("\n</div>\n")
    lines.append(content.INTRO + "\n")

    # Sections are separated by their own shape, not by a repeated ornament.
    # The six rule.svg references that used to sit between them were one
    # cached request, not six, but they were also the same mark six times
    # carrying nothing — which is the objection that actually mattered.
    for entry in data["featured"]:
        cfg = entry.get("profile_config") or {}
        has_showroom = entry["name"] in (data.get("showrooms") or {})
        if has_showroom and f"showroom-{_flow_id(entry['name'])}" in filenames:
            lines.append(_showroom_card(entry, filenames, data))
        elif cfg.get("diagram") == "flow" and cfg.get("stages"):
            lines.append(_prose_card(entry, filenames, data))
        else:
            lines.append(_plain_card(entry))
        lines.append("---\n")

    lines.append(_atrium_card(filenames, data))
    lines.append("---\n")

    lines.append(f"### {content.ALSO_RUNNING_HEADING}\n")
    for title, prose in content.ALSO_RUNNING:
        lines.append(f"**{title}** &nbsp;·&nbsp; {prose}\n")
    lines.append("---\n")

    lines.append(f"### {content.STACK_HEADING}\n")
    lines.append('<div align="center">\n')
    lines.append(_picture(orbit_dark, orbit_light, content.STACK_ORBIT_ARIA))
    lines.append("\n</div>\n")
    lines.append("---\n")

    lines.append('<div align="center">\n')
    lines.append(_picture(content.SNAKE_DARK_URL, content.SNAKE_LIGHT_URL, content.SNAKE_ARIA))
    lines.append("\n")
    lines.append(f"<sub>{content.FOOTER_SUB}</sub>\n")
    lines.append(content.FOOTER_LINKS + "\n")
    lines.append("</div>")

    return "\n".join(lines) + "\n"


def _write_all(out_dir: Path, variants: dict[str, dict[str, str]],
               filenames: dict[str, dict[str, str]], readme: str,
               contributions: dict | None = None,
               cache_path: Path | None = None,
               showrooms: dict[str, dict] | None = None) -> tuple[list[Path], list[Path]]:
    if cache_path is not None:
        if contributions is not None and contributions.get("days"):
            _write_contrib_cache(cache_path, contributions)
        for name, grid in (showrooms or {}).items():
            showroom.write_cache(
                cache_path.parent / f"showroom-{_flow_id(name)}.json", grid)
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
          cache_path: Path | None = None) -> list[Path]:
    if token is None:
        token = os.environ.get("GITHUB_TOKEN") or None
    # Relative to out_dir, never to REPO_ROOT: a test building into tmp_path
    # must not be able to rewrite the repo's own committed cache.
    if cache_path is None:
        cache_path = out_dir / "data" / "contributions.json"

    data = _load_data(token, fixture_path, orbit_path, cache_path)
    _validate(data)
    variants = _render_svgs_in_memory(data)
    filenames = _hash_variants(variants)
    readme = _render_readme(data, filenames)

    written, removed = _write_all(out_dir, variants, filenames, readme,
                                  data.get("contributions"), cache_path,
                                  data.get("showrooms"))
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
