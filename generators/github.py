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


def fetch_featured_repos(token: str) -> list[dict]:
    """Return the authenticated user's opt-in featured repos.

    Featured = topic 'profile-feature', not archived, not a fork.
    Sorted by pushed_at descending for deterministic ordering.
    """
    url = f"{API_BASE}/user/repos?per_page=100&type=owner&sort=pushed"
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
