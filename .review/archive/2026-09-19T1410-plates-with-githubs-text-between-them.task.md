# The page is plates with GitHub's text between them
Written: 2026-09-19

`b8a38235` put every asset on Atrium's palette and gave each its own field.
**That worked and it exposed the real problem.**

Thomas, looking at the result: *"it looks quite weird, I think the GitHub page
needs a full redesign."*

**He is right, and the diagnosis is structural, not chromatic.** Rasterised, the
page is:

* **seven full-width plates, all roughly the same width and weight**, stacked
* **GitHub's default prose between them** — small, grey, system-font, nothing to
  do with the plates
* no hierarchy: the BlueBand halftone and the Atrium lattice get the same space
  as a four-box flow diagram
* very long, and nothing tells the eye where to start

The previous task said *"the pieces are right, everything between them is not."*
**The pieces are now also wrong, because they are all the same piece at the same
size.**

## The insight this redesign turns on

**GitHub strips CSS from prose. It cannot strip text inside an SVG.**

`b8a38235` reported exactly what GitHub removes and concluded the typography
between plates is not ours. **That is true, and the conclusion should be to stop
putting words there.**

Text that belongs to the design — a project's line, a figure's caption, a
heading — **can live inside the plate, typeset properly, in the right face at
the right size.** Only genuinely structural text stays as markdown.

**Work out what that costs.** Text in an SVG is not selectable, not searchable
by GitHub, and needs an accurate `alt`. **Say where the line falls**: what must
stay real text for accessibility and search, and what can move into the plate.
This is the central judgement and the report should argue it.

## What to change

**Hierarchy.** One thing should dominate. Everything else is smaller. **Decide
what the page is for** — a recruiter scanning for ninety seconds — and let that
choose.

**Rhythm.** Seven plates at one width is a list, not a composition. Vary width,
height and density. A four-box flow diagram does not need the space a halftone
render does.

**Length.** It is very long. **Say what you cut and why.**

**An entry point.** After the hero the eye has nowhere to go. Give it one.

## Constraints

* **Palette from `atrium-design` tokens.** Already wired. Do not reintroduce a
  hand-picked colour; `bin/conformance.py` will catch it.
* **Dark field everywhere.** The light variant was deliberately dropped and
  that decision stands.
* **No invented metrics.** Every number traceable or absent.
* **`make build` reproduces the README; `pytest tests -q` green.**
* **Do not touch `showroom/atrium-lattice.png`** — inverted and contrast-lifted
  deliberately.

## Evidence

**Rasterise the whole page and show it, at desktop and phone width.** Thomas has
now rejected three versions of this page. **A report without the rendered page
is not a report**, and the previous rejection was made from the render, not the
description.

**Show the before and after side by side** if you can, because the argument is
about composition and that is only visible as a pair.

## Stop conditions

- **Moving text into plates breaks accessibility beyond what `alt` can carry**:
  say so, and keep it as prose. **Accessibility beats aesthetics here** and a
  portfolio nobody can read with a screen reader is a worse outcome than an
  ugly one.
- **The composition cannot be judged without Thomas choosing what dominates**:
  render two options and let him pick. **Do not average them.**
- **Three hours**: stop and report.

---

## Added 2026-09-19, after Thomas saw the rendered page

Two more findings from the render, both the same root cause as the typography.

**The blue links clash.** Markdown links get **GitHub's default blue**, which
cannot be styled, and against a warm dark field it reads as broken rather than
designed. He said so directly: *"the red and blue don't work."*

**This is the same constraint as the prose.** A markdown link belongs to GitHub.
A link inside an SVG is yours — colour, weight, everything. **An `<a>` inside an
SVG works on GitHub and can carry the palette.**

So the Start-here list and the per-project repo lines are candidates to move
into plates. **Weigh it against accessibility exactly as for the text**: a link
inside an SVG is not crawled and may not be reachable by keyboard. **If a link
must stay markdown for that reason, say so and let it be blue** — a blue link
that works beats a styled one that does not.

**There are no animations.** He said so: *"there's also barely any cool
animations."*

**GitHub strips `<script>` from SVG but renders CSS animation and SMIL inside
it.** So the field can move, and the marks are already there.

**Use it once, where it means something.** The contribution field could settle
in. The lattice could drift. **One moving thing, not five** — five is a
carousel, one is a signature. The rule that nothing is drawn that carries
nothing applies to motion too: **motion that means nothing is decoration.**

**Check what it costs**: an animated SVG runs whenever the page is open. Say
whether it respects `prefers-reduced-motion`, because a page that moves at
someone who asked it not to is a defect.

**Both are subordinate to the composition.** The page being a stack of
same-sized plates with GitHub text between them is still the main problem.
**Do not spend the session on an animation and leave the layout as it is.**
