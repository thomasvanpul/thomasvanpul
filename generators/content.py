"""Hand-written prose for the profile README, keyed by repo name where applicable.

Nothing in here is generated. build.py never composes sentences; it only slots
these strings into a fixed layout.
"""

# Which section the page is built around. One thing dominates and everything
# else is smaller; averaging the two is what produced a page of seven equal
# plates.
#
# Set to "atrium" on 2026-09-19, by Thomas: "atrium way too little". It is his
# main project and it was getting the least space on the page -- a 760-wide
# lattice below a 1200-wide render of a different project. The lattice now
# takes the full column and is the first thing under his name, and BlueBand's
# render is gone rather than shrunk (see SHOWROOMS).
DOMINANT = "atrium"

# Plate widths per option. Width is the only hierarchy lever a README has, and
# it is also the divisor that sets apparent type size -- see svg/figures.py.
LAYOUT = {
    "atrium": {
        "order": ["atrium", "blueband-concept", "Finance-Tracker"],
        # One key, because there is one showroom. Width is the divisor for
        # type and the multiplier for everything else: at 760 the lattice's
        # pitch was 4.1 units and its lightest mark 0.9 wide, a hairline. At
        # the full 1200 the same frame is drawn with marks you can see, which
        # is most of why it was reading as "too little".
        "showroom_w": {"atrium": 1200},
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

# Cut 2026-09-19 with the field it captioned: FIELD_LEGEND read "One mark, one
# contribution, shaded by month". A picture that needs a caption to be read at
# all is the caption doing the work, and the four figures below the plate were
# already saying it in words. See svg/hero.py for the measurement.

# Second sentence cut 2026-09-19 -- "either a thing that moves or a thing that
# tracks something" is a taxonomy of a list the reader is about to read anyway.
INTRO = "I build hardware and the software that runs it."

# "Start here" was cut 2026-09-19, and it is the one cut here that was not
# asked for by name. It was a heading and three links, one per project, each
# with a one-line claim after it. Two of the four points above remove its
# reason to exist: Atrium is now the first thing under the name rather than the
# fourth, and every project body is now the single line that Start here was
# already setting -- so the page stated each project's claim twice, a screen
# apart, and the first statement was the one the eye hit first. Reinstating it
# is this block and `_start_here` in build.py.

# Per-repo prose. Keys match the "name" field in data/repos.sample.json.
FEATURED = {
    "blueband-concept": {
        "heading": "BlueBand",
        # Three sentences became one, 2026-09-19. What the chain *is* was
        # spelled out link by link -- enclosure fits board, board fits sensor
        # loop, app reads the output -- which is the list in the first clause
        # with a verb attached to each item.
        "body": "A wearable motion band, in development — enclosure, board, firmware "
                "and app, one person doing the whole chain.",
        "repo_suffix": "concept model and the render pipeline. Web and CAD repos are private.",
        # The build-chain strip goes too, and this is the judgement call in the
        # task rather than a line of it. Thomas asked for the concept render
        # gone and for BlueBand at "the same weight as the others"; Numeris
        # carries no diagram, so a diagram here would leave BlueBand heavier
        # than the section it is meant to match. The strip is the smaller of
        # the two things it could have been, so it is the reversible one:
        # deleting this key brings it back.
        "flow": False,
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
        # Cut to one line, 2026-09-19. The list of what daily use forced --
        # rate limits, dirty data, cache invalidation, latency -- was four
        # examples of the claim in the clause before it.
        "body": [
            "A finance app I use daily: Plaid in, market data alongside it, normalised "
            "into Postgres, out through a typed API. Daily use is what makes it real.",
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
    # Cut again 2026-09-19, to two lines each at the profile column width.
    # Nothing true was dropped and the third paragraph is intact in substance:
    # what went was the restatement around it. "Moving forward through it is
    # moving back through the history" is "depth is recency" said twice; "one
    # frozen binary, 33 runs over 6.5 hours, 448 values compared per run" is
    # the shape of the 13-of-33 figure rather than a second finding; and "it
    # would be dishonest to file it as anything else" is the sentence before it
    # defending itself. The honest-state claim itself is load-bearing and is
    # still here in full -- see Atlas/Projects/Atrium/Verified-Record.md.
    "body": [
        "A spatial desktop for macOS, in Swift and Metal. It draws the machine's own "
        "record as a navigable three-dimensional field: every mark a real event, depth "
        "is recency.",
        "The measurement is the part worth reading. The suite returned a red verdict on "
        "**`13 of 33` runs of unchanged code** — the scene was anchoring to wall-clock "
        "time at process start, and pinning it collapsed 393 drifting values to 5 "
        "timings and 3 pixels of GPU noise.",
        "**No users, no release, and the acceptance harness has never passed.** "
        "Engineering depth, not delivery.",
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
        "Malaysia property launch map with an EdgeProp collaborator, "
        "[password-gated](https://interstellarsanctuary.com) while licensing is settled.",
    ),
    (
        "HFQ forming research",
        "Hot Form Quench forming with Dr Nan Li at the Dyson School, remote since Aug 2026.",
    ),
    (
        "Air defence economics",
        "a self-directed paper; every figure regenerable from a CSV by one script.",
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
        # Retightened 2026-09-19, when this became the full-column lead. The
        # previous band, (0.42, 0.44, 1.00, 0.86), was chosen to sit at 760
        # wide. Drawn at 1200 its left half is a void: mean darkness per sixth,
        # left to right, was 1.3, 0.7, 2.0, 3.6, 5.3, 4.7 on the 0-9 scale, so
        # the picture read as pushed into the right-hand third of its own
        # frame. Measured, not eyeballed -- at 760 the same imbalance was there
        # and small enough to miss.
        #
        # This band runs 4.2, 5.1, 5.8, 5.6, 5.2, 4.5: evenly inked across the
        # full width, mean 5.07 against 2.95. Still a wide band at 132x69
        # rather than the near-square that a deeper crop gives, because the
        # lead image sets the height of the first screen.
        "crop": (0.70, 0.56, 1.00, 0.80),
        "cols": 132,
        "aria": "The Atrium lattice at ten times magnification, drawn as a "
                "halftone dot screen: thousands of small marks, each one a real "
                "commit, file change or test run",
        "caption": "A real frame at 10x: every mark is one event, from one of "
                   "31 repositories.",
    },
}

# BlueBand's showroom was removed 2026-09-19, by Thomas: "blueband getting way
# too much, and no i don't want that band there". It was the three-quarter
# render of the module and band, screened to a 112-column halftone and drawn at
# the full 1200 column -- the largest object on the page, above the project that
# was supposed to be leading it. It is not shrunk to a smaller plate because a
# smaller version of an unwanted picture is still the picture. The source is
# public and unchanged at
# raw.githubusercontent.com/thomasvanpul/blueband-concept/main/renders/01_three_quarter_with_band.png,
# so reinstating it is this dict entry and nothing else.

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
