"""Minimal GitHub API client for the profile build.

Uses urllib to avoid a runtime dependency on `requests`. Raises `GitHubError`
on any HTTP or network failure so build.py can bail out and leave existing
assets untouched.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Iterator

import yaml

API_BASE = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"
FEATURE_TOPIC = "profile-feature"
UA = "thomasvanpul-profile-builder"


class GitHubError(RuntimeError):
    pass


def _http_get(url: str, token: str, accept: str) -> tuple[int, bytes, dict]:
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "User-Agent": UA,
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read() or b"", dict(e.headers)
    except urllib.error.URLError as e:
        raise GitHubError(f"network error for {url}: {e.reason}")


def _json_get(url: str, token: str) -> tuple[list | dict, dict]:
    status, body, headers = _http_get(url, token, "application/vnd.github+json")
    if status == 403 and b"rate limit" in body.lower():
        raise GitHubError(f"rate limited on {url}")
    if status >= 400:
        raise GitHubError(f"HTTP {status} for {url}: {body[:200].decode(errors='replace')}")
    if not body:
        return [], headers
    return json.loads(body), headers


def _paginate(url: str, token: str) -> Iterator[dict]:
    next_url = url
    while next_url:
        data, headers = _json_get(next_url, token)
        if not isinstance(data, list):
            raise GitHubError(f"expected list from {next_url}, got {type(data).__name__}")
        yield from data
        next_url = _next_link(headers.get("Link", ""))


def _next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        part = part.strip()
        if 'rel="next"' not in part:
            continue
        segments = part.split(";")
        if not segments:
            continue
        url = segments[0].strip()
        if url.startswith("<") and url.endswith(">"):
            return url[1:-1]
    return None


def fetch_featured_repos(token: str, owner: str = "thomasvanpul") -> list[dict]:
    """Return `owner`'s opt-in featured public repos.

    Featured = topic 'profile-feature', not archived, not a fork.
    Pre-sorted by pushed_at descending; final ordering is applied in build.py
    after each repo's .profile.yml weight is known.

    Uses GET /users/{owner}/repos rather than /user/repos so this works with
    the Actions installation token (`GITHUB_TOKEN`), which is not a user and
    cannot hit /user/repos. That endpoint choice also makes the
    public-repos-only property STRUCTURAL rather than conventional: the
    /users/{owner}/repos endpoint only ever returns public repos, so no PAT
    misconfiguration downstream can widen what this build sees.
    """
    url = f"{API_BASE}/users/{owner}/repos?per_page=100&type=owner&sort=pushed"
    all_repos = list(_paginate(url, token))
    featured = [
        r for r in all_repos
        if FEATURE_TOPIC in (r.get("topics") or [])
        and not r.get("archived")
        and not r.get("fork")
    ]
    featured.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    return featured


def fetch_profile_config(token: str, owner: str, repo: str, branch: str) -> dict | None:
    """Return parsed .profile.yml from the repo's default branch, or None.

    None means: file missing, empty, malformed, or not a mapping. A warning is
    logged for the malformed cases; this never raises so the plain card path
    keeps working.
    """
    url = f"{API_BASE}/repos/{owner}/{repo}/contents/.profile.yml?ref={branch}"
    status, body, _ = _http_get(url, token, "application/vnd.github.raw")
    if status == 404:
        return None
    if status >= 400:
        raise GitHubError(f"HTTP {status} fetching .profile.yml for {owner}/{repo}")
    if not body.strip():
        return None
    try:
        cfg = yaml.safe_load(body)
    except yaml.YAMLError as e:
        print(f"warning: malformed .profile.yml in {owner}/{repo}: {e}", file=sys.stderr)
        return None
    if not isinstance(cfg, dict):
        print(f"warning: .profile.yml in {owner}/{repo} is not a mapping", file=sys.stderr)
        return None
    return cfg


# ---- Contributions (GraphQL) ---------------------------------------------

# NOTE on `restrictedContributionsCount` (deliberately omitted): the field is
# viewer-relative — it counts contributions the *viewer* cannot see. When the
# viewer is the profile owner (any token I own), the owner can see everything,
# so the field is structurally 0 regardless of token scope. GitHub already
# folds private commits into contributionCalendar.totalContributions for the
# owner, so the total is complete. No separate "PRIVATE" figure is obtainable
# for an owner-scoped call, and the earlier three-vs-four column diagnostic
# was a misread.
#
# NOTE on `user(login:)` vs `viewer`: `viewer` requires the query to be run as
# a user, which the Actions installation token (GITHUB_TOKEN) is not. Using
# `user(login:)` makes the same calendar totals reachable with GITHUB_TOKEN,
# so the build no longer needs a second classic PAT for this call.
_CONTRIB_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
""".strip()


def _graphql(token: str, query: str, variables: dict | None = None) -> dict:
    payload: dict = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    body = json.dumps(payload).encode()
    req = urllib.request.Request(GRAPHQL_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise GitHubError(f"GraphQL HTTP {e.code}: {e.read()[:200].decode(errors='replace')}")
    except urllib.error.URLError as e:
        raise GitHubError(f"GraphQL network error: {e.reason}")
    if payload.get("errors"):
        raise GitHubError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def _flatten_days(calendar: dict) -> list[dict]:
    """Return chronological [{date, count}, ...] from a contributionCalendar."""
    days: list[dict] = []
    for week in calendar.get("weeks") or []:
        for day in week.get("contributionDays") or []:
            days.append({"date": day["date"], "count": day["contributionCount"]})
    return days


def current_streak(days: list[dict]) -> int:
    """Consecutive-non-zero days ending at the most recent day.

    A blank most-recent day gets one grace (the day may not be over yet); any
    zero after we've started counting terminates the streak.
    """
    streak = 0
    grace = 1
    for day in reversed(days):
        if day["count"] > 0:
            streak += 1
            grace = 0
        elif grace > 0:
            grace -= 1
        else:
            break
    return streak


def longest_streak(days: list[dict]) -> int:
    best = 0
    run = 0
    for day in days:
        if day["count"] > 0:
            run += 1
            if run > best:
                best = run
        else:
            run = 0
    return best


def fetch_contributions(token: str, owner: str = "thomasvanpul") -> dict:
    """Return contribution stats for `owner`, last 12 months.

    Keys: total, current_streak, longest_streak.

    Per-repo counts are deliberately not returned. calendar totals and
    streaks are safe because they come from the server's per-day totals
    rather than from repo enumeration. See the query comment for why
    restrictedContributionsCount is not fetched.

    Raises GitHubError on any HTTP, network, or GraphQL failure.
    """
    data = _graphql(token, _CONTRIB_QUERY, {"login": owner})
    cc = data["user"]["contributionsCollection"]
    days = _flatten_days(cc["contributionCalendar"])
    return {
        "total": cc["contributionCalendar"]["totalContributions"],
        "current_streak": current_streak(days),
        "longest_streak": longest_streak(days),
    }
