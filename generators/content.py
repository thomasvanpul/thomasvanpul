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

# The page since 2026-09-24: the corridor Thomas picked on 19 Sep, and under
# it name, one line, links. Nothing else. `HERO_PICK` names the finish in
# `design/hero/` whose assets `generators/build.py` ships; `bin/hero.py`
# builds them. The alt text lives with the plate, in `corridor.ALT`.
HERO_PICK = "flight"
NAME = "Thomas van Pul"
# 5 Nov 2026: the second sentence was "I build hardware and the software that
# runs it", which no row in the vault's Atlas/Verified-Claims.md backs. This is
# the line thomasvp.com kept after its 6 Aug audit, which the register records.
LINE = ("MEng Design Engineering at Imperial College London. "
        "I build instruments, then use them.")
LINE_CLAIMS = ("edu-meng", "site-intro")

# --- what this page may say about Thomas, 5 Nov 2026 ---------------------------
#
# Only claims marked `verified: true` in the vault's Atlas/Verified-Claims.md
# may appear on a public page. Every card, list item and stack row below names
# the rows it rests on, and `generators/build.py` leaves out anything resting on
# a row that is not in this dict, so a claim cannot reach the page by being
# typed into a card. To bring a withheld card back (Atrium, IRIS), Thomas flips
# its rows in the vault and the ids are added here; nothing else changes.
# Each value says where the row is and when it was confirmed.
PUBLIC_CLAIMS = {
    "edu-meng": "MEng Design Engineering, Imperial College London (2025-2029); Thomas 2026-08-04",
    "site-intro": "thomasvp.com intro kept after the 2026-08-06 audit: "
                  "'Design engineering at Imperial. I build instruments, then use them.'",
    "handle-linkedin": "linkedin.com/in/vanpulthomas; Thomas 2026-08-05",
    "bb-uplyft": "BlueBand created at the upLYFT Wearable Tech Hackathon, Imperial; "
                 "team placed second; Thomas 2026-09-16",
    "bb-uplyft-date": "that hackathon was March 2026; Thomas 2026-09-16",
    "bb-build": "board in KiCad (two-layer ESP32-S3, custom printed), enclosure in "
                "CadQuery, the site; modular sports wristband; team working towards "
                "a launch; not open hardware; Thomas 2026-09-16, corrected 2026-10-13",
    "num-headline": "React, Node.js, PostgreSQL on Vercel; Plaid; Yahoo Finance; "
                    "Thomas 2026-08-04 (sweep)",
    "num-daily-use": "latency, API rate limits, dirty data, cache invalidation in "
                     "daily use; Thomas 2026-08-04 (sweep)",
    "icss-strum-booms": "designed and 3D-printed moulds for four carbon-fibre booms, "
                        "each over 2 m (Project Svarog); Thomas 2026-08-18",
    "icss-strum-doors": "designed carbon-fibre-reinforced doors (Project Svarog); "
                        "Thomas 2026-08-18",
    "ep-role": "interstellarsanctuary.com built with an EdgeProp employee, framed as "
               "a collaboration; Thomas 2026-08-05",
    "interstellar-dates": "that collaboration ran July to September 2026; Thomas 2026-09-03",
    "research-hfq": "with Dr Nan Li at the Dyson School since August 2026, HFQ forming "
                    "across Al, steel, Ti and FML; Thomas 2026-08-05",
    "urop-naming": "the work may be called a UROP; Thomas 2026-09-16",
    "skl-prog": "Python, JavaScript, SQL, MATLAB; Thomas 2026-08-04 (sweep)",
    "skl-eng": "Fusion 360, Ansys FEA, SimScale CFD, TIG welding, composite tooling; "
               "Thomas 2026-08-04, extended 2026-08-23",
}

# Strings the register marks false or do-not-restore, plus the corrections in
# Thomas's own profile. None may appear on the page in any card, shown or not.
NEVER_ON_THE_PAGE = (
    "firmware",            # bb firmware: no firmware exists (2026-08-31)
    "open hardware", "open-hardware",  # bb-build correction 2026-10-13
    "one person",          # BlueBand is a team (bb-build)
    "First Class", "First-Class", "predicted First",  # edu-meng-nc-first-class
    "co-lead",             # icss-rocketry-colead is not a verified role
    "60+ teams", "200+ teams",  # falsified / unsourced field sizes
    "patent",              # track-bike patent pending is FALSE
    "licensing is settled",  # no row says why the site is gated
)

# --- the interactive page, 12 Oct 2026 ---------------------------------------
#
# Thomas: "i dont want it to be animation i want it to be interactive". A
# README runs no JavaScript, so interactive means what a visitor can open or
# click: each project is a <details> card, each picture is a link, and one
# line under the links is rewritten by the daily Action from real push data.
#
# Until 5 Nov every sentence below was copied from the prose that was on the
# page before 24 Sep. On 5 Nov each card was checked against the vault's
# Atlas/Verified-Claims.md and rewritten to the verified wording where the old
# one went further: BlueBand's "firmware" and "one person doing the whole
# chain" are both contradicted there (no firmware exists; BlueBand is a team).
#
# `lane` names the corridor lane whose still `bin/cards.py` draws for the card,
# None for a card with no lane. `repo` is the public repository, None where the
# work is private. `case` is the card's case page on thomasvp.com; the still
# links there when it exists, and to the repo otherwise. `claims` are the
# PUBLIC_CLAIMS rows every line of the card rests on: a card with any row
# missing from PUBLIC_CLAIMS is left off the page.
CARDS = {
    "atrium": {
        "lane": "ATRIUM · SURFACE",
        "lane_alt": "Atrium surface repository",
        "title": "Atrium",
        "what": "a spatial desktop for macOS, in Swift and Metal",
        "repo": None,
        # Withheld 5 Nov 2026: `atrium-build` and `atrium-drift` are TODO in the
        # register, awaiting Thomas since 2026-09-16. The still stays at the
        # top of the page (it is drawn from commit data, not from a claim); the
        # card returns when both rows are flipped and added to PUBLIC_CLAIMS.
        "claims": ("atrium-build", "atrium-drift"),
        "body": [
            "It draws the machine's own record as a navigable three-dimensional "
            "field: every mark a real event, depth is recency.",
            "The measurement is the part worth reading. The suite returned a red "
            "verdict on **13 of 33 runs of unchanged code**. The scene was anchoring "
            "to wall-clock time at process start, and pinning it collapsed 393 "
            "drifting values to 5 timings and 3 pixels of GPU noise.",
            "**No users, no release, and the acceptance harness has never passed.** "
            "Engineering depth, not delivery.",
        ],
        "table_head": ("Measured", "2026-09-16"),
        "table": [("Swift", "18,470 lines, 75 files")] + [
            # ATRIUM["table"], below, unchanged.
            ("Tests", "418 assertions, 38% of the code"),
            ("Events", "218,016 from 31 repositories"),
            ("Runtime", "10 MB resident, 0% idle CPU"),
            ("Acceptance", "11 criteria, all UNMEASURED"),
            ("Interface", "3 of 19 designed elements built"),
        ],
        "links": "Private repo.",
    },
    "blueband": {
        "lane": "BLUEBAND",
        "lane_alt": "blueband-concept",
        "title": "BlueBand",
        "what": "a modular sports wristband, in development",
        "repo": "blueband-concept",
        "case": "https://www.thomasvp.com/work/blueband",
        "claims": ("bb-uplyft", "bb-uplyft-date", "bb-build"),
        "body": [
            "Created at the upLYFT Wearable Tech Hackathon at Imperial in March 2026, "
            "where our team placed second.",
            "After the hackathon I designed and routed its two-layer ESP32-S3 board in "
            "KiCad and had it custom printed, built the enclosure in CadQuery, and "
            "built the site. The team is working towards a launch.",
        ],
        "repo_note": "concept model and the render pipeline. Board and enclosure "
                     "files are private.",
    },
    "numeris": {
        "lane": "NUMERIS",
        "lane_alt": "Finance-Tracker",
        "title": "Numeris",
        "what": "a portfolio tracker, in daily use",
        "repo": "Finance-Tracker",
        "case": "https://www.thomasvp.com/work/numeris",
        "claims": ("num-headline", "num-daily-use"),
        "body": [
            "A full-stack build: React, Node.js and PostgreSQL on Vercel, with Plaid "
            "for bank connections and Yahoo Finance for market data.",
            "Daily use is where the real problems came from: latency, API rate "
            "limits, dirty data and cache invalidation.",
        ],
        "repo_note": None,
    },
    "svarog": {
        "lane": None,
        "title": "Project Svarog",
        "what": "Imperial College Space Society's satellite project",
        "repo": None,
        "case": "https://www.thomasvp.com/work/svarog",
        "claims": ("icss-strum-booms", "icss-strum-doors"),
        "body": [
            "I designed and 3D-printed the moulds for four carbon-fibre booms, each "
            "over two metres long, and designed carbon-fibre-reinforced doors.",
        ],
        "links": "Society project; no public repo.",
    },
}

# The card whose still heads the page. Atrium leads (Thomas, 19 Sep: "atrium
# way too little"), so its card carries no second copy of the same picture.
LEAD_CARD = "atrium"

HERO_ARIA ="Thomas van Pul, Design Engineering at Imperial College London"

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

ALSO_RUNNING_HEADING = "Also"

# (bold_name, body_prose, claims). Rewritten 5 Nov 2026 against the register:
# "Air defence economics" and "IRIS" are gone because no row backs the first
# and `iris-daemon` is TODO; Interstellar Sanctuary lost "while licensing is
# settled", which nothing records, and gained its verified dates; the research
# line uses the name `urop-naming` allows.
ALSO_RUNNING = [
    (
        "Interstellar Sanctuary",
        "a Peninsular Malaysia property-launch map, built with an EdgeProp "
        "collaborator, July to September 2026. "
        "[Password-gated](https://interstellarsanctuary.com).",
        ("ep-role", "interstellar-dates"),
    ),
    (
        "UROP",
        "with Dr Nan Li at the Dyson School since August 2026, on Hot Form Quench "
        "forming across aluminium, steel, titanium and fibre metal laminates.",
        ("research-hfq", "urop-naming"),
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
# 5 Nov 2026: each row now lists only tools a verified row names. TypeScript,
# "FDM printing" and "composite layup" had none; JavaScript, SQL, MATLAB,
# CadQuery, 3D printing and "composite tooling" (the register's own words) do.
STACK_TABLE = [
    ("Software", "Python · JavaScript · SQL · React · Node.js · PostgreSQL · MATLAB",
     ("skl-prog", "num-headline")),
    ("Simulation & CAD", "Fusion 360 · Ansys FEA · SimScale CFD · KiCad · CadQuery",
     ("skl-eng", "bb-build")),
    ("Workshop", "TIG welding · 3D printing · composite tooling",
     ("skl-eng", "icss-strum-booms")),
]

FOOTER_SUB = (
    "Second-year MEng Design Engineering, Dyson School, Imperial College London "
    "&nbsp;·&nbsp; Dutch · Penang / London"
)

FOOTER_LINKS_CLAIMS = ("handle-linkedin",)
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
