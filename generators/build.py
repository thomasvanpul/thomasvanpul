"""Build README.md and assets/ from the picked hero and live GitHub data.

Since 2026-09-24 the page is the corridor Thomas picked (`content.HERO_PICK`,
built by `bin/hero.py` into `design/hero/<pick>/assets/`) and under it name,
one line, links. Nothing on it is drawn from GitHub data any more. The data
is still loaded, because the daily CI run is what keeps
`data/contributions.json` fresh, and `bin/field_data.py` reads that cache to
lay out the corridor's substrate the next time the plate is rebuilt.

Order of operations, deliberately strict so we never publish a half-built
profile:

  1. Load repo data (live via API when GITHUB_TOKEN is present, else fixture).
  2. Validate we ended up with >= 1 featured repo. Otherwise raise BuildError.
  3. Read the four hero files, name them by content hash, render the README.
  4. Only then touch disk: write assets, write README, delete orphans.

Any failure in steps 1-3 raises BuildError and leaves README.md and assets/
exactly as they were on disk.

The SVG generators under `generators/svg/` and `generators/showroom.py` are no
longer called from here. They are left in place, as the orbit plate was, so
the measured page of 19 Sep can be reinstated from git rather than rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from . import content
from . import corridor
from . import github as gh

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPOS_FIXTURE = REPO_ROOT / "data" / "repos.sample.json"
DEFAULT_ORBIT_CONFIG = REPO_ROOT / "data" / "orbit.json"
DEFAULT_OUT = REPO_ROOT
DEFAULT_HERO_DIR = REPO_ROOT / "design" / "hero" / content.HERO_PICK / "assets"

# The four files a finish in design/hero/ consists of, by stem. The animated
# pair is GIF or APNG, whichever `animate.encode` found smaller; the stills
# are always PNG.
HERO_STEMS = ("still-dark", "still-light", "anim-dark", "anim-light")

# Profile repo coordinates (used to build raw.githubusercontent URLs in README).
PROFILE_OWNER = "thomasvanpul"
PROFILE_REPO = "thomasvanpul"
PROFILE_BRANCH = "main"


class BuildError(RuntimeError):
    pass


def _sha7(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:7]


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


def hero_picture(urls: dict[str, str], alt: str) -> str:
    """One element carrying four images: two themes times motion or not.

    A reader with reduced motion set gets the still for their theme, which is
    why those two sources come first -- a browser takes the first source that
    matches, and `prefers-reduced-motion` has to beat `prefers-color-scheme`
    rather than lose to it. The light animation is the bare `img`, so a client
    that understands none of this still gets a picture rather than alt text.

    The switch is out here and not inside the asset because an
    `<img>`-referenced file is told the reader's colour scheme and is not told
    their motion preference, measured in Chromium both ways on 2026-09-19. A
    `<source media>` is the page's own CSS, so the page evaluates it.

    `bin/hero.py` writes the same block into `design/hero/<finish>/README.md`
    through this function, so a finish previews exactly what shipping it
    would publish.
    """
    return "\n".join([
        "<picture>",
        '  <source media="(prefers-reduced-motion: reduce) and '
        f'(prefers-color-scheme: dark)" srcset="{urls["still-dark"]}">',
        '  <source media="(prefers-reduced-motion: reduce)" '
        f'srcset="{urls["still-light"]}">',
        '  <source media="(prefers-color-scheme: dark)" '
        f'srcset="{urls["anim-dark"]}">',
        f'  <img alt="{alt}" src="{urls["anim-light"]}">',
        "</picture>",
    ])


def _load_hero(hero_dir: Path) -> dict[str, tuple[bytes, str]]:
    """The picked finish's four files: {stem: (bytes, extension)}.

    Exactly one file per stem, or BuildError: a finish half-rebuilt by an
    interrupted `bin/hero.py` has two animations or none, and either would
    otherwise ship as a README pointing at a file that is not there.
    """
    out: dict[str, tuple[bytes, str]] = {}
    for stem in HERO_STEMS:
        found = sorted(hero_dir.glob(f"{stem}.*"))
        if len(found) != 1:
            raise BuildError(
                f"expected one {stem}.* in {hero_dir}, found "
                f"{[f.name for f in found] or 'none'}; run `python3 bin/hero.py "
                f"{content.HERO_PICK}`")
        out[stem] = (found[0].read_bytes(), found[0].suffix.lstrip("."))
    return out


def _hash_hero(hero: dict[str, tuple[bytes, str]]) -> dict[str, str]:
    """{stem: filename}. The hash is of the bytes, recomputed, never trusted
    from the source filename: a renamed file must not ship under a name that
    does not match what is in it, because raw.githubusercontent caches by
    name."""
    return {stem: f"{stem}.{hashlib.sha256(data).hexdigest()[:7]}.{ext}"
            for stem, (data, ext) in hero.items()}


def _render_readme(data: dict, filenames: dict[str, str]) -> str:
    """The page, top to bottom: the corridor, then name, one line, links.

    Three headings, two tables, four plates and a snake came off on
    2026-09-24 with the pick. They were the page arguing in prose for what
    the corridor now shows: every mark on it is a real commit and the panel
    names the repository. The rule that survives from the old page is the
    one about text: nothing a reader needs is inside an image. The name, the
    line and the three links are markdown, so GitHub search, Ctrl-F, a
    screen reader and a copy-paste all get them.
    """
    urls = {stem: _raw_url(data["owner"], data["repo"], data["branch"], name)
            for stem, name in filenames.items()}
    return "\n".join([
        hero_picture(urls, corridor.ALT[content.HERO_PICK]), "",
        f"# {content.NAME}", "",
        content.LINE, "",
        content.FOOTER_LINKS, "",
    ])


def _write_all(out_dir: Path, hero: dict[str, tuple[bytes, str]],
               filenames: dict[str, str], readme: str,
               contributions: dict | None = None,
               cache_path: Path | None = None) -> tuple[list[Path], list[Path]]:
    if cache_path is not None and contributions is not None \
            and contributions.get("days"):
        _write_contrib_cache(cache_path, contributions)
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    kept: set[Path] = set()
    for stem, (body, _ext) in hero.items():
        path = assets_dir / filenames[stem]
        path.write_bytes(body)
        kept.add(path)
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    removed = []
    # Every asset the old page shipped was an SVG; the corridor is GIF, APNG
    # and PNG. All four kinds are orphans when the README stops naming them.
    for existing in sorted(assets_dir.iterdir()):
        if existing.suffix in (".svg", ".gif", ".png") and existing not in kept:
            existing.unlink()
            removed.append(existing)
    return sorted(kept), sorted(removed)


def build(fixture_path: Path = DEFAULT_REPOS_FIXTURE,
          orbit_path: Path = DEFAULT_ORBIT_CONFIG,
          out_dir: Path = DEFAULT_OUT,
          token: str | None = None,
          cache_path: Path | None = None,
          hero_dir: Path = DEFAULT_HERO_DIR) -> list[Path]:
    if token is None:
        token = os.environ.get("GITHUB_TOKEN") or None
    # Relative to out_dir, never to REPO_ROOT: a test building into tmp_path
    # must not be able to rewrite the repo's own committed cache.
    if cache_path is None:
        cache_path = out_dir / "data" / "contributions.json"

    data = _load_data(token, fixture_path, orbit_path, cache_path)
    _validate(data)
    hero = _load_hero(hero_dir)
    filenames = _hash_hero(hero)
    readme = _render_readme(data, filenames)

    written, removed = _write_all(out_dir, hero, filenames, readme,
                                  data.get("contributions"), cache_path)
    for r in removed:
        print(f"removed  {r.relative_to(out_dir)}", file=sys.stderr)
    for w in written:
        print(f"wrote    {w.relative_to(out_dir)}  "
              f"{w.stat().st_size / 1024:.0f} KB", file=sys.stderr)
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
