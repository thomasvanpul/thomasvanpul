#!/usr/bin/env python3
"""Reduce every region of the page to one week-aligned activity series.

Why this file exists
--------------------
`svg/lattice.py` draws one field for the whole page: a 53-column substrate
where a column is a calendar week, held at the same pitch and the same phase
in every band so the columns line up down the page. A field like that is only
honest if every column of every region is a real count, so the counts have to
come from somewhere and they have to be the same weeks everywhere.

They come from three places and none of them is fetched at build time:

* the contribution calendar already cached in `data/contributions.json`,
  which is the substrate -- every week of the year, all repositories, public
  and private,
* the GitHub API for the two public featured repositories,
* `git log` in the three local Atrium working copies, because Atrium is
  private and cannot be fetched. This is the same treatment
  `showroom/atrium-lattice.png` already gets: a private source reduced once,
  by hand, to the few numbers the page actually draws, and those numbers
  committed.

Run it when the counts are stale. `generators/` never runs it, never reaches
the network, and reads only the committed `data/field.json`, so the build
stays reproducible offline and CI does not depend on a private checkout
existing.

The week grid
-------------
Weeks are taken from the contribution series itself rather than from the
calendar, so the substrate and the lanes cannot drift apart: day 0 of
`contributions.json` opens week 0 and every seventh day after it opens the
next. The series is 370 days, so the last bucket is a short week of six days
and is marked as such rather than silently normalised.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRIB = ROOT / "data" / "contributions.json"
OUT = ROOT / "data" / "field.json"

# Atrium is three repositories, not one, and the page says "Atrium" for all
# three. Paths are local because the repositories are private; if one is
# missing the script says so and refuses rather than writing a short count.
ATRIUM_REPOS = {
    "surface": Path.home() / "dev" / "atrium-surface",
    "host": Path.home() / "dev" / "atrium-host",
    "design": Path.home() / "dev" / "atrium-design",
}

# The two public featured repositories, read through `gh`.
GH_REPOS = {
    "blueband-concept": "thomasvanpul/blueband-concept",
    "Finance-Tracker": "thomasvanpul/Finance-Tracker",
}


def _weeks(days: list[dict]) -> list[dict]:
    """Bucket the contribution series into 7-day weeks, in order."""
    out = []
    for start in range(0, len(days), 7):
        chunk = days[start:start + 7]
        out.append({
            "start": chunk[0]["date"],
            "days": len(chunk),
            "count": sum(d["count"] for d in chunk),
        })
    return out


def _index(weeks: list[dict]) -> tuple[date, int]:
    return date.fromisoformat(weeks[0]["start"]), len(weeks)


def _bucket(dates: list[str], origin: date, n: int) -> list[int]:
    """Commit timestamps to a per-week count on the substrate's grid."""
    counts = [0] * n
    for raw in dates:
        when = datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
        idx = (when - origin).days // 7
        if 0 <= idx < n:
            counts[idx] += 1
    return counts


def _git_dates(repo: Path) -> list[str]:
    if not (repo / ".git").exists():
        raise SystemExit(f"not a git working copy: {repo}")
    out = subprocess.run(["git", "-C", str(repo), "log", "--format=%cI"],
                         check=True, capture_output=True, text=True)
    return [line for line in out.stdout.splitlines() if line]


def _git_files(repo: Path) -> int:
    out = subprocess.run(["git", "-C", str(repo), "ls-files"],
                         check=True, capture_output=True, text=True)
    return len([line for line in out.stdout.splitlines() if line])


def _gh(args: list[str]) -> str:
    return subprocess.run(["gh", "api", *args], check=True,
                          capture_output=True, text=True).stdout


def _gh_dates(slug: str) -> list[str]:
    raw = _gh(["--paginate", f"repos/{slug}/commits?per_page=100",
               "--jq", ".[].commit.committer.date"])
    return [line for line in raw.splitlines() if line]


def _gh_files(slug: str, branch: str = "main") -> int:
    raw = _gh([f"repos/{slug}/git/trees/{branch}?recursive=1",
               "--jq", '[.tree[]|select(.type=="blob")]|length'])
    return int(raw.strip())


def main() -> int:
    contrib = json.loads(CONTRIB.read_text(encoding="utf-8"))
    weeks = _weeks(contrib["days"])
    origin, n = _index(weeks)

    regions: dict[str, dict] = {}

    lanes = []
    for name, path in ATRIUM_REPOS.items():
        dates = _git_dates(path)
        lanes.append({"name": name, "commits": _bucket(dates, origin, n),
                      "total": len(dates), "files": _git_files(path)})
    regions["atrium"] = {"lanes": lanes}

    for name, slug in GH_REPOS.items():
        dates = _gh_dates(slug)
        regions[name] = {"lanes": [{
            "name": name, "commits": _bucket(dates, origin, n),
            "total": len(dates), "files": _gh_files(slug),
        }]}

    doc = {
        "generated": date.today().isoformat(),
        "origin": origin.isoformat(),
        "weeks": weeks,
        "regions": regions,
        "note": "Written by bin/field_data.py. generators/ reads this and "
                "never fetches. Atrium's three repositories are private and "
                "are reduced from local working copies.",
    }
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}: {n} weeks from {origin}", file=sys.stderr)
    for region, spec in regions.items():
        for lane in spec["lanes"]:
            live = sum(1 for c in lane["commits"] if c)
            print(f"  {region:18} {lane['name']:18} {lane['total']:4} commits, "
                  f"{lane['files']:4} files, {live:2}/{n} weeks lit", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
