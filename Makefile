PORT ?= 8000

.PHONY: preview

# Serve the site at http://localhost:$(PORT). Pages use root-relative paths, so they need a server.
preview:
	@echo "Serving ykimura.dev at http://localhost:$(PORT) (Ctrl+C to stop)"
	python3 -m http.server $(PORT)
