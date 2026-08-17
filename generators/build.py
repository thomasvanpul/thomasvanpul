"""Emit README.md and every SVG asset from repo data + hand-written content.

Each SVG is written to assets/<basename>.<7-char-sha256>-<theme>.svg. README.md
references the exact hashed names produced this run. Any *.svg in assets/ not
referenced by the freshly rendered README is deleted.

Usage:
    python -m generators.build [--data path/to/repos.json] [--out path/to/repo]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import content
from .svg import THEMES, flow, hero, orbit, rule

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = REPO_ROOT / "data" / "repos.sample.json"
DEFAULT_OUT = REPO_ROOT


def _sha7(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:7]


def _emit(assets_dir: Path, basename: str, renderer, kept: set[Path]) -> dict[str, str]:
    """Render dark and light variants of a single SVG. Returns {theme: filename}."""
    variants: dict[str, str] = {}
    for theme in THEMES:
        body = renderer(theme)
        digest = _sha7(body)
        filename = f"{basename}.{digest}-{theme}.svg"
        path = assets_dir / filename
        path.write_text(body, encoding="utf-8")
        kept.add(path)
        variants[theme] = filename
    return variants


def _raw_url(owner: str, repo: str, branch: str, asset: str) -> str:
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/assets/{asset}"


def _picture(dark_url: str, light_url: str, alt: str) -> str:
    return (
        '<picture>\n'
        f'  <source media="(prefers-color-scheme: dark)" srcset="{dark_url}">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="{light_url}">\n'
        f'  <img alt="{alt}" src="{dark_url}">\n'
        '</picture>'
    )


def _render_readme(data: dict, variants: dict[str, dict[str, str]]) -> str:
    owner = data["owner"]
    repo = data["repo"]
    branch = data["branch"]

    def urls(basename: str) -> tuple[str, str]:
        v = variants[basename]
        return (
            _raw_url(owner, repo, branch, v["dark"]),
            _raw_url(owner, repo, branch, v["light"]),
        )

    hero_dark, hero_light = urls("hero")
    rule_dark, rule_light = urls("rule")
    orbit_dark, orbit_light = urls("orbit")

    def rule_block() -> str:
        return _picture(rule_dark, rule_light, "")

    lines: list[str] = []
    lines.append('<div align="center">\n')
    lines.append(_picture(hero_dark, hero_light, content.HERO_ARIA))
    lines.append('\n</div>\n')

    lines.append(content.INTRO + "\n")
    lines.append(rule_block() + "\n")

    for entry in data["featured"]:
        name = entry["name"]
        prose = content.FEATURED[name]
        flow_id = entry["flow"]["id"]
        flow_dark, flow_light = urls(f"flow-{flow_id}")

        lines.append(f'### {prose["heading"]}\n')
        body = prose["body"]
        if isinstance(body, list):
            lines.append(body[0] + "\n")
        else:
            lines.append(body + "\n")

        lines.append(_picture(flow_dark, flow_light, prose["flow_aria"]) + "\n")

        if isinstance(body, list) and len(body) > 1:
            for extra in body[1:]:
                lines.append(extra + "\n")

        suffix = prose.get("repo_suffix")
        repo_line = f'Repo: [`{name}`]({entry["url"]})'
        if suffix:
            repo_line += f' &nbsp;·&nbsp; {suffix}'
        lines.append(repo_line + "\n")
        lines.append(rule_block() + "\n")

    lines.append(f'### {content.ALSO_RUNNING_HEADING}\n')
    for i, (title, prose) in enumerate(content.ALSO_RUNNING):
        lines.append(f'**{title}** &nbsp;·&nbsp; {prose}\n')
    lines.append(rule_block() + "\n")

    lines.append(f'### {content.STACK_HEADING}\n')
    lines.append('<div align="center">\n')
    lines.append(_picture(orbit_dark, orbit_light, content.STACK_ORBIT_ARIA))
    lines.append('\n</div>\n')
    lines.append(rule_block() + "\n")

    lines.append('<div align="center">\n')
    lines.append(_picture(content.SNAKE_DARK_URL, content.SNAKE_LIGHT_URL, content.SNAKE_ARIA))
    lines.append("\n")
    lines.append(f'<sub>{content.FOOTER_SUB}</sub>\n')
    lines.append(content.FOOTER_LINKS + "\n")
    lines.append('</div>')

    return "\n".join(lines) + "\n"


def build(data_path: Path, out_dir: Path) -> list[Path]:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    kept: set[Path] = set()
    variants: dict[str, dict[str, str]] = {}

    variants["hero"] = _emit(
        assets_dir, "hero",
        lambda theme: hero.render(theme, content.HERO_NAME, content.HERO_SUBTITLES),
        kept,
    )
    variants["rule"] = _emit(assets_dir, "rule", rule.render, kept)
    variants["orbit"] = _emit(
        assets_dir, "orbit",
        lambda theme: orbit.render(theme, data["orbit"]["rings"]),
        kept,
    )

    for entry in data["featured"]:
        f = entry["flow"]
        flow_id = f["id"]
        stages = [tuple(s) for s in f["stages"]]
        duration = f.get("duration")
        side_input = f.get("side_input")
        variants[f"flow-{flow_id}"] = _emit(
            assets_dir, f"flow-{flow_id}",
            lambda theme, s=stages, d=duration, si=side_input: flow.render(theme, s, d, si),
            kept,
        )

    readme = _render_readme(data, variants)
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    removed: list[Path] = []
    for existing in assets_dir.glob("*.svg"):
        if existing not in kept:
            existing.unlink()
            removed.append(existing)

    written = sorted(p.relative_to(out_dir) for p in kept)
    for r in removed:
        print(f"removed  {r.relative_to(out_dir)}", file=sys.stderr)
    for w in written:
        print(f"wrote    {w}", file=sys.stderr)
    print(f"wrote    README.md", file=sys.stderr)
    return sorted(kept) + [out_dir / "README.md"]


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    build(args.data, args.out)


if __name__ == "__main__":
    main()
