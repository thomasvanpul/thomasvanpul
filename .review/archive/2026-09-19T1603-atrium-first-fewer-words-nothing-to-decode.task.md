# The profile reads as Atrium-first, with fewer words and nothing he has to decode
Written: 2026-09-19
Queue: auto
Model: claude-opus-5

## Thomas's verdict on the current page, 19 Sep, verbatim

"certain things don't look right, blueband getting way too much, and no i don't
want that band there, atrium way too little and too much text everywhere and i
don't get all the dots under my name doesn't make sense."

So, four changes, each judged by how the page looks, not by a check passing:

1. **BlueBand shrinks, and the band render goes.** Remove the BlueBand concept
   render (the three-quarter halftone of the module and band) entirely. BlueBand
   stays as a project line at most, same weight as the others.
2. **Atrium becomes the lead.** It is his main project and currently gets the
   least space. The lattice imagery and what Atrium is should be the first thing
   a visitor understands after his name.
3. **Much less text everywhere.** Cut every block of prose to the fewest words
   that still say what the thing is. Prefer one line per project. No paragraph
   anywhere longer than two lines at 1440px.
4. **The dots under his name.** Find what they are (likely the hero's halftone
   dot screen or a data strip). If they encode something, it is not legible to
   him, which means it is not legible to anyone: either make the meaning obvious
   at a glance with a two-word label, or remove it. Default to remove.

Keep: the blue links (his decision earlier today), the dark field everywhere,
the Atrium tokens (`data/atrium-tokens.json`), and `make page` as the preview.

## Working tree, stated

Dirty before this task: `.github/workflows/snake.yml`, `.gitignore`,
`.claude/gate.timing`, `.review/*` are modified and uncommitted from earlier
sessions today. Read the diffs first. Commit what belongs to the 12:45 and 14:57
reports as its own commit with a message naming them, then start. If any diff is
unexplained, stop and report it rather than committing it.

## Verify

`make page` at desktop and phone width, before and after, both saved. Judge the
after-still against the four points above and say plainly for each whether it is
met. The gate must stay green without being loosened.

## Do not

- Do not push to GitHub. Thomas looks at the stills first.

## Report

Before and after stills at both widths, the four points each marked met or not,
and the word count of the page before and after.
