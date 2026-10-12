# GitHub profile: interactive, not animated

Thomas, 12 Oct: "i dont want it to be animation i want it to be interactive". The profile
README is what github.com/thomasvanpul shows.

## Constraint

A profile README cannot run JavaScript. Interactive here means things a visitor clicks or
opens that change what they see:
- collapsible `<details>` sections (each project opens into a short card: what it is, a photo
  or render, the live link, the repo link);
- clickable image tiles that go to the live site, the case page on thomasvp.com/work/<id>,
  or the repo;
- state that updates on its own through GitHub Actions (for example a "currently building"
  line regenerated daily from recent commit activity across his public repos);
- optionally an issue-driven element (a visitor opens a templated issue, an Action replies
  and updates the README) only if it can be done without spam risk; say if not.

## Do

1. Read the current README, the generators/, showroom/ and assets/ folders, and the earlier
   profile work, to keep what already works.
2. Remove the animated pieces (animated SVG/GIF banners); keep static versions if they read well.
3. Build the interactive version above. Every claim about Thomas must match what the repos and
   thomasvp.com already say publicly; invent nothing. No em dashes in copy.
4. Check it renders: GitHub sanitises HTML (no style, no script); test with the GitHub
   markdown API (`gh api markdown`) or a render preview and look at the result at 390px and 1280px.
5. Tests in tests/ still pass. Commit on a branch, open a PR, do not merge.

## Report

What a visitor can now click or open, before and after renders, the PR link, and anything
that needs Thomas.
