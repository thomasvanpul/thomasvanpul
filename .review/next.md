# A profile with something to look at
Written: 2026-09-17

Thomas, 2026-09-17: *"I want way more added to my profile in terms of design,
and way more improvements in our designs"*, and *"for certain projects I want
automatic previews or showrooms"*.

**It stays generated.** No hand-edited README. Everything through `generators/`
and `content.py`, and `make build` must keep reproducing the page.

## Read this first

His design taste is recorded and it cuts against the current page:

* **Density is a positive, provided every mark means something.** The reference
  he settled on is GMUNK's *Tron: Ares* computer-vision work — vast dark fields
  of thousands of small marks where position and density carry the information.
* **He rejects one layout template reused across a page.** Every featured
  section here is currently heading → prose → diagram → link → rule.
* **He rejects decoration that carries nothing.**
* **He responds to references, not descriptions.**

**The hero is a name, one subtitle and a small planet on a mostly empty canvas.**
That is the gap. It is not that it is ugly; it is that it is empty, and empty is
the one thing his taste is not.

## Part 1 — the hero earns its space

Redesign `generators/svg/hero.py` so the canvas carries information rather than
air.

**Every mark must mean something** — that is his standing rule and the point of
the exercise. The generator already has live GitHub data in `build.py`
(`_load_data`), so marks can be real: repositories, commits over time, languages
by volume, years active.

**Do not add ornament.** If a mark cannot be traced to a number, it does not go
in. **State in the report what each element encodes.**

The existing subtitle rotation in `content.py` (`HERO_SUBTITLES`) stays.

## Part 2 — showrooms

**This is the thing he asked for that does not exist.**

Projects should show themselves. Specifically:

* **Atrium** already renders stills every build into `~/.atrium/stills/<sha>/` —
  four octaves plus a descent video. **A still is a showroom.** Work out how one
  reaches this repo: committed asset, a second workflow, or a generated SVG that
  embeds a downscaled frame. **Say what you chose and what it costs.**
* **Interstellar Sanctuary** is live at `interstellarsanctuary.com`. A
  screenshot is a showroom. **Can the Action take one?** If it needs a headless
  browser in CI, say what that costs in workflow time.
* **BlueBand** has a render pipeline in `blueband-concept`.

**Pick the ones that are genuinely automatable and say plainly which are not.**
A showroom that needs Thomas to drop a file in by hand is not automatic, and
saying so is a real answer.

**Constraint: the page must not become slow.** It already loads thirteen images.
**Report request count and total bytes before and after**, and if showrooms push
it up, say by how much and propose the trade.

## Part 3 — Atrium goes on the profile at all

His largest project is not mentioned. **18,470 lines across 75 Swift files, 177
commits, 91 in the last seven days.** A Metal-rendered spatial environment
drawing **218,000 real events from 31 repositories**, **38% of the codebase
automated checks** (418 assertions plus screen-readback tests), 0% idle CPU,
10 MB resident.

**Write it honestly.** The measured record is at
`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/vault_general/Atlas/Projects/Atrium/Verified-Record.md`
and states what may not be claimed: **no users, no release, acceptance never
passed.** The story is scale, rigour and method.

The strongest true line: **a test suite that gave a different verdict on
identical code in 13 of 33 runs, diagnosed by running one frozen binary 33 times
over 6.5 hours and comparing 448 values per run.**

## Part 4 — break the template

Featured entries currently share one shape. **Give them different structures.**
One can lead with its diagram, one with a single number, one with prose. **Say
why each got the shape it did.**

And **the six identical `rule` SVGs**: cut them, or make the separator carry
something. Six requests for decoration is the thing his rules forbid.

## The snake stays

He likes it. **Do not remove it.** It is the one element not generated here, so
**see whether it can be made his**: restyle to the profile palette if
`snake.yml`'s action exposes colours, or regenerate an equivalent from the
contribution data `stats` already fetches. **Leaving it untouched is a
legitimate answer** if the effort does not repay — say so.

## Constraints

* **`.claude/gate` green.** It is `pytest tests -q` then
  `python3 -m generators.build`, proven to fail on a broken generator.
* **`make preview` now works** via `rsvg-convert` — cairosvg cannot work under
  make on macOS because SIP strips `DYLD_LIBRARY_PATH`. **Use it. Rasterise
  everything you make and look at it.**
* **No badge soup, no shields.io, no emoji headers.**
* **No invented metrics.** Every number traceable or absent.
* Do not touch `.github/workflows/` unless a chosen option requires it, and say
  so if it does.

## Evidence

* `make build` output, README diff summarised
* **request count and total asset bytes, before and after**
* **rasterised previews of everything new**, and a sentence on how the page reads
  at phone width
* **Thomas judges this by looking.** A report with no images is not done.

## Stop conditions

- **A hero element cannot be traced to real data**: leave it out, say what you
  dropped.
- **No showroom is automatable**: say so plainly with the reason for each. That
  is a complete answer.
- **The page gets materially slower**: report the numbers and stop before
  committing.
- **Three hours**: stop and report.
