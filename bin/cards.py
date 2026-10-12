#!/usr/bin/env python3
"""Draw the still for each project card, in both themes, and write a manifest.

The page stopped moving on 12 Oct 2026. Thomas: "i dont want it to be
animation i want it to be interactive". The corridor is still the picture, but
as one frame per project: the flight docked on that project's lane, at the
week its commits peak. `generators/build.py` ships these files and never draws,
so a build needs no Pillow and no font; this script does both.

    python3 bin/cards.py

writes `design/cards/<key>-<theme>.<sha7>.png` and `design/cards/cards.json`,
which carries the lane counts the alt text is written from. Rerun it whenever
`data/field.json` changes. On a Mac it draws in Menlo; elsewhere in DejaVu
Sans Mono (see `generators.animate.FALLBACK`).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from generators import content, corridor  # noqa: E402

OUT = ROOT / "design" / "cards"

# Four frames back from the frame where the busiest week reaches the near
# edge, so that week's marks are inside the rails rather than under the frame.
LAG = 4


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    field = json.loads((ROOT / "data" / "field.json").read_text(encoding="utf-8"))
    manifest = {"_field": {"from": field["weeks"][0]["start"],
                           "to": field["generated"]}}
    for key, card in content.CARDS.items():
        entry = {"lane": card["lane"], "files": {}}
        for theme in corridor.THEMES:
            blob, frame, lane = corridor.lane_still("flight", theme, card["lane"], LAG)
            name = f"{key}-{theme}.{hashlib.sha256(blob).hexdigest()[:7]}.png"
            (OUT / name).write_bytes(blob)
            entry["files"][theme] = name
            entry.update(frame=frame, commits=lane["total"], files_touched=lane["files"],
                         weeks=lane["weeks"])
            print(f"wrote design/cards/{name}  {len(blob) / 1024:.0f} KB  frame {frame}")
        manifest[key] = entry
    (OUT / "cards.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
    print("wrote design/cards/cards.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
