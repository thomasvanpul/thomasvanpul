"""Hand-written prose for the profile README, keyed by repo name where applicable.

Nothing in here is generated. build.py never composes sentences; it only slots
these strings into a fixed layout.
"""

# Which section the page is built around. One thing dominates and everything
# else is smaller; averaging the two is what produced a page of seven equal
# plates. "blueband" makes the object the focal point, "atrium" makes the
# measurement the focal point. Nothing else in the page changes.
DOMINANT = "blueband"

# Plate widths per option. Width is the only hierarchy lever a README has, and
# it is also the divisor that sets apparent type size -- see svg/figures.py.
LAYOUT = {
    "blueband": {
        "order": ["blueband-concept", "atrium", "Finance-Tracker"],
        # 760 rather than 560 for the lattice. Width is the divisor for type,
        # and it is the multiplier for everything else: at 560 the grid's pitch
        # is 4.1 units and its lightest mark 0.9 wide, which rasterises to a
        # hairline. At 760 the same picture is drawn with marks you can see.
        "showroom_w": {"blueband-concept": 1200, "atrium": 760},
        "figures_w": 560,
    },
    "atrium": {
        "order": ["atrium", "blueband-concept", "Finance-Tracker"],
        "showroom_w": {"blueband-concept": 620, "atrium": 1200},
        "figures_w": 900,
    },
}

HERO_NAME = "THOMAS VAN PUL"

HERO_ARIA = "Thomas van Pul, Design Engineering at Imperial College London"

# The four lines that used to rotate inside the hero plate, as one line of
# markdown. They left the plate because at 15px on a 1200 viewBox they read at
# 4.5px on a phone; here they are legible at every width and GitHub can search
# them. Same words, nothing added.
HERO_STANDFIRST = "**Design Engineering, Imperial College London.**"

# Cut 2026-09-19. It read "CAD · FEA · CFD · TypeScript · Python · Dutch ·
# Penang / London" and rode on the end of the field legend, which made a
# nine-item line under the hero out of two unrelated things: a legend for the
# plot above it and a list of tools. Every tool in it appears again in the
# Stack table, so it was the page saying the same thing twice within one
# screen. Where Thomas is from and where he works moved to the footer, which
# is where the rest of the biography already lives.

# The legend for the contribution field. It was 9px inside the plate, which is
# 2.7px on a phone.
FIELD_LEGEND = "One mark, one contribution, shaded by month"

INTRO = (
    "I build hardware and the software that runs it. Most of what is here is either "
    "a thing that moves or a thing that tracks something."
)

# The entry point. After the hero the eye had nowhere to go; this is where it
# goes. Three lines, three anchors, one claim each -- which is what ninety
# seconds actually buys a reader. It is markdown and not a plate because every
# line of it is a link, and a link cannot exist inside an <img>.
START_HERE_HEADING = "Start here"

START_HERE = [
    ("BlueBand", "blueband", "a wearable motion band — enclosure, board, firmware, app"),
    ("Numeris", "numeris", "a finance app I use daily — Plaid in, a typed API out"),
    ("Atrium", "atrium", "a spatial desktop in Swift and Metal, and its measurement"),
]

# Per-repo prose. Keys match the "name" field in data/repos.sample.json.
FEATURED = {
    "blueband-concept": {
        "heading": "BlueBand",
        "body": (
            "A wearable motion band, in development. One person doing the whole chain: "
            "the enclosure has to fit the board, the board has to fit the sensor loop, "
            "and the app has to make sense of what comes out."
        ),
        "repo_suffix": "concept model and the render pipeline. Web and CAD repos are private for now.",
        "flow_aria": "BlueBand build chain: CAD to PCB to firmware to app",
    },
    "Finance-Tracker": {
        "heading": "Numeris",
        # The flow diagram this repo used to carry was cut. It drew
        # BANK to INGEST to POSTGRES to API to UI, which is the sentence
        # directly above it with boxes around it. BlueBand's kept its diagram
        # because "one person doing the whole chain" is a claim the diagram
        # proves and the sentence only asserts.
        # Two paragraphs became one, 2026-09-19. The second opened "Daily use
        # is what makes it a real project", which is the first sentence of the
        # first paragraph restated as a topic sentence. The list it introduced
        # is the only part that carried anything, so it is now a clause.
        "body": [
            "A personal finance app I use every day, which is why it exists: Plaid in, "
            "market data alongside it, normalised into Postgres, out through a typed API. "
            "Daily use is what makes it real — rate limits, dirty data, cache invalidation "
            "and latency had to be dealt with rather than designed around.",
        ],
        "repo_suffix": None,
        "flow": False,
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
    # Was a run-on line of three bolded figures, and before that a row inside
    # the plate at 22px and 9px. It is a table now, for the reason the whole
    # section is being rebuilt: markdown gives you headings, paragraphs, lists,
    # tables and code, and a table is the only one of those that sets a column
    # of numbers without reading as a clump. Two rows are new here and neither
    # is new information -- "Acceptance" and "Interface" are the figures that
    # were buried mid-sentence in the third paragraph, which is exactly where a
    # reader skims past the part that matters most.
    "table_head": ("Atrium", "measured 2026-09-16"),
    "table": [
        # No "Swift | 18,470 lines across 75 files" row: the plate directly above
        # sets that same figure at 85px. Printing it again two lines later is the
        # clump in miniature — the same fact twice inside one screen.
        ("Tests", "418 assertions, 38% of the code"),
        ("Events", "218,016 from 31 repositories"),
        ("Runtime", "10 MB resident, 0% idle CPU"),
        ("Acceptance", "11 criteria, all UNMEASURED"),
        ("Interface", "3 of 19 designed elements built"),
    ],
    # Three dense blocks became three short ones. Nothing true was dropped:
    # the counts that were buried in prose are in the table above, and what is
    # left in each paragraph is the one claim it exists to make.
    "body": [
        "A spatial computing environment for macOS — Swift and Metal, running as a "
        "persistent desktop shell. It draws the machine's own record as a navigable "
        "three-dimensional field: every mark is a real event, and depth is recency, "
        "so moving forward through it is moving back through the history.",
        "The part worth reading is the measurement. The suite returned a red verdict "
        "on **`13 of 33` runs of unchanged code** — one frozen binary, 33 runs over "
        "6.5 hours, 448 values compared per run. The scene was anchoring to "
        "wall-clock time at process start; pinning it collapsed 393 drifting values "
        "to 5 timings and 3 pixels of GPU noise.",
        "**No users, no release, and the acceptance harness has never passed.** This "
        "is evidence of engineering depth, not of delivery, and it would be "
        "dishonest to file it as anything else.",
    ],
    "repo_line": "Private repo.",
    "figures_aria": "Atrium, measured: 18,470 lines of Swift across 75 files; 418 assertions covering 38% of the codebase; 218,016 real events from 31 repositories; 10 MB resident at 0% idle CPU.",
}

ALSO_RUNNING_HEADING = "Also running"

# Ordered list of items in the "Also running" section. Each entry is
# (bold_name, body_prose).
# One sentence each, down from two or three. These are the things that are
# *not* the argument of the page, and four three-line entries in a row was the
# longest unbroken run of prose on it.
ALSO_RUNNING = [
    (
        "Interstellar Sanctuary",
        "Malaysia property launch map with an EdgeProp collaborator — "
        "government-database crawlers feeding a searchable map, "
        "[password-gated](https://interstellarsanctuary.com) while licensing is settled.",
    ),
    (
        "HFQ forming research",
        "Hot Form Quench forming with Dr Nan Li at the Dyson School, remote since "
        "Aug 2026 — aluminium, steel, titanium, fibre metal laminates.",
    ),
    (
        "Air defence economics",
        "a self-directed paper; every figure in it regenerable from a CSV by one script.",
    ),
    (
        "IRIS",
        "an always-on personal assistant daemon on macOS. Private repo.",
    ),
]

STACK_HEADING = "Stack"

# The orbit plate is cut. It spent 330 viewBox units of page height setting
# twelve tool names at 12px on a 1200 viewBox -- 3.6px on a phone, which is
# texture and not a legend. The same twelve names as markdown are legible at
# every width, selectable, and findable by GitHub search, and cost one line.
# `generators/svg/orbit.py` and `data/orbit.json` are left in place, so
# reinstating it is a two-line change if this judgement is wrong.
# Was one line of twelve names in three groups separated by dots, which is a
# clump with punctuation in it: the groups were there and unreadable. Same
# twelve names, three rows, nothing added and nothing removed.
STACK_TABLE = [
    ("Software", "Python · TypeScript · React · Node · PostgreSQL"),
    ("Simulation & CAD", "Fusion 360 · Ansys FEA · SimScale CFD · KiCad"),
    ("Workshop", "TIG welding · FDM printing · composite layup"),
]

FOOTER_SUB = (
    "Second-year MEng Design Engineering, Dyson School, Imperial College London "
    "&nbsp;·&nbsp; Dutch · Penang / London"
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
        # Was (0.0, 0.10, 1.0, 0.92), which took the whole frame including the
        # quiet top-left quadrant: 28.8% of its cells carried ink, and once the
        # plate stopped painting a ground of its own there was nothing left to
        # give that emptiness an edge -- it read as a smudge on the page rather
        # than as a frame of anything. This is the dense band of the same still,
        # 52.2% inked on the reduced grid, and at 132x62 it is a wide band
        # rather than a near-square, which is the shape a supporting plate
        # wants next to a full-column one.
        "crop": (0.42, 0.44, 1.00, 0.86),
        "cols": 132,
        "aria": "The Atrium lattice at ten times magnification, drawn as a "
                "halftone dot screen: thousands of small marks, each one a real "
                "commit, file change or test run",
        "caption": "A real frame at 10x: every mark is one event, from one of "
                   "31 repositories.",
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
