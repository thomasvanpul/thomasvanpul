# The profile is an Atrium interface, not a page with an Atrium picture on it
Written: 2026-09-19
Queue: auto
Weight: light
Model: claude-opus-5

## Why

Thomas looked at today's after-stills (Atrium leads, BlueBand render gone, dots
gone, a third shorter) and said: "I feel like for the GitHub profile we can be
more intelligent and use the Atrium over the entire thing, making it seem like
the interface." Today the page is a README with one lattice image at the top
and prose sections under it. He wants the whole page to read as Atrium.

## Premise, stated so it can be falsified

A GitHub README renders only Markdown, sanitised HTML and images (SVG is served
as an image, so no script and no interaction). "Atrium as the interface" must
therefore be built from generated images laid out by Markdown. If the stills show
that images cannot carry it without becoming unreadable on a phone (the 19 Sep
measurement: SVG type at 0.30x, 13 of 15 sizes under 8 px), say so and propose
the closest honest version rather than forcing it.

## Do, stop after step 3

1. **Design it as Atrium.** Each project is a region of one lattice field in its
   real data's grammar (commits, files, gates), the field runs the whole page
   length rather than one hero image, and the words are Atrium's micro-labels
   and docked panels: a name, a one-line what, a link. Read
   `Atlas/Projects/Atrium/Design-Language.md` and use
   `data/atrium-tokens.json` only. Keep: blue links, dark field, Atrium leading,
   BlueBand at the same weight as the rest, no dots under his name, far fewer
   words than even today's version.
2. **Two or three directions as `make page` stills**, desktop and phone, dark.
   One must be the most literal ("the page is one continuous field, sections are
   regions of it"), one the most readable.
3. **Judge each at phone width** with the smallest rendered type size measured,
   and say which you would ship.

## Working tree

Today's 16:03 work is uncommitted or committed per that report; do not push.
Build on it.

## Do not

- Do not push to GitHub.

## Report

The stills, the measured type sizes, your pick and why.
