"""Hand-written prose for the profile README, keyed by repo name where applicable.

Nothing in here is generated. build.py never composes sentences; it only slots
these strings into a fixed layout.
"""

HERO_NAME = "THOMAS VAN PUL"

HERO_SUBTITLES = [
    "DESIGN ENGINEERING · IMPERIAL COLLEGE LONDON",
    "HARDWARE THAT SHIPS, SOFTWARE THAT RUNS",
    "CAD · FEA · CFD · TYPESCRIPT · PYTHON",
    "DUTCH · PENANG / LONDON",
]

HERO_ARIA = "Thomas van Pul, Design Engineering at Imperial College London"

INTRO = (
    "I build hardware and the software that runs it. Most of what is here is either "
    "a thing that moves or a thing that tracks something."
)

# Per-repo prose. Keys match the "name" field in data/repos.sample.json.
FEATURED = {
    "blueband-concept": {
        "heading": "BlueBand",
        "body": (
            "A wearable motion band, in development. One person doing the whole chain, "
            "which is the interesting part and also the hard part: the enclosure has to "
            "fit the board, the board has to fit the sensor loop, and the app has to "
            "make sense of what comes out."
        ),
        "repo_suffix": "concept model and the render pipeline. Web and CAD repos are private for now.",
        "flow_aria": "BlueBand build chain: CAD to PCB to firmware to app",
    },
    "Finance-Tracker": {
        "heading": "Numeris",
        "body": [
            "A personal finance app I actually use every day, which is why it exists. "
            "Bank data in through Plaid, market data alongside it, normalised into "
            "Postgres, out through a typed API.",
            "Daily use is what makes it a real project: rate limits, dirty data, cache "
            "invalidation and latency all had to be dealt with rather than designed around.",
        ],
        "repo_suffix": None,
        "flow_aria": "Numeris data flow: bank via Plaid, ingest, Postgres, API, React UI",
    },
}

# Atrium is a private repo, so repo discovery cannot find it and it carries no
# .profile.yml. It is written out here instead. Every figure is copied from
# Atlas/Projects/Atrium/Verified-Record.md, measured 2026-09-16 — including the
# three lines under "honest state", which are not optional decoration.
ATRIUM = {
    "heading": "Atrium",
    "lede_number": "18,470",
    "lede_caption": "LINES OF SWIFT, 75 FILES",
    "figures": [
        ("418", "ASSERTIONS · 38% OF CODE"),
        ("218,016", "EVENTS · 31 REPOS"),
        ("10 MB", "RESIDENT · 0% IDLE CPU"),
    ],
    "body": [
        "A spatial computing environment for macOS — Swift and Metal, running as "
        "a persistent desktop shell. It draws the machine's own record as a "
        "navigable three-dimensional field: every mark is a real event, a commit "
        "or a file change or a gate run, and pressing one opens the artefact it "
        "stands for. Depth is derived from recency, so moving forward through the "
        "field is moving through the history.",
        "The part worth reading is the measurement. The test suite was found to "
        "return a red verdict on **13 of 33 runs of unchanged code**. Diagnosing "
        "it meant running one frozen binary 33 times over 6.5 hours and comparing "
        "448 values per run; the cause was the scene anchoring to wall-clock time "
        "at process start. Pinning it collapsed 393 drifting values to 5 timings "
        "and 3 pixels of GPU noise.",
        "**No users, no release, and the acceptance harness has never passed** — "
        "all eleven criteria currently read UNMEASURED. It runs daily on one "
        "machine and 3 of 19 designed interface elements are built. This is "
        "evidence of engineering depth, not of delivery, and it would be dishonest "
        "to file it as anything else.",
    ],
    "repo_line": "Private repo. Figures measured 2026-09-16.",
    "figures_aria": "Atrium, measured: 18,470 lines of Swift across 75 files; 418 assertions covering 38% of the codebase; 218,016 real events from 31 repositories; 10 MB resident at 0% idle CPU.",
}

ALSO_RUNNING_HEADING = "Also running"

# Ordered list of items in the "Also running" section. Each entry is
# (bold_name, body_prose).
ALSO_RUNNING = [
    (
        "Interstellar Sanctuary",
        "Malaysia property launch map, built with an EdgeProp collaborator. "
        "Government-database crawlers feeding a searchable map. "
        "[interstellarsanctuary.com](https://interstellarsanctuary.com) is "
        "behind a password while the data licensing is settled.",
    ),
    (
        "HFQ forming research",
        "remote work with Dr Nan Li at the Dyson School since Aug 2026. "
        "Hot Form Quench forming across aluminium, steel, titanium and fibre metal laminates.",
    ),
    (
        "Air defence economics",
        "a self-directed paper. Every figure in it has to be regenerable from a CSV "
        "by running one script, so the analysis code matters as much as the writing.",
    ),
    (
        "IRIS",
        "an always-on personal assistant daemon on macOS. Private repo.",
    ),
]

STACK_HEADING = "Stack"

STACK_ORBIT_ARIA = (
    "Tools in orbit: Python, TypeScript, React, Node, PostgreSQL, "
    "Fusion 360, Ansys FEA, SimScale CFD, KiCad, "
    "TIG welding, FDM printing, composite layup"
)

FOOTER_SUB = (
    "Second-year MEng Design Engineering, Dyson School, Imperial College London "
    "&nbsp;·&nbsp; CV and the rest at <a href=\"https://thomasvp.com\">thomasvp.com</a>"
)

FOOTER_LINKS = (
    "[thomasvp.com](https://thomasvp.com) &nbsp;·&nbsp; "
    "[linkedin.com/in/vanpulthomas](https://www.linkedin.com/in/vanpulthomas) &nbsp;·&nbsp; "
    "`vanpulthomas@gmail.com`"
)

# Showroom sources, keyed by featured repo name. `cols` sets the halftone
# grid width and therefore the asset size; `crop` trims the render to a wide
# band around the product before reduction. Only public, already-committed
# images belong here — see .review/report.md for why the other two candidate
# showrooms are not automatable.
SHOWROOMS = {
    # Atrium's repo is private, so its render cannot be fetched the way
    # BlueBand's is. The still is committed to this repo instead and read from
    # disk — the same treatment, a different source. It is a real frame of the
    # lattice at 10x: 218,016 events from 31 repositories, every mark an event.
    "atrium": {
        "path": "showroom/atrium-lattice.png",
        "crop": (0.0, 0.10, 1.0, 0.92),
        "cols": 132,
        "aria": "The Atrium lattice at ten times magnification, drawn as a "
                "halftone dot screen: thousands of small marks, each one a real "
                "commit, file change or test run",
        "caption": "A real frame of the lattice at 10x. Every mark is an event "
                   "from one of 31 repositories; density is what the region has "
                   "been doing.",
    },
    "blueband-concept": {
        "url": "https://raw.githubusercontent.com/thomasvanpul/blueband-concept"
               "/main/renders/01_three_quarter_with_band.png",
        "crop": (0.04, 0.14, 0.96, 0.84),
        "cols": 112,
        "aria": "BlueBand concept render: the module and band, three-quarter view, "
                "drawn as a halftone dot screen",
        "caption": "Canonical render from the concept repo, screened to monochrome "
                   "at build time.",
    },
}

SNAKE_DARK_URL = "https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake-dark.svg"
SNAKE_LIGHT_URL = "https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake.svg"
SNAKE_ARIA = "contribution snake"

# Kept because Thomas likes it, and it is the one element on this page not
# generated here. Platane/snk takes per-output query parameters, so the two
# SVGs it publishes to the `output` branch can be asked for in this page's
# own colours instead of GitHub's defaults. The parameters live in
# .github/workflows/snake.yml; these URLs only have to match the filenames
# that workflow writes.

STATS_ARIA = "Contributions in the last 12 months"
