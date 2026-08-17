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

ALSO_RUNNING_HEADING = "Also running"

# Ordered list of items in the "Also running" section. Each entry is
# (bold_name, body_prose).
ALSO_RUNNING = [
    (
        "Interstellar Sanctuary",
        "Malaysia property launch map, built with an EdgeProp collaborator. "
        "Government-database crawlers feeding a searchable map. "
        "Live at [interstellarsanctuary.com](https://interstellarsanctuary.com)",
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

SNAKE_DARK_URL = "https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake-dark.svg"
SNAKE_LIGHT_URL = "https://raw.githubusercontent.com/thomasvanpul/thomasvanpul/output/github-contribution-grid-snake.svg"
SNAKE_ARIA = "contribution snake"
