<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/hero-still.003b166.svg">
  <img alt="Thomas van Pul, Design Engineering at Imperial College London" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/hero.efad40a.svg">
</picture>

**2,774** contributions &nbsp;·&nbsp; **78 of 370** days active &nbsp;·&nbsp; **151** busiest day &nbsp;·&nbsp; **45** longest streak

<sub>One mark, one contribution, shaded by month &nbsp;·&nbsp; 2025-11 - 2026-09</sub>

**Design Engineering, Imperial College London.**

I build hardware and the software that runs it. Most of what is here is either a thing that moves or a thing that tracks something.

### Start here

**[BlueBand](#blueband)** &nbsp;·&nbsp; a wearable motion band — enclosure, board, firmware, app

**[Numeris](#numeris)** &nbsp;·&nbsp; a finance app I use daily — Plaid in, a typed API out

**[Atrium](#atrium)** &nbsp;·&nbsp; a spatial desktop in Swift and Metal, and its measurement

### BlueBand

<img alt="BlueBand concept render: the module and band, three-quarter view, drawn as a halftone dot screen" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/showroom-blueband-concept.bcc39d7.svg">

<sub>Canonical render from the concept repo, screened to monochrome at build time.</sub>

A wearable motion band, in development. One person doing the whole chain: the enclosure has to fit the board, the board has to fit the sensor loop, and the app has to make sense of what comes out.

<img alt="BlueBand build chain: CAD to PCB to firmware to app" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/flow-blueband-concept.073066c.svg">

Repo: [`blueband-concept`](https://github.com/thomasvanpul/blueband-concept) &nbsp;·&nbsp; concept model and the render pipeline. Web and CAD repos are private for now.

### Atrium

<img alt="The Atrium lattice at ten times magnification, drawn as a halftone dot screen: thousands of small marks, each one a real commit, file change or test run" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/showroom-atrium.85e9ed7.svg">

<sub>A real frame at 10x: every mark is one event, from one of 31 repositories.</sub>

<img alt="Atrium, measured: 18,470 lines of Swift across 75 files; 418 assertions covering 38% of the codebase; 218,016 real events from 31 repositories; 10 MB resident at 0% idle CPU." src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/atrium-figures.7cd3f65.svg">

| Atrium | measured 2026-09-16 |
| --- | --- |
| Tests | 418 assertions, 38% of the code |
| Events | 218,016 from 31 repositories |
| Runtime | 10 MB resident, 0% idle CPU |
| Acceptance | 11 criteria, all UNMEASURED |
| Interface | 3 of 19 designed elements built |

A spatial computing environment for macOS — Swift and Metal, running as a persistent desktop shell. It draws the machine's own record as a navigable three-dimensional field: every mark is a real event, and depth is recency, so moving forward through it is moving back through the history.

The part worth reading is the measurement. The suite returned a red verdict on **`13 of 33` runs of unchanged code** — one frozen binary, 33 runs over 6.5 hours, 448 values compared per run. The scene was anchoring to wall-clock time at process start; pinning it collapsed 393 drifting values to 5 timings and 3 pixels of GPU noise.

**No users, no release, and the acceptance harness has never passed.** This is evidence of engineering depth, not of delivery, and it would be dishonest to file it as anything else.

Private repo.

### Numeris

A personal finance app I use every day, which is why it exists: Plaid in, market data alongside it, normalised into Postgres, out through a typed API. Daily use is what makes it real — rate limits, dirty data, cache invalidation and latency had to be dealt with rather than designed around.

Repo: [`Finance-Tracker`](https://github.com/thomasvanpul/Finance-Tracker)

### Also running

**Interstellar Sanctuary** &nbsp;·&nbsp; Malaysia property launch map with an EdgeProp collaborator — government-database crawlers feeding a searchable map, [password-gated](https://interstellarsanctuary.com) while licensing is settled.

**HFQ forming research** &nbsp;·&nbsp; Hot Form Quench forming with Dr Nan Li at the Dyson School, remote since Aug 2026 — aluminium, steel, titanium, fibre metal laminates.

**Air defence economics** &nbsp;·&nbsp; a self-directed paper; every figure in it regenerable from a CSV by one script.

**IRIS** &nbsp;·&nbsp; an always-on personal assistant daemon on macOS. Private repo.

### Stack

|  |  |
| --- | --- |
| Software | Python · TypeScript · React · Node · PostgreSQL |
| Simulation & CAD | Fusion 360 · Ansys FEA · SimScale CFD · KiCad |
| Workshop | TIG welding · FDM printing · composite layup |

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake.svg">
  <img alt="contribution snake" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake-dark.svg">
</picture>


<sub>Second-year MEng Design Engineering, Dyson School, Imperial College London &nbsp;·&nbsp; Dutch · Penang / London</sub>

[thomasvp.com](https://thomasvp.com) &nbsp;·&nbsp; [linkedin.com/in/vanpulthomas](https://www.linkedin.com/in/vanpulthomas) &nbsp;·&nbsp; `vanpulthomas@gmail.com`

</div>
