"""Build README.md and assets/ from the project cards and live GitHub data.

Since 2026-10-12 nothing on the page moves. Thomas: "i dont want it to be
animation i want it to be interactive". The page is one still of the corridor
(the lead card's), then name, line, links, a line the daily run rewrites from
real push data, and one `<details>` card per project that a visitor opens.
Every picture is a link. The stills are drawn by `bin/cards.py` into
`design/cards/`; this module only reads, hashes and ships them.

The history below is the page this replaced, kept because it still explains
the data loading and the order of operations, which are unchanged.

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
DEFAULT_HERO_DIR = REPO_ROOT / "design" / "cards"

# The files the page ships, by stem: one still per card per theme, all PNG.
# There is no animated stem any more, and `_write_all` sweeps any GIF left in
# assets/ from the corridor page as an orphan.
THEMES = ("dark", "light")
HERO_STEMS = tuple(f"{key}-{theme}" for key in content.CARDS for theme in THEMES)

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
               cache_path: Path, activity_path: Path | None = None) -> dict:
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
    if activity_path is None:
        activity_path = cache_path.parent / "activity.json"

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
    data["latest"] = _latest_push(data["featured"], token, activity_path)
    return data


def _latest_push(featured: list[dict], token: str | None,
                 activity_path: Path) -> dict | None:
    """The most recently pushed featured public repo: name, url, pushed_at.

    This is the one line on the page that changes on its own. It is read off
    the repo list the build already fetches, so it costs no API call, and
    only public repos can appear in it because that list is
    /users/{owner}/repos. A tokened build stores it in data/activity.json and
    a tokenless one replays that file, for the same reason the contributions
    cache exists: `make build` has to write the page CI last wrote. With no
    token and no cache it falls back to the fixture.
    """
    if not token and activity_path.exists():
        try:
            got = json.loads(activity_path.read_text(encoding="utf-8"))
            if {"name", "url", "pushed_at"} <= set(got):
                return got
        except json.JSONDecodeError as e:
            print(f"warning: ignoring unreadable {activity_path.name}: {e}",
                  file=sys.stderr)
    dated = [r for r in featured if r.get("pushed_at")]
    if not dated:
        return None
    top = max(dated, key=lambda r: r["pushed_at"])
    return {"name": top["name"], "url": top["url"], "pushed_at": top["pushed_at"]}


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
    """Every card still: {stem: (bytes, extension)}.

    Exactly one file per stem, or BuildError: a set half-rebuilt by an
    interrupted `bin/cards.py` has two stills for a card or none, and either
    would otherwise ship as a README pointing at a file that is not there.
    """
    out: dict[str, tuple[bytes, str]] = {}
    for stem in HERO_STEMS:
        found = sorted(hero_dir.glob(f"{stem}.*"))
        if len(found) != 1:
            raise BuildError(
                f"expected one {stem}.* in {hero_dir}, found "
                f"{[f.name for f in found] or 'none'}; run `python3 bin/cards.py`")
        out[stem] = (found[0].read_bytes(), found[0].suffix.lstrip("."))
    return out


def _hash_hero(hero: dict[str, tuple[bytes, str]]) -> dict[str, str]:
    """{stem: filename}. The hash is of the bytes, recomputed, never trusted
    from the source filename: a renamed file must not ship under a name that
    does not match what is in it, because raw.githubusercontent caches by
    name."""
    return {stem: f"{stem}.{hashlib.sha256(data).hexdigest()[:7]}.{ext}"
            for stem, (data, ext) in hero.items()}


def still_picture(dark: str, light: str, alt: str, href: str | None) -> str:
    """A still in both themes, as a link when there is somewhere to go.

    GitHub keeps `<a>`, `<picture>`, `<source>` and `<img>` through its
    sanitiser and drops `style` and `script`, so this is the whole of what an
    image on a README can do: be the right colour and be clickable. Light is
    the bare `img`, so a client that ignores `<source>` still gets a picture.
    """
    pic = "\n".join([
        "<picture>",
        f'  <source media="(prefers-color-scheme: dark)" srcset="{dark}">',
        f'  <img alt="{alt}" src="{light}" width="820">',
        "</picture>",
    ])
    return f'<a href="{href}">\n{pic}\n</a>' if href else pic


def card_alt(key: str, counts: dict, field: dict) -> str:
    """What the still shows, in words, from the counts it was drawn from."""
    card = content.CARDS[key]
    return (f"A still of one year of real commits, {field['from']} to {field['to']}, "
            f"drawn as a corridor and docked on the {card['lane_alt']} lane: "
            f"{counts['commits']:,} commits touching {counts['files_touched']:,} files, "
            f"in {counts['weeks']} of 53 weeks. Every mark above a lane is one commit.")


def _repo_url(data: dict, name: str) -> str:
    for r in data.get("featured") or []:
        if r.get("name") == name and r.get("url"):
            return r["url"]
    return f"https://github.com/{data['owner']}/{name}"


def _latest_line(latest: dict | None) -> str | None:
    if not latest:
        return None
    return (f"<sub>Most recent push to a featured public repo: "
            f"<a href=\"{latest['url']}\">{latest['name']}</a>, "
            f"{latest['pushed_at'][:10]}. Updated daily by a GitHub Action.</sub>")


def _card(data: dict, key: str, urls: dict[str, str], counts: dict) -> str:
    """One project, closed until a visitor opens it.

    A blank line after `</summary>` is what makes GitHub render the inside
    as markdown rather than as a single run of literal text.
    """
    card = content.CARDS[key]
    out = ["<details>",
           f"<summary><b>{card['title']}</b> &nbsp;·&nbsp; {card['what']}</summary>", ""]
    repo = card.get("repo")
    href = _repo_url(data, repo) if repo else None
    if key != content.LEAD_CARD:
        out += [still_picture(urls[f"{key}-dark"], urls[f"{key}-light"],
                              card_alt(key, counts[key], counts["_field"]), href), ""]
    for para in card["body"]:
        out += [para, ""]
    if card.get("table"):
        head = card["table_head"]
        out += [f"| {head[0]} | {head[1]} |", "| --- | --- |"]
        out += [f"| {k} | {v} |" for k, v in card["table"]]
        out.append("")
    if repo:
        note = f": {card['repo_note']}" if card.get("repo_note") else ""
        out += [f"Repo: [{data['owner']}/{repo}]({href}){note}", ""]
    else:
        out += [card["links"], ""]
    out += ["</details>", ""]
    return "\n".join(out)


def _list_card(title: str, what: str, lines: list[str]) -> str:
    return "\n".join(["<details>",
                      f"<summary><b>{title}</b> &nbsp;·&nbsp; {what}</summary>", "",
                      *lines, "", "</details>", ""])


def _render_readme(data: dict, filenames: dict[str, str],
                   counts: dict | None = None) -> str:
    """The page, top to bottom.

    One still, the lead card's, linking to thomasvp.com. Name, line, links,
    and the push line the daily run rewrites. Then the projects, each a
    `<details>` a visitor opens, then the two lists that were cut on 24 Sep,
    back in the same words but closed, so the page a visitor lands on is
    still the short one.

    The rule from the corridor page holds: nothing a reader needs is inside
    an image. Every count a still shows is in its alt text, and every
    sentence is markdown.
    """
    counts = counts or _card_counts(DEFAULT_HERO_DIR)
    urls = {stem: _raw_url(data["owner"], data["repo"], data["branch"], name)
            for stem, name in filenames.items()}
    lead = content.LEAD_CARD
    lines = [still_picture(urls[f"{lead}-dark"], urls[f"{lead}-light"],
                           card_alt(lead, counts[lead], counts["_field"]), "https://thomasvp.com"), "",
             f"# {content.NAME}", "",
             content.LINE, "",
             content.FOOTER_LINKS, ""]
    latest = _latest_line(data.get("latest"))
    if latest:
        lines += [latest, ""]
    for key in content.CARDS:
        lines.append(_card(data, key, urls, counts))
    lines.append(_list_card(
        content.ALSO_RUNNING_HEADING, "four smaller things",
        [f"- **{name}**: {prose}" for name, prose in content.ALSO_RUNNING]))
    lines.append(_list_card(
        content.STACK_HEADING, "what I build with",
        ["| | |", "| --- | --- |",
         *[f"| {k} | {v} |" for k, v in content.STACK_TABLE]]))
    return "\n".join(lines)


def _card_counts(hero_dir: Path) -> dict:
    """The lane counts each still was drawn from, as `bin/cards.py` wrote them."""
    path = hero_dir / "cards.json"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return {key: doc[key] for key in (*content.CARDS, "_field")}
    except (OSError, json.JSONDecodeError, KeyError) as e:
        raise BuildError(f"cannot read {path}: {e}; run `python3 bin/cards.py`") from e


def _write_all(out_dir: Path, hero: dict[str, tuple[bytes, str]],
               filenames: dict[str, str], readme: str,
               contributions: dict | None = None,
               cache_path: Path | None = None,
               latest: dict | None = None,
               activity_path: Path | None = None) -> tuple[list[Path], list[Path]]:
    if cache_path is not None and contributions is not None \
            and contributions.get("days"):
        _write_contrib_cache(cache_path, contributions)
    if activity_path is not None and latest is not None:
        activity_path.parent.mkdir(parents=True, exist_ok=True)
        activity_path.write_text(json.dumps(latest, indent=1) + "\n", encoding="utf-8")
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    kept: set[Path] = set()
    for stem, (body, _ext) in hero.items():
        path = assets_dir / filenames[stem]
        path.write_bytes(body)
        kept.add(path)
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    removed = []
    # Every asset the old pages shipped was an SVG, a GIF, an APNG or a PNG.
    # All of them are orphans when the README stops naming them, which is how
    # the corridor's two 1.5 MB animations leave assets/.
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

    activity_path = cache_path.parent / "activity.json"
    data = _load_data(token, fixture_path, orbit_path, cache_path, activity_path)
    _validate(data)
    hero = _load_hero(hero_dir)
    filenames = _hash_hero(hero)
    readme = _render_readme(data, filenames, _card_counts(hero_dir))

    written, removed = _write_all(out_dir, hero, filenames, readme,
                                  data.get("contributions"), cache_path,
                                  data.get("latest"), activity_path)
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
