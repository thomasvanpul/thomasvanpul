# Blue links stay. Make everything else good.
Written: 2026-09-19

`47e847b2` measured the thing that mattered and was right: **a README asset is a
fixed-ratio image in a fluid column**, so SVG type scales away — 0.82x on
desktop, **0.30x on a phone**, and 13 of 15 type sizes on the rejected page were
under 8px. Words came out of the plates. That stands.

Thomas has now seen A and B and rejected both: *"a mixture of poor colours, poor
interface, clumps of text and no animations."*

**One decision is made: the blue links stay.** He said so. **Stop fighting
GitHub's link colour** — it is a fixed point, and the palette has to work with it
rather than against it.

## What that changes

**GitHub's link blue is roughly `#4493f8` on dark.** Everything else on the page
is a warm ramp from `atrium-design`. That is the clash he keeps seeing, and it is
now a constraint rather than a bug.

**So the warm has to stop competing.** Options, and this is the judgement:

* **use warm sparingly** — one accent, not a field of it, so blue reads as the
  only strong colour and looks deliberate
* **cool the plates** — the tokens carry `field-cool-source`; a less saturated
  field sits under a blue link without arguing with it
* **let blue in** — if the links are blue, a plate may legitimately use blue too

**Whatever you choose, `bin/conformance.py` must stay green.** If a colour is
needed that is not a token, it goes in `EXCEPTIONS` with a written reason, in
`~/dev/atrium-design/bin/conformance.py`.

## "Clumps of text"

**He is right, and this is the harder half.** With the words out of the plates,
the page is now long paragraphs of markdown between images.

Markdown gives you headings, paragraphs, lists, tables and code. **That is the
whole toolbox.** So:

* **Shorter paragraphs.** The Atrium section is four dense blocks.
* **Use the structures markdown does have.** A table is not a clump. A short
  list is not a clump. The measured figures could be a table instead of a
  sentence.
* **Cut.** The page says a lot. **Say what you removed and why.**

## "No animations"

`47e847b2` showed SVG *type* scales away. **Marks do not** — the contribution
field and the lattice are legible at any width because they are texture.

**So animate a mark, not a word.** CSS animation inside an SVG renders on
GitHub. **One moving thing, not five.** It must respect
`prefers-reduced-motion`, and if it cannot, do not ship it.

**If an animation would cost legibility, do not.** The page being readable beats
the page moving.

## Then decide A or B, with a reason

Thomas did not pick. **Pick one and argue it in a sentence**, then render both
anyway so he can overrule.

## Constraints

* **`make build` reproduces the README; `pytest tests -q` green.**
* **No invented metrics.**
* **Do not touch `showroom/atrium-lattice.png`.**
* **`data/atrium-tokens.json` is a verbatim vendored copy** — conformance checks
  it byte for byte. Regenerate it from `atrium-design`, never hand-edit.

## Evidence

**Render desktop and phone, and show them.** He has rejected three versions from
the render. **A report without the rendered page is not a report.**

## Stop conditions

- **The warm palette cannot be made to work with GitHub's blue**: say so
  plainly. **That is a real finding** and it would mean the page should be
  near-monochrome with blue as its only colour.
- **Three hours**: stop and report.
