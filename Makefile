PYTHON ?= python3
PREVIEW_DIR := preview

.PHONY: build preview clean

build:
	$(PYTHON) -m generators.build

# Rasterise with rsvg-convert. cairosvg was the original choice and cannot
# work under make on macOS: it finds libcairo through ctypes, and SIP strips
# DYLD_LIBRARY_PATH from the shell make spawns, so Homebrew's prefix is
# invisible. Its error names `libcairo-2.dll`, a Windows filename, which sends
# you looking in entirely the wrong place. rsvg-convert needs no library path.
RSVG ?= $(shell command -v rsvg-convert 2>/dev/null)

# Each theme is rasterised onto the background GitHub actually serves it on.
# Without -b, rsvg-convert composites onto transparency, which most viewers
# show as white — and a dark-theme asset drawn in #e6edf3 on white is
# invisible. Previews that cannot be judged are worse than no previews.
preview: build
	@mkdir -p $(PREVIEW_DIR)
	@test -n "$(RSVG)" || { echo "rsvg-convert not found. brew install librsvg"; exit 1; }
	@for svg in assets/*.svg; do \
		out="$(PREVIEW_DIR)/$$(basename $$svg .svg).png"; \
		case "$$svg" in *-dark.svg) bg="#0d1117";; *) bg="#ffffff";; esac; \
		$(RSVG) -w 1200 -b "$$bg" -o "$$out" "$$svg" && echo "rasterised $$out"; \
	done

clean:
	rm -rf $(PREVIEW_DIR)
