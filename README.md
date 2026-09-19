<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/hero.156d9d0-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/hero.5b8980f-light.svg">
  <img alt="Thomas van Pul, Design Engineering at Imperial College London" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/hero.156d9d0-dark.svg">
</picture>

</div>

I build hardware and the software that runs it. Most of what is here is either a thing that moves or a thing that tracks something.

### BlueBand

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/showroom-blueband-concept.f5f9c6d-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/showroom-blueband-concept.9cd327c-light.svg">
  <img alt="BlueBand concept render: the module and band, three-quarter view, drawn as a halftone dot screen" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/showroom-blueband-concept.f5f9c6d-dark.svg">
</picture>

<sub>Canonical render from the concept repo, screened to monochrome at build time.</sub>

</div>

A wearable motion band, in development. One person doing the whole chain, which is the interesting part and also the hard part: the enclosure has to fit the board, the board has to fit the sensor loop, and the app has to make sense of what comes out.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/flow-blueband-concept.1ba4f76-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/flow-blueband-concept.98f7ec1-light.svg">
  <img alt="BlueBand build chain: CAD to PCB to firmware to app" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/flow-blueband-concept.1ba4f76-dark.svg">
</picture>

Repo: [`blueband-concept`](https://github.com/thomasvanpul/blueband-concept) &nbsp;·&nbsp; concept model and the render pipeline. Web and CAD repos are private for now.

---

### Numeris

A personal finance app I actually use every day, which is why it exists. Bank data in through Plaid, market data alongside it, normalised into Postgres, out through a typed API.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/flow-finance-tracker.6415abd-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/flow-finance-tracker.f7dda1b-light.svg">
  <img alt="Numeris data flow: bank via Plaid, ingest, Postgres, API, React UI" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/flow-finance-tracker.6415abd-dark.svg">
</picture>

Daily use is what makes it a real project: rate limits, dirty data, cache invalidation and latency all had to be dealt with rather than designed around.

Repo: [`Finance-Tracker`](https://github.com/thomasvanpul/Finance-Tracker)

---

### Atrium

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/atrium-figures.b534726-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/atrium-figures.9ae56ae-light.svg">
  <img alt="Atrium, measured: 18,470 lines of Swift across 75 files; 418 assertions covering 38% of the codebase; 218,016 real events from 31 repositories; 10 MB resident at 0% idle CPU." src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/atrium-figures.b534726-dark.svg">
</picture>

A spatial computing environment for macOS — Swift and Metal, running as a persistent desktop shell. It draws the machine's own record as a navigable three-dimensional field: every mark is a real event, a commit or a file change or a gate run, and pressing one opens the artefact it stands for. Depth is derived from recency, so moving forward through the field is moving through the history.

The part worth reading is the measurement. The test suite was found to return a red verdict on **13 of 33 runs of unchanged code**. Diagnosing it meant running one frozen binary 33 times over 6.5 hours and comparing 448 values per run; the cause was the scene anchoring to wall-clock time at process start. Pinning it collapsed 393 drifting values to 5 timings and 3 pixels of GPU noise.

**No users, no release, and the acceptance harness has never passed** — all eleven criteria currently read UNMEASURED. It runs daily on one machine and 3 of 19 designed interface elements are built. This is evidence of engineering depth, not of delivery, and it would be dishonest to file it as anything else.

Private repo. Figures measured 2026-09-16.

---

### Also running

**Interstellar Sanctuary** &nbsp;·&nbsp; Malaysia property launch map, built with an EdgeProp collaborator. Government-database crawlers feeding a searchable map. [interstellarsanctuary.com](https://interstellarsanctuary.com) is behind a password while the data licensing is settled.

**HFQ forming research** &nbsp;·&nbsp; remote work with Dr Nan Li at the Dyson School since Aug 2026. Hot Form Quench forming across aluminium, steel, titanium and fibre metal laminates.

**Air defence economics** &nbsp;·&nbsp; a self-directed paper. Every figure in it has to be regenerable from a CSV by running one script, so the analysis code matters as much as the writing.

**IRIS** &nbsp;·&nbsp; an always-on personal assistant daemon on macOS. Private repo.

---

### Stack

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/orbit.56a5c23-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/orbit.1711996-light.svg">
  <img alt="Tools in orbit: Python, TypeScript, React, Node, PostgreSQL, Fusion 360, Ansys FEA, SimScale CFD, KiCad, TIG welding, FDM printing, composite layup" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/orbit.56a5c23-dark.svg">
</picture>

</div>

---

<div align="center">

<picture>
<<<<<<< HEAD
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/stats.dc2eeda-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/stats.663dfe1-light.svg">
  <img alt="Contributions in the last 12 months" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/main/assets/stats.dc2eeda-dark.svg">
</picture>


<picture>
=======
>>>>>>> 742c92b (automatic snapshot 2026-09-19)
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake.svg">
  <img alt="contribution snake" src="https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake-dark.svg">
</picture>


<sub>Second-year MEng Design Engineering, Dyson School, Imperial College London &nbsp;·&nbsp; CV and the rest at <a href="https://thomasvp.com">thomasvp.com</a></sub>

[thomasvp.com](https://thomasvp.com) &nbsp;·&nbsp; [linkedin.com/in/vanpulthomas](https://www.linkedin.com/in/vanpulthomas) &nbsp;·&nbsp; `vanpulthomas@gmail.com`

</div>
