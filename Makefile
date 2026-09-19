PYTHON ?= python3
PREVIEW_DIR := preview

.PHONY: build preview page clean

build:
	$(PYTHON) -m generators.build

# Rasterise with rsvg-convert. cairosvg was the original choice and cannot
# work under make on macOS: it finds libcairo through ctypes, and SIP strips
# DYLD_LIBRARY_PATH from the shell make spawns, so Homebrew's prefix is
# invisible. Its error names `libcairo-2.dll`, a Windows filename, which sends
# you looking in entirely the wrong place. rsvg-convert needs no library path.
RSVG ?= $(shell command -v rsvg-convert 2>/dev/null)

# No -b any more. Every asset paints Atrium's field as its first element, so
# there is nothing for a rasteriser background to show through and no theme
# suffix left to switch on: one asset, one ground, whatever page it lands on.
# The -b flag mattered when the assets were transparent, because rsvg
# composites onto white and a dark-theme asset drawn in near-white on white
# is invisible. A preview that cannot be judged is worse than no preview.
preview: build
	@mkdir -p $(PREVIEW_DIR)
	@test -n "$(RSVG)" || { echo "rsvg-convert not found. brew install librsvg"; exit 1; }
	@for svg in assets/*.svg; do \
		out="$(PREVIEW_DIR)/$$(basename $$svg .svg).png"; \
		$(RSVG) -w 1200 -o "$$out" "$$svg" && echo "rasterised $$out"; \
	done

# The assets one at a time answer "is this asset right". They cannot answer
# "does this page hold together", which is the question that has been failed
# twice, so `page` renders the whole README through GitHub's own markdown
# renderer at desktop and phone width, in both themes.
page: build
	$(PYTHON) bin/page_preview.py

clean:
	rm -rf $(PREVIEW_DIR)
