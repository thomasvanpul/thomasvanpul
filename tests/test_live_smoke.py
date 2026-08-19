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


@pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"),
    reason="requires GITHUB_TOKEN (Actions installation token or a PAT)",
)
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
