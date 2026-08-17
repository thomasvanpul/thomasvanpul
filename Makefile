PYTHON ?= python3
PREVIEW_DIR := preview

.PHONY: build preview clean

build:
	$(PYTHON) -m generators.build

preview: build
	@mkdir -p $(PREVIEW_DIR)
	@$(PYTHON) -c "import cairosvg" 2>/dev/null || { \
		echo "cairosvg not installed. Install with: pip install cairosvg"; exit 1; }
	@for svg in assets/*.svg; do \
		out="$(PREVIEW_DIR)/$$(basename $$svg .svg).png"; \
		$(PYTHON) -c "import cairosvg; cairosvg.svg2png(url='$$svg', write_to='$$out', output_width=1200)" && \
			echo "rasterised $$out"; \
	done

clean:
	rm -rf $(PREVIEW_DIR)
