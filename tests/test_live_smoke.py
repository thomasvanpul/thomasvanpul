"""Live smoke test — exercises the real discovery path against api.github.com.

This exists because the mocked unit suite passed in every CI run while the live
call 403'd on /user/repos (installation token cannot hit that endpoint). Any
future regression that breaks the actual discovery path — wrong endpoint,
wrong token scope, wrong query parameters — must be caught here before the
build step runs.

Skipped when GITHUB_TOKEN is absent (local runs without an exported token).
"""
from __future__ import annotations

import os

import pytest

from generators import github as gh


requires_token = pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"),
    reason="requires GITHUB_TOKEN (Actions installation token or a PAT)",
)


@requires_token
def test_live_discovery_returns_at_least_one_featured_repo():
    token = os.environ["GITHUB_TOKEN"]
    featured = gh.fetch_featured_repos(token, "thomasvanpul")
    assert featured, (
        "expected >=1 public repo with topic 'profile-feature' on thomasvanpul; "
        "got 0 — either the topic is missing from every repo or discovery is broken"
    )
    for r in featured:
        assert r.get("archived") is False
        assert r.get("fork") is False
        assert "profile-feature" in (r.get("topics") or [])


@requires_token
def test_live_contributions_query_works_with_installation_token():
    """`user(login:)` must be reachable with GITHUB_TOKEN.

    The previous query used `viewer`, which requires a user token. Under the
    Actions installation token that returned no viewer and the panel would
    have failed. Guard against a regression back to `viewer`.
    """
    token = os.environ["GITHUB_TOKEN"]
    stats = gh.fetch_contributions(token, "thomasvanpul")
    assert set(stats.keys()) == {"total", "current_streak", "longest_streak"}
    assert isinstance(stats["total"], int)
    assert stats["total"] >= 0
    assert isinstance(stats["current_streak"], int)
    assert isinstance(stats["longest_streak"], int)
    # A live account with a public README-repo push history should have some
    # activity in the last 12 months; a zero here means either the query is
    # aimed at the wrong user or the calendar came back empty.
    assert stats["total"] > 0, "expected at least one contribution in the last 12 months"
