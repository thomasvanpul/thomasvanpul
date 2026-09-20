# The whole page in Atrium's language, not one section of it
Written: 2026-09-19

`41f3a5f2` gave the page a dense hero from the real contribution record, a
BlueBand showroom, three differently-shaped featured entries, and an honest
Atrium section. Since then a **real lattice still** landed as an Atrium
showroom (`6ca49ec`).

Thomas, 2026-09-19: *"by Atrium design I mean the entire thing gets Atrium
design."*

**The page is currently GitHub-default with Atrium-shaped pieces in it.** The
pieces are right; everything between them is not.

## What Atrium's language actually is

Not a colour swap. It is recorded in `Atlas/Projects/Atrium/Decided.md` and
`topics/design-taste.md`, and the rules that matter here:

* **A dark field.** Warm, near-black, not GitHub grey.
* **Hue is reserved for state.** It is never used for looks. The palette is the
  warm ramp derived from 41 GMUNK frames: DayCurve −7.8° to +13.1°.
* **Density is a positive, provided every mark means something.** The reference
  is thousands of small marks where position and density carry the information.
* **Nothing is drawn that carries nothing.** The six `rule` SVGs were cut for
  exactly this.
* **He rejects one layout template reused across a page.** Already half-fixed.
* **Monospace for figures**, because a number that is measured should look
  measured.

## What to do

**Work out what is actually controllable.** GitHub strips most CSS from a
README, so the page's typography and background are not yours. **That is the
central constraint and the report must state it plainly.**

What *is* yours is every SVG, and the SVGs can carry their own field. So:

* **Give each asset its own dark field** rather than transparent-on-GitHub-grey,
  so the page reads as a continuous dark surface instead of images floating on
  default chrome. **Check this against light mode** — there are light variants
  and they must not become unreadable.
* **One palette across every asset.** Audit what each generator currently uses
  and unify on the warm ramp. Report which were off it.
* **The figures are the identity.** Monospace, wide tracking, the measured
  number large and its caption small — the treatment `atrium-figures` already
  has. **Apply it wherever a number appears.**
* **The space between sections.** With the rules gone there may be nothing
  holding them apart. If a separator earns its place it must carry something:
  a density gradient, a scale, a count. **If nothing earns it, use nothing.**

## What must not happen

* **No invented metrics.** Every number traceable or absent.
* **No badge soup, no shields.io, no emoji headers.**
* **`make build` must keep reproducing the README**, and `pytest tests -q` green.
  It is `.claude/gate` and it has been proven to fail on a broken generator.
* **Do not touch `showroom/atrium-lattice.png`.** It is inverted and
  contrast-lifted deliberately — the halftone maps bright to a large dot, so the
  un-inverted dark field reduced to almost nothing.

## Evidence

**Rasterise the whole page, dark and light, and at phone width.** `make preview`
works via `rsvg-convert`. **A report with no images is not done — Thomas judges
this by looking**, and he has rejected two versions of this page already.

## Stop conditions

- **A change would only look right in one colour scheme**: say so and do not
  ship it. Both must work.
- **GitHub strips what the design needs**: say exactly what it strips, and what
  the best achievable version is.
- **Two hours**: stop and report.
