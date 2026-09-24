"""The hero: Atrium's corridor, flown once a year, in two finishes.

Round 5 was rejected in four words -- "it doesn't feel fluid and doesn't feel
like it works together" -- and the rejection was correct about all four plates
that preceded it. Each held a field still and slid one line across it, because
a still field is what keeps a GIF under 200KB. That buys the size and loses
the thing the page is for: Atrium is a scene you move through, and a scene you
cannot move through is a chart with a nice palette.

So this module moves the camera instead of the line, and pays for it.

The world, and why it is this world
-----------------------------------
`Atlas/Projects/Atrium/Design-Language.md` settles the scene and rules out the
obvious alternative in the same breath. "Depth is time. The camera moves
forward through a stack of planes. No roll, no free rotation, horizon always
implied." And: "The sense of space comes from parallax and occlusion, not from
being able to fly around." So the first design here -- a camera orbiting the
time axis, which would have given each project its moment by simply rotating
it to the front -- is not built. What is built is the note's own world: "time
as a receding corridor: today at the near edge, the past running away to a
horizon, repos as lanes along it."

Thomas's answer to what a flat plane was missing was "dimensions, seeing
things from sides and orbiting". A tilted plane in perspective with the camera
drifting laterally gives the first two of those honestly: lanes pass, their
stacks occlude each other, the vanishing point slides. It does not give
orbiting, and this module does not pretend to. That is the one place the
design language and the frame answers disagree, and the note is older, longer
and written down, so it wins.

What is in it, and where every mark comes from
----------------------------------------------
* **The floor** is `data/field-grid.json` -- one real frame of the Atrium
  lattice reduced once to a 132 x 107 grid of density levels, the same frame
  every other asset on this page is cut from. Two grid rows are one week, so
  106 of its 107 rows are 53 weeks of corridor. It scrolls under the camera at
  exactly the rate the weeks do, which is the one-frame rule from the note:
  "the frame is the scene, each region is a slice of it."
* **The lanes** are the five real lanes of `data/field.json` -- Atrium's
  surface, host and design repositories, `blueband-concept`, `Finance-Tracker`.
  One mark is one commit. A week's commits stack upward off the floor, so the
  height of a stack is that week's commit count and nothing else. 933 marks,
  933 commits.
* **A lane's width is its files touched**, 4 columns at the narrowest and 12
  at the widest. Three of the five come out the same width because three of
  them really are the same size: 11, 14 and 24 files.
* **Null cells.** A lane-week with no commits draws the X of primitive 3
  rather than nothing, wherever the cell is big enough to draw it. Atrium's
  design lane is 52 of those and one mark, which is what that lane is.

Nothing is invented to fill space. The note's line on this is the shortest one
in it: "If a mark has to be invented to fill space, the region should be empty
instead."

Colour: three, and what each one means
--------------------------------------
Ground is the page's own `#0d1117`. The seven-step density ramp out of
`data/atrium-tokens.json` carries how much happened. One white -- the `now`
token, `LatticeLanguage.now`, which the ramp stops short of since 19 Sep -- is
the focal reserve, and it is spent on exactly one thing per
frame: the lane being read. That resolves the note's open question ("Either
text takes step 6 or the reserve goes") in favour of the reserve; drawn text
takes step 5.

The link blue is not in the image at all. It was removed on purpose, and the
rule it leaves behind is worth more than the colour was: blue means clickable,
and nothing inside a README image is clickable.

The light plate is the same seven tokens read the other way up -- ground near
white, density 6 near black. Not a second palette, the same one inverted, so
the two cannot drift.

Motion: four verbs, and none of them is "glow"
-----------------------------------------------
The note allows resolve, de-resolve, sweep and track, and says why: "Each has
a direction and a cause." This uses two. The camera **sweeps** forward through
the year at a constant rate. A box **tracks** from lane to lane, and the
camera drifts laterally to follow it, which is the only reason the vanishing
point moves. Nothing modulates brightness in place. Thomas called that
shimmering and he was right.

Dwell is not equal. Each lane gets 12 frames plus a share of the remainder
weighted by the square root of its commits, so Numeris is read for four times
as long as Atrium's design lane. Equal dwell would have been one easing and
one duration applied to five different things, which is a tell.

The loop
--------
One pass is one year. The camera's time position runs 0 to 53 weeks across the
frame count, the floor's 106 rows wrap at the same rate, and the station cycle
closes on the same frame, so frame N is frame 0 exactly and there is no seam
to see. This is the property that cannot be checked from a still, which is why
`bin/hero.py` ends in video.

Size
----
A corridor that moves has no still region to delta against, so this costs what
the earlier plates were built to avoid. Both finishes are encoded as GIF and
as APNG and the smaller ships; `build()` reports both numbers rather than
asserting one.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from . import svg
from .animate import (BOLD, LABEL, MIN_APPARENT_PX, MONO,  # noqa: F401
                      PHONE_COLUMN, REGULAR, VALUE, _font, _mix,
                      _text, _width_of, day_curve, encode, ramp_at)

ROOT = Path(__file__).resolve().parent.parent
GRID_JSON = ROOT / "data" / "field-grid.json"
FIELD_JSON = ROOT / "data" / "field.json"

VARIANTS = ("flight", "readout")
THEMES = ("dark", "light")

# The plate is narrower than the 980-unit desktop column the static plates
# use, and the reason is bytes rather than taste. A corridor that moves has
# no still region to delta against, so the file is close to linear in pixel
# count: the same ten seconds at 980 x 430 encodes to 2,630KB and will not
# come down without taking the motion out of it. 820 x 360 is 70% of the
# area, which is what brings it inside the budget with the loop intact.
#
# It costs nothing on a phone, where every image is scaled to the 358px
# column anyway, and on desktop it sits inside the column rather than filling
# it. `orhun`, which is the reference this page is built from, does the same.
WIDTH = 820

# The type floor follows the plate, it is not copied from the plate that
# happened to be 980 wide. 11px apparent in GitHub's 358px phone column.
FLOOR = MIN_APPARENT_PX * WIDTH / PHONE_COLUMN

# --- the loop ----------------------------------------------------------------

# 96 rather than 112. Both finishes grew vertically to stop their chrome
# overlapping (see FLIGHT_H and READOUT_FOOT), and a taller plate is a bigger
# plate: at 112 frames the taller flight encoded to 1,559KB, over budget.
# Frames are the only lever that does not cost the reader anything visible --
# the field is the same field, the camera covers the same year, the steps
# between frames are 8% longer. At 13fps the loop is 7.4s, so a reader sees
# the join about twice in the twenty seconds `bin/hero.py` films.
FRAMES = 96
FPS = 13
WEEKS = 53
ROWS_PER_WEEK = 2

# --- the camera --------------------------------------------------------------

# Every one of these is a focal choice and none of them is measured, so they
# are named and gathered rather than scattered through the drawing code.
# Camera standoff, in weeks. It is the shape of the whole corridor: at 1.1
# the first week of the year fills the lower two thirds of the frame and the
# other 52 pile into a band 60px deep, which drew a black floor with a red
# smear along the top of it. At 5 the fall-off is gentle enough that half the
# year is still resolvable and the near rows are 30px apart rather than 170.
D0 = 5.0
VISIBLE = 53        # the whole year is in frame; the camera flies through it
# Wide enough that the corridor is under the whole frame at every depth. At
# 1.5 the lattice ran out 150px short of the right edge whenever the camera
# leaned toward Numeris, which is the rightmost lane, and the bottom right
# corner photographed as unlit ground rather than as floor.
NEAR_SPAN = 2.6
CAM_LEAN = 0.40     # how far the camera slides toward the lane being read
VPX_FRAC = 0.42     # the vanishing point is off centre on purpose
HORIZON_FRAC = 0.22
FLOOR_OVERSHOOT = 30    # the near edge runs off the bottom of the frame
# Supersample factor. It is 1, and that is a measurement rather than a
# preference: at 2 the reduction gives every mark edge intermediate values,
# every frame quantises those differently, and the same 130 frames encode to
# 5,990KB instead of 2,630KB. Looking at the two side by side, the hard-edged
# plate is also the better one -- the marks read as a grid of discrete cells,
# which is what the field is. Raising this costs a factor of 2.3 in bytes for
# a softer image, so it is written down here rather than left as a knob.
SS = 1

# Below this a mark is drawn at the floor size and dimmed instead of shrunk.
# Shrinking past a pixel is what makes a scrolling field crawl and flicker.
MARK_FLOOR_PX = 1.0 * SS

# A substrate row whose neighbours are closer together than this is not drawn.
# 132 columns at a third of a pixel is not a row a reader can count, it is a
# haze; it also changes everywhere in every frame and is the single most
# expensive band in the file. The lanes and their rails keep drawing past it,
# so the corridor still reaches the horizon -- what stops is the texture.
MIN_ROW_PX = 1.1 * SS

MARK_OF_PITCH = 0.42    # Design-Language: "squares at 0.42 of the pitch"
# A commit is structure and a floor cell is texture, and the note is explicit
# that texture may go sub-pixel while structure may not. So a commit is drawn
# larger than the pitch would give it and never smaller than this.
COMMIT_OF_PITCH = 0.66
COMMIT_FLOOR_PX = 2.0 * SS
NULL_MIN_PITCH = 7.0 * SS   # below this a null cell is not drawn, it is ground

# --- the lanes ---------------------------------------------------------------

LANE_ORDER = [
    ("atrium", "surface", "ATRIUM · SURFACE"),
    ("atrium", "host", "ATRIUM · HOST"),
    ("atrium", "design", "ATRIUM · DESIGN"),
    ("blueband-concept", "blueband-concept", "BLUEBAND"),
    ("Finance-Tracker", "Finance-Tracker", "NUMERIS"),
]

GRID_COLS = 132
MIN_LANE_COLS, MAX_LANE_COLS = 4, 12


def lanes() -> list[dict]:
    """The five real lanes, laid out across the corridor floor.

    Order is the order they sit in `data/field.json`, which puts Atrium's
    three together -- so the flight reads as one project of three lanes, then
    two of one, rather than as five interchangeable things.
    """
    doc = json.loads(FIELD_JSON.read_text(encoding="utf-8"))
    raw = []
    for region, name, label in LANE_ORDER:
        lane = next(l for l in doc["regions"][region]["lanes"]
                    if l["name"] == name)
        raw.append({"label": label, "commits": lane["commits"],
                    "total": lane["total"], "files": lane["files"],
                    "weeks": sum(1 for c in lane["commits"] if c)})

    top = max(l["files"] for l in raw)
    for l in raw:
        span = MAX_LANE_COLS - MIN_LANE_COLS
        l["cols"] = MIN_LANE_COLS + round(span * l["files"] / top)

    gap = (GRID_COLS - sum(l["cols"] for l in raw)) / (len(raw) + 1)
    at = gap
    for l in raw:
        l["u0"] = at
        l["u1"] = at + l["cols"]
        l["uc"] = at + l["cols"] / 2
        at += l["cols"] + gap

    return raw


def grid() -> tuple[list[list[int]], int, int]:
    """One real Atrium frame as density levels, 132 wide."""
    doc = json.loads(GRID_JSON.read_text(encoding="utf-8"))
    cols, rows, cells = doc["cols"], doc["rows"], doc["cells"]
    return ([[int(cells[r * cols + c]) for c in range(cols)]
             for r in range(rows)], cols, rows)


# --- palette -----------------------------------------------------------------

def palette(theme: str) -> dict:
    """Ground, the seven density steps, and the focal reserve.

    Light is the same seven steps reversed, over a near-white ground. There is
    no second set of values anywhere: invert the index and the plate inverts.
    """
    curve = day_curve()
    ramp = ramp_at(curve, curve["resting_point"]["hue_deg"])
    if theme == "light":
        ramp = list(reversed(ramp))
        ground = (246, 248, 250)          # GitHub's light canvas
    else:
        ground = svg.rgb(svg.GROUND_DARK)
    # The panel ground is the page ground, unmixed. That is what makes a
    # readout survive over a lit field: it is the one rectangle on the plate
    # darker (or, on light, lighter) than everything around it.
    # The focal reserve is `now` on dark: the ramp's top step is a pale tint,
    # and white is the one colour that means the thing being read. On light
    # the reversed ramp's far end, density-0, is already the extreme.
    focal = ramp[6] if theme == "light" else svg.rgb(svg.token("now"))
    return {"ground": ground, "ramp": ramp,
            "panel": ground, "focal": focal, "text": ramp[5],
            "dim": _mix(ground, ramp[5], 0.52)}


# --- projection --------------------------------------------------------------

class Camera:
    """A tilted plane in perspective. Tilt, no roll, a horizon that exists."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w * SS, h * SS
        self.vpx = self.w * VPX_FRAC
        # Solved rather than guessed: the near edge lands `FLOOR_OVERSHOOT`
        # below the frame and week 53 lands on the horizon, so changing the
        # plate height moves neither of them off their mark.
        floor_y = (h + FLOOR_OVERSHOOT) * SS
        horizon = h * HORIZON_FRAC * SS
        self.k = (floor_y - horizon) / (1 / D0 - 1 / (VISIBLE + D0))
        self.c = floor_y - self.k / D0
        self.horizon = horizon
        self.sx = NEAR_SPAN * self.w * D0 / GRID_COLS
        self.hy = self.sx          # one stacked commit rises one column pitch
        self.u = GRID_COLS / 2.0

    def at(self, u: float, d: float, height: float = 0.0):
        z = d + D0
        return (self.vpx + (u - self.u) * self.sx / z,
                self.c + self.k / z - height * self.hy / z)

    def depth_at(self, frac: float) -> float:
        """The depth, in weeks, whose floor sits `frac` down the viewport."""
        y = frac * self.h
        return self.k / max(1e-6, y - self.c) - D0

    def pitch(self, d: float) -> tuple[float, float]:
        """One column wide and one substrate row deep, in screen units."""
        z = d + D0
        row = 1.0 / ROWS_PER_WEEK
        return self.sx / z, self.k / z - self.k / (z + row)


def _t(d, x: float, y: float, string: str, size: float, fill, **kw) -> None:
    """`animate._text`, in supersampled coordinates.

    Everything here is drawn at `SS` times size and reduced at the end, so a
    naive call would hand the type floor a number `SS` times too large and the
    check would pass on type nobody can read. The floor is applied to the unit
    size and the scaling happens after it.
    """
    if size < FLOOR:
        raise ValueError(
            f"{kw.get('where') or string!r}: {size:.1f} units is "
            f"{size * PHONE_COLUMN / WIDTH:.1f}px in a {PHONE_COLUMN}px phone "
            f"column, under the {MIN_APPARENT_PX:g}px floor")
    _text(d, x * SS, y * SS, string, size * SS, fill, **kw)


def _w(string: str, size: float, tracking: float = 0.0) -> float:
    return _width_of(string, size * SS, tracking) / SS


def _tone(pal, level: float, near: float, focal: bool = False):
    """A mark's colour: the ramp step its density falls in, dimmed by depth.

    The ramp is a seven-step spec and a mark takes the step it falls in rather
    than a blend of two, because that is how `LatticeRenderer` bands it. Depth
    is then a mix toward ground, which is the only place a blend happens.
    """
    step = pal["focal"] if focal else pal["ramp"][min(4, int(level * 4.999))]
    return _mix(pal["ground"], step, max(0.06, min(1.0, near)))


# --- the corridor ------------------------------------------------------------

def _draw_corridor(d, cam, pal, cells, lns, p: float, tracked: int):
    """One frame of floor and stacks, in supersampled coordinates.

    Drawn far to near so that near stacks occlude far ones. Occlusion and
    parallax are where the space comes from; there is no shading model here
    and there is not meant to be.
    """
    m0 = math.ceil(p)
    for m in range(m0 + VISIBLE, m0 - 1, -1):
        dep = m - p
        if dep < 0:
            continue
        pu, pv = cam.pitch(dep)
        size = max(MARK_FLOOR_PX, MARK_OF_PITCH * min(pu, pv))
        fade = min(1.0, (MARK_OF_PITCH * min(pu, pv)) / MARK_FLOOR_PX)
        near = (D0 / (dep + D0)) ** 0.55 * fade
        week = (WEEKS - 1 - (m % WEEKS))

        # --- the floor: two real grid rows per week
        floor_on = pv >= MIN_ROW_PX
        #
        # The per-column x is `A + c * B` on any one row, so it is computed
        # that way rather than through `cam.at` per mark. 132 columns times 52
        # rows times 130 frames is 892,000 marks a plate; a method call per
        # mark is the difference between a build that takes a minute and one
        # that takes eight.
        # Grid levels run 1..9, so the nine are spread over the five steps the
        # substrate is allowed rather than over seven: levels 5 and 6, which
        # are 4,093 of the 14,124 cells, must not both land on step 2.
        # Level 1 must not land on step 0. Step 0 is #080302 on a #0d1117
        # ground, so 1,171 of the 14,124 cells were being drawn invisible and
        # the sparse left of the frame photographed as an unlit edge. The
        # nine levels are mapped onto steps 1 to 4, and 0 stays what it is:
        # the level the grid records as nothing.
        tones = [_tone(pal, 0.25 + (v - 1) / 8.0 * 0.75, near * 0.92)
                 for v in range(10)]
        for sub in range(ROWS_PER_WEEK if floor_on else 0):
            row = (m * ROWS_PER_WEEK + sub) % (WEEKS * ROWS_PER_WEEK)
            dd = dep + sub / ROWS_PER_WEEK
            line = cells[row]
            z = dd + D0
            b = cam.sx / z
            a = cam.vpx + (0.5 - cam.u) * b
            y = cam.c + cam.k / z
            half = size / 2
            lo, hi = y - half, y + half
            for c in range(GRID_COLS):
                v = line[c]
                if not v:
                    continue
                x = a + c * b
                if x < -size or x > cam.w + size:
                    continue
                d.rectangle([x - half, lo, x + half, hi], fill=tones[v])

        # --- the lanes: one mark, one commit
        c_size = max(COMMIT_FLOOR_PX, COMMIT_OF_PITCH * min(pu, pv))
        c_near = min(1.0, (D0 / (dep + D0)) ** 0.42 * 1.25)
        for i, lane in enumerate(lns):
            c_n = lane["commits"][week]
            per = lane["cols"] * ROWS_PER_WEEK
            if not c_n:
                if pu >= NULL_MIN_PITCH:
                    _null(d, cam, pal, lane, dep, near)
                continue
            focal = i == tracked
            for k in range(c_n):
                layer, slot = divmod(k, per)
                cu = lane["u0"] + (slot % lane["cols"]) + 0.5
                dd = dep + (slot // lane["cols"]) / ROWS_PER_WEEK
                x, y = cam.at(cu, dd, layer + 0.5)
                if x < -size or x > cam.w + size:
                    continue
                s = c_size / 2
                d.rectangle([x - s, y - s, x + s, y + s],
                            fill=_tone(pal, 1.0, c_near, focal))


def _null(d, cam, pal, lane, dep, near):
    """Primitive 3: a repo-week where genuinely nothing happened, said so."""
    x0, y0 = cam.at(lane["u0"] + 0.35, dep)
    x1, y1 = cam.at(lane["u1"] - 0.35, dep + 1 / ROWS_PER_WEEK)
    tone = _mix(pal["ground"], pal["ramp"][1], min(1.0, near * 1.6))
    w = max(1, int(SS))
    d.line([x0, y0, x1, y1], fill=tone, width=w)
    d.line([x0, y1, x1, y0], fill=tone, width=w)


# --- the tracker -------------------------------------------------------------

TRACK_NEAR = 0.2        # weeks ahead of the camera the rails start
TRACK_DEEP = 22.0       # and where they stop, short of the horizon
# Where on the rails the leader line lands, as a fraction of the viewport
# height. The near end of a rail is below the bottom of the frame -- that is
# what `FLOOR_OVERSHOOT` is for -- so a leader drawn to it points off the
# plate at something nobody can see.
ANCHOR_AT = 0.66


def _lane_rails(d, cam, pal, lns, skip: int) -> None:
    """Every lane's near rail, dim, all the time.

    Without these the corridor is a field with one bright pair of lines
    floating in it and no reason for them to be where they are. With them it
    is five lanes, one of which is being read, which is also the honest
    answer to Thomas on hover chrome: nothing appears because you asked.
    """
    for i, lane in enumerate(lns):
        if i == skip:
            continue
        for u in (lane["u0"] - 0.6, lane["u1"] + 0.6):
            a = cam.at(u, TRACK_NEAR)
            b = cam.at(u, TRACK_DEEP)
            d.line([a[0], a[1], b[0], b[1]],
                   fill=_mix(pal["ground"], pal["dim"], 0.42), width=SS)


def _track_rails(d, cam, pal, u0: float, u1: float):
    """Primitive 4 as a rail, not a slice.

    The first build put a box across the lane at a fixed depth ahead of the
    camera. On `blueband-concept`, which has commits in one week of 53, that
    box framed nothing for 51 of the 53 weeks it flew over -- a label reading
    13 COMMITS over an empty rectangle. Rails run the lane's whole visible
    length instead, so whatever the lane has is inside them wherever it is.
    Returns the near end of the right rail, which is what the leader line
    comes off.
    """
    w = max(2, int(1.2 * SS))
    for u in (u0 - 0.6, u1 + 0.6):
        a = cam.at(u, TRACK_NEAR)
        b = cam.at(u, TRACK_DEEP)
        d.line([a[0], a[1], b[0], b[1]], fill=pal["focal"], width=w)
    # A tick at the far end, so the rails read as a measured span and not as
    # two lines that happen to converge.
    f0, f1 = cam.at(u0 - 0.6, TRACK_DEEP), cam.at(u1 + 0.6, TRACK_DEEP)
    d.line([f0[0], f0[1], f1[0], f1[1]], fill=pal["focal"], width=w)
    return cam.at((u0 + u1) / 2, cam.depth_at(ANCHOR_AT))


# The camera holds over a week with work in it and covers an empty one in a
# frame. `SLOW` is the ratio between the two at the busiest week; `SMOOTH` is
# the radius, in weeks, of the cyclic blur applied to the profile.
#
# This is not a flourish, it is forced by the data. Thirty-eight of the
# fifty-three weeks in `data/field.json` are empty: nothing was pushed to any
# of the five lanes before June 2026. A camera at constant speed spends seven
# of its ten seconds over null cells. Weighting the speed by the week's real
# contribution count spends them where the year actually happened, and the
# rule it follows is one a reader can state: the flight slows over a week
# something was done in.
#
# The blur is cyclic and wide because the seam is the point. Week 52 is the
# slowest week of the year and week 0 is the fastest, and they are adjacent
# across the loop join; without the blur the loop restarts with a jolt, which
# is the one defect a looping hero cannot have.
SLOW = 9.0
SMOOTH = 3


def week_weight() -> list[float]:
    """How long the camera spends on each week, from that week's real record."""
    doc = json.loads(FIELD_JSON.read_text(encoding="utf-8"))
    counts = [w["count"] for w in doc["weeks"]]
    peak = max(counts) or 1
    raw = [1.0 + SLOW * (c / peak) ** 0.5 for c in counts]
    n = len(raw)
    span = 2 * SMOOTH + 1
    return [sum(raw[(i + k) % n] for k in range(-SMOOTH, SMOOTH + 1)) / span
            for i in range(n)]


def camera_path() -> list[float]:
    """The camera's time position, in weeks, at each frame of the loop.

    Traversal runs week 52 first: today is at the near edge and the camera
    flies into the past, which is Atrium's own rule that moving forward is
    moving back through time.
    """
    weight = week_weight()
    cost = [weight[WEEKS - 1 - j] for j in range(WEEKS)]
    bounds, run = [0.0], 0.0
    for c in cost:
        run += c
        bounds.append(run)
    total = run

    path, j = [], 0
    for i in range(FRAMES):
        t = i / FRAMES * total
        while j < WEEKS - 1 and t >= bounds[j + 1]:
            j += 1
        path.append(j + (t - bounds[j]) / cost[j])
    return path


def _frame_of_week(week: int, path: list[float]) -> int:
    """The frame at which a given week is at the camera's near edge."""
    want = WEEKS - 1 - week
    for i, p in enumerate(path):
        if p >= want:
            return i
    return FRAMES - 1


def schedule(lns, path: list[float]) -> list[dict]:
    """When each lane is read: at the frame its own busiest week arrives.

    The first build weighted dwell by the square root of a lane's commits and
    placed the windows in list order, which meant a panel could read NUMERIS,
    712 COMMITS while the camera was over February and the lane under the
    rails was empty. Anchoring each window to the lane's peak week fixes the
    cause rather than the symptom: the tracker moves to a lane because the
    camera has arrived at that lane's biggest week.

    Boundaries fall at the midpoints between consecutive anchors, so the
    windows tile the loop exactly and their lengths are a consequence of the
    data rather than a second set of weights.
    """
    anchors = []
    for i, lane in enumerate(lns):
        peak = max(range(WEEKS), key=lane["commits"].__getitem__)
        anchors.append((_frame_of_week(peak, path), i, peak))
    anchors.sort()

    out = []
    n = len(anchors)
    for k, (at, i, peak) in enumerate(anchors):
        nxt, _, _ = anchors[(k + 1) % n]
        prv, _, _ = anchors[k - 1]
        start = (prv + at) // 2 if k else (at + (anchors[-1][0] - FRAMES)) // 2
        end = (at + nxt) // 2 if k < n - 1 else (at + anchors[0][0] + FRAMES) // 2
        out.append({"lane": i, "at": at, "peak": peak,
                    "start": start % FRAMES, "frames": end - start})
    if sum(w["frames"] for w in out) != FRAMES:
        raise ValueError(f"the station windows tile {sum(w['frames'] for w in out)} "
                         f"frames of {FRAMES}")

    short = [w for w in out if w["frames"] < MIN_WINDOW]
    if short:
        owed = sum(MIN_WINDOW - w["frames"] for w in short)
        donors = [w for w in out if w["frames"] > MIN_WINDOW]
        spare = sum(w["frames"] - MIN_WINDOW for w in donors)
        if owed > spare:
            raise ValueError(f"{len(out)} stations cannot each hold "
                             f"{MIN_WINDOW} frames of {FRAMES}")
        for w in short:
            w["frames"] = MIN_WINDOW
        left = owed
        for w in donors[:-1]:
            take = round(owed * (w["frames"] - MIN_WINDOW) / spare)
            w["frames"] -= take
            left -= take
        donors[-1]["frames"] -= left
        at = out[0]["start"]
        for w in out:
            w["start"] = at % FRAMES
            at += w["frames"]
    if sum(w["frames"] for w in out) != FRAMES:
        raise ValueError("window floor did not conserve the loop length")
    return out


# Two lanes peak in the same week, so the midpoints alone give one of them a
# six-frame window: half a second, which is not a station, it is a flicker.
# Every window is raised to this floor and the deficit is taken from the long
# ones in proportion. The order and the anchors stay where the data put them.
MIN_WINDOW = 15
EASE = 7        # frames a handover takes


def station(plan, frame: int) -> tuple[int, int, float]:
    """Which lane is being read, which it is moving to, and how far along."""
    for k, win in enumerate(plan):
        into = (frame - win["start"]) % FRAMES
        if into < win["frames"]:
            left = win["frames"] - into
            nxt = plan[(k + 1) % len(plan)]["lane"]
            if left <= EASE:
                t = (EASE - left) / EASE
                return win["lane"], nxt, t * t * (3 - 2 * t)
            return win["lane"], win["lane"], 0.0
    raise ValueError(f"frame {frame} falls in no station window")


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


# --- chrome ------------------------------------------------------------------

PAD = 34
PANEL_PAD = 20


def _fits(items) -> float:
    """The width the widest of these strings needs, measured not estimated.

    `animate._foot` exists because the first instrument stills read
    CONTRIBUTIOИDAYS: a slot was 194 units and the label wanted 242, and a
    screenshot was trusted to notice. Every panel in this module is sized by
    this function instead, and it raises rather than clipping.
    """
    return max(_w(string, size, track) for string, size, track in items)


def _ground_panel(d, box, pal, alpha: float = 1.0):
    """A readout paints the ground before it draws.

    Measured on 2026-09-19, not preferred: a 72px readout survives over dense
    lattice marks and its 38px caption does not, at any opacity that still
    reads as a caption. So the panel is the page ground, opaque, and the
    question does not come up.
    """
    x0, y0, x1, y1 = [v * SS for v in box]
    d.rectangle([x0, y0, x1, y1], fill=pal["panel"])
    d.line([x0, y0, x1, y0],
           fill=_mix(pal["panel"], pal["focal"], alpha), width=2 * SS)


PANEL_H = 16 + LABEL + 14 + VALUE + 10 + LABEL + 6 + LABEL + 18


def _readout(d, pal, x: float, y: float, lane: dict, alpha: float,
             on_right: bool = True) -> tuple[float, float]:
    """The docked panel: which lane is being read, and its three real counts.

    It does not fade. A panel at 40% over a lit field is the caption problem
    the measurement above rules out, so the handover hides it instead: below
    half opacity it is simply not drawn, and it comes back carrying the next
    lane's numbers. No frame ever shows a blend of two lanes.

    `x` is the edge the panel docks to, and the type anchors to that edge.
    Docked right the type is right-aligned to it; docked left the type
    starts at `x + PANEL_PAD`, which is the chronometer's own left edge, so
    the date line above and the counts below share one margin. The first
    build right-aligned both sides to the widest lane's panel, so a narrow
    lane docked left sat up to 60 units off the chronometer's margin.

    Returns the type's left edge and the panel's far edge.
    """
    lines = _readout_lines(lane)
    width = _fits(lines)
    if on_right:
        left, x0, x1 = x - width - PANEL_PAD, x - width - 2 * PANEL_PAD, x
    else:
        left, x0, x1 = x + PANEL_PAD, x, x + width + 2 * PANEL_PAD
    if alpha < 0.5:
        return left, x1 if on_right else x0
    _ground_panel(d, [x0, y, x1, y + PANEL_H], pal)
    at = y + 16
    for k, (string, size, track) in enumerate(lines):
        _t(d, left, at, string, size,
           pal["text"] if k < 2 else pal["dim"], bold=k < 2, tracking=track,
           where=f"readout line {k}")
        at += size + (14 if k == 0 else 10 if k == 1 else 6)
    return left, x0 if on_right else x1


def _readout_lines(lane: dict):
    """Four lines, because three of them will not fit on one.

    `404 FILES · 3/53 WEEKS` is 22 characters, which is 443 units at the type
    floor -- wider than the widest panel that leaves the corridor visible. It
    is split rather than shrunk, because shrinking it is shrinking below the
    floor and that is the check this repo exists to keep.
    """
    return [(lane["label"], LABEL, 0.12),
            (_count(lane["total"], "COMMIT"), VALUE, 0.0),
            (_count(lane["files"], "FILE"), LABEL, 0.05),
            (f"{lane['weeks']} OF 53 WEEKS", LABEL, 0.05)]


def _count(n: int, noun: str) -> str:
    """`1 COMMITS` is what the first build of this panel said, for a year.

    Atrium's design lane really is one commit across 24 files, so the panel
    that reads it is the one a reader looks at hardest. The separator is the
    same one every other number on this page uses.
    """
    return f"{n:,} {noun}" + ("" if n == 1 else "S")


def _leader(d, pal, frm, to, alpha: float) -> None:
    """Primitive 5: the line lands on its subject, which is the whole point.

    It elbows. A straight run from a docked panel to a mark in the field
    crosses the lattice at whatever angle the two happen to make, and that is
    named in the v3 critique as one of the things that made the frame read as
    a chart with lines drawn on it. Two orthogonal segments read as chrome.
    """
    if alpha < 0.5:
        return
    x0, y0 = frm
    x1, y1 = to[0] * SS, to[1] * SS
    w = max(2, int(1.2 * SS))
    d.line([x1, y1, x0, y1], fill=pal["focal"], width=w)
    d.line([x0, y1, x0, y0], fill=pal["focal"], width=w)


CHRONO_LABEL = "ATRIUM · ONE YEAR OF THE RECORD"


def _chronometer(d, pal, x: float, y: float, start: str, n: int,
                 ground: bool) -> None:
    """The one dominant readout everything else responds to.

    On `flight` it paints its ground, because the corridor reaches the top of
    the frame there and 31-unit tracked capitals do not survive over lit
    marks. On `readout` the chrome band above the viewport is already ground
    and a second rectangle over it would be a panel with nothing under it.
    """
    value = f"{start}  W{n:02d}/53"
    w = max(_w(CHRONO_LABEL, LABEL, 0.14), _w(value, VALUE)) + 2 * PANEL_PAD
    h = 16 + LABEL + 12 + VALUE + 16
    if ground:
        _ground_panel(d, [x - PANEL_PAD, y - 16, x - PANEL_PAD + w,
                          y - 16 + h], pal)
    _t(d, x, y, CHRONO_LABEL, LABEL, pal["dim"], tracking=0.14,
       where="chronometer label")
    _t(d, x, y + LABEL + 12, value, VALUE, pal["text"], bold=True,
       where="chronometer value")


# Six rows -- one group header and five lanes -- have to land between the top
# of the field band and the top of the foot. That is 246 units, and six rows
# of LABEL is 186, so the gaps are what is left rather than what looks
# comfortable. They were 10 and 16 and the rail overran the foot by 42.
STATION_GROUP_GAP = 8
STATION_ROW_GAP = 10


def _stations(d, pal, x: float, y: float, lns, tracked: int) -> None:
    """Every lane, named, all the time.

    Thomas on hover-to-reveal chrome: what he hates about it is "not knowing
    what is there". A rail that lists all five and lights the one being read
    is the opposite of that, and it is the structural difference between the
    two finishes that a reader would describe in words.
    """
    rows, seen = [], None
    for i, lane in enumerate(lns):
        group, _, leaf = lane["label"].partition(" · ")
        if leaf and group != seen:
            rows.append((None, group, 0))
        seen = group if leaf else None
        rows.append((i, leaf or group, 1 if leaf else 0))

    yy = y
    for i, string, indent in rows:
        on = i is not None and i == tracked
        left = x + indent * 22
        if on:
            d.rectangle([(x - 14) * SS, (yy - 5) * SS,
                         (x - 9) * SS, (yy + LABEL + 5) * SS],
                        fill=pal["focal"])
        _t(d, left, yy, string, LABEL,
           pal["text"] if on else pal["dim"], bold=on, tracking=0.10,
           where=f"station {string}")
        yy += LABEL + (STATION_GROUP_GAP if i is None else STATION_ROW_GAP)


# --- the two finishes --------------------------------------------------------

# Both heights are the sum of what the chrome measures, not a round number.
#
# flight: the chronometer panel runs y 34 to 150 and the docked readout is
# PANEL_H tall with PAD under it. At 360 those two overlapped by 22px and the
# readout's top rule was drawn straight through `W51/53` in the chronometer
# value -- visible in `design/hero/flight/page/dark-desktop.png` before this
# change. 402 is 150 + 20 clear + PANEL_H + PAD, so the two rules stack.
FLIGHT_H = 402
# readout: the foot needs 18 + VALUE + LABEL + 12 = 102 units under the field
# and had 92, so its labels were drawn over the last ten rows of corridor;
# and the six-row station rail ran to y 392, through the foot values. 130
# clears the foot, and the rail rows are tightened below to end above it.
READOUT_H = 452
READOUT_TOP = 96
READOUT_FOOT = 130
READOUT_RAIL = 276

FLIGHT_ALT = (
    "One year of real work flown as a corridor: the floor is a real frame of "
    "the Atrium lattice, the five lanes running away to the horizon are "
    "Atrium's surface, host and design repositories, blueband-concept and "
    "Finance-Tracker, and every mark stacked above a lane is one real commit "
    "in that week. Two rails run the length of whichever lane is being read "
    "and a docked panel names it with its commit, file and week counts.")

READOUT_ALT = (
    "The same corridor of one real year, framed as an Atrium readout: a "
    "chronometer counting the week at the near edge, a rail naming all five "
    "repository lanes with the one being read lit, and a foot carrying that "
    "lane's real commit, file and week counts. Every mark stacked above a "
    "lane is one commit.")

ALT = {"flight": FLIGHT_ALT, "readout": READOUT_ALT}


def _frame(variant: str, theme: str, i: int, cells, lns, pal, plan, path):
    from PIL import Image, ImageDraw

    h = FLIGHT_H if variant == "flight" else READOUT_H
    im = Image.new("RGB", (WIDTH * SS, h * SS), pal["ground"])

    a, b, t = station(plan, i)
    la, lb = lns[a], lns[b]
    reading = a if t < 0.5 else b
    u0 = _lerp(la["u0"], lb["u0"], t)
    u1 = _lerp(la["u1"], lb["u1"], t)
    # 1 while docked, falling to 0 at the midpoint of a handover and back.
    # The panel is drawn above 0.5 and hidden below it, so the swap happens
    # while there is nothing on screen to swap.
    settled = abs(t - 0.5) * 2 if t else 1.0

    view = ((0, 0, WIDTH, h) if variant == "flight"
            else (0, READOUT_TOP, WIDTH - READOUT_RAIL, h - READOUT_FOOT))
    vw, vh = view[2] - view[0], view[3] - view[1]

    cam = Camera(vw, vh)
    # The camera leans toward the lane being read rather than centring on it.
    # Centring puts Numeris, which is the rightmost of the five, 23 columns
    # from the edge of a 132-column field, and the right third of the frame
    # falls off the lattice into ground. A lean keeps the corridor under the
    # whole frame and still moves the vanishing point, which is the only
    # reason the lean exists.
    cam.u = _lerp(GRID_COLS / 2.0, _lerp(la["uc"], lb["uc"], t), CAM_LEAN)

    field = Image.new("RGB", (vw * SS, vh * SS), pal["ground"])
    fd = ImageDraw.Draw(field)
    p = path[i]
    _draw_corridor(fd, cam, pal, cells, lns, p, reading)
    _lane_rails(fd, cam, pal, lns, reading)
    anchor = _track_rails(fd, cam, pal, u0, u1)
    im.paste(field, (view[0] * SS, view[1] * SS))

    d = ImageDraw.Draw(im)
    week_i = (WEEKS - 1 - (math.ceil(p) % WEEKS))

    if variant == "flight":
        _chronometer(d, pal, PAD + PANEL_PAD, PAD + 16,
                     _week_start(week_i), week_i + 1, ground=True)
        # The panel docks away from the lane it names. Docking it always
        # right put it straight on top of Numeris, which is the rightmost of
        # the five, and the plate then read as a caption over a blank corner
        # while the thing it described was underneath it. Which side it takes
        # is therefore a consequence of where the camera is looking, and the
        # composition is different at every station rather than the same one
        # five times.
        on_right = anchor[0] < cam.w / 2
        px = (WIDTH - PAD) if on_right else PAD
        py = h - PANEL_H - PAD
        _, edge = _readout(d, pal, px, py, lns[reading], settled, on_right)
        # The leader stops at the panel's own edge, not at its text: the
        # first build drew it to where the type starts and ran the rule up
        # against the `1` of `12 COMMITS`.
        _leader(d, pal, (anchor[0] + view[0] * SS, anchor[1] + view[1] * SS),
                (edge, py + PANEL_H / 2), settled)
    else:
        _chronometer(d, pal, PAD, PAD - 12, _week_start(week_i), week_i + 1,
                     ground=False)
        _stations(d, pal, WIDTH - READOUT_RAIL + 34, READOUT_TOP + 8,
                  lns, reading)
        _foot(d, pal, h, lns[reading])
        _ticks(d, pal, h)

    return im if SS == 1 else im.resize((WIDTH, h), Image.LANCZOS)


def _foot(d, pal, h: int, lane: dict) -> None:
    """Three counts, never more: `animate._foot` proves four does not fit."""
    items = [("COMMITS", f"{lane['total']:,}"), ("FILES", f"{lane['files']:,}"),
             ("WEEKS", f"{lane['weeks']} / 53")]
    step = (WIDTH - 2 * PAD) / len(items)
    base = h - 18
    for i, (label, value) in enumerate(items):
        x = PAD + i * step
        _t(d, x, base - VALUE - LABEL - 12, label, LABEL, pal["dim"],
           tracking=0.05, where=f"foot label {i}")
        _t(d, x, base - VALUE, value, VALUE, pal["text"], bold=True,
           where=f"foot value {i}")


def _ticks(d, pal, h: int) -> None:
    """Corner ticks. GMUNK's interface.029, which Thomas marked `love`."""
    for x in (PAD - 14, WIDTH - PAD + 14):
        for y in (PAD - 22, h - PAD + 22):
            d.line([(x - 9) * SS, y * SS, (x + 9) * SS, y * SS],
                   fill=pal["dim"], width=SS)
            d.line([x * SS, (y - 9) * SS, x * SS, (y + 9) * SS],
                   fill=pal["dim"], width=SS)


_WEEK_STARTS: list[str] = []


def _week_start(i: int) -> str:
    global _WEEK_STARTS
    if not _WEEK_STARTS:
        doc = json.loads(FIELD_JSON.read_text(encoding="utf-8"))
        _WEEK_STARTS = [w["start"] for w in doc["weeks"]]
    return _WEEK_STARTS[i]


# --- build -------------------------------------------------------------------

CHRONO_H = 16 + LABEL + 12 + VALUE + 16


def check_layout() -> None:
    """The two collisions this module shipped once, as arithmetic.

    Both were found in a screenshot rather than in the code: a rule through
    `W51/53` on flight, and a station rail written over the foot values on
    readout. A screenshot only catches what someone happens to look at, so
    the same two sums now run before any frame is drawn and raise.
    """
    top = PAD + CHRONO_H - 16
    panel = FLIGHT_H - PANEL_H - PAD
    if panel <= top:
        raise ValueError(
            f"flight: the docked readout starts at {panel} and the "
            f"chronometer ends at {top}; FLIGHT_H must be at least "
            f"{top + PANEL_H + PAD + 1}")

    foot_label = READOUT_H - 18 - VALUE - LABEL - 12
    field_bottom = READOUT_H - READOUT_FOOT
    if foot_label < field_bottom:
        raise ValueError(
            f"readout: the foot label starts at {foot_label}, inside the "
            f"field band that ends at {field_bottom}; READOUT_FOOT must be "
            f"at least {18 + VALUE + LABEL + 12}")

    rows = 1 + len(LANE_ORDER)          # one group header, five lanes
    rail = (READOUT_TOP + 8 + rows * LABEL + STATION_GROUP_GAP
            + (rows - 2) * STATION_ROW_GAP)
    if rail > foot_label:
        raise ValueError(
            f"readout: the station rail ends at {rail} and the foot label "
            f"starts at {foot_label}")


def build(variant: str, theme: str) -> dict:
    """One finished plate: frames, the smaller encoding, and both sizes."""
    check_layout()
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; have {VARIANTS}")
    if theme not in THEMES:
        raise ValueError(f"unknown theme {theme!r}; have {THEMES}")

    cells, cols, _rows = grid()
    if cols != GRID_COLS:
        raise ValueError(f"field-grid.json is {cols} columns, not {GRID_COLS}")
    lns = lanes()
    pal = palette(theme)

    path = camera_path()
    plan = schedule(lns, path)
    frames = [_frame(variant, theme, i, cells, lns, pal, plan, path)
              for i in range(FRAMES)]
    # 24 rather than 48. At SS 1 the plate is already close to a palette
    # image -- ground, five substrate steps, the focal white and antialiased
    # type -- so the extra 24 entries were spent on glyph edges and bought
    # nothing a reader can see, at 4% of the file.
    data, ext, sizes = encode(frames, FPS, colours=24)

    from io import BytesIO
    buf = BytesIO()
    # The reduced-motion still is the frame where the largest lane is being
    # read, not frame zero, because frame zero is the smallest of the five.
    big = max(plan, key=lambda w: lns[w["lane"]]["total"])
    at = (big["start"] + big["frames"] // 2) % FRAMES
    frames[at].save(buf, format="PNG", optimize=True)

    return {"variant": variant, "theme": theme, "data": data, "ext": ext,
            "sizes": sizes, "still": buf.getvalue(), "still_frame": at,
            "frames": len(frames), "fps": FPS, "seconds": len(frames) / FPS,
            "size": (WIDTH, frames[0].height),
            "alt": ALT[variant],
            "lanes": lns, "plan": plan}
