PYTHON := .venv/bin/python
HOST ?= root@home
SKY_DIR := $(abspath ../sky)

.PHONY: serve build static-build setup publish dry-run

setup: .venv

.venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

serve: .venv
	$(PYTHON) serve.py

build:
	pnpm --dir "$(SKY_DIR)" run build
	find "$(SKY_DIR)/.output/public/assets" -type f -name '*.map' -delete
	cd "$(SKY_DIR)" && node scripts/recompress-public-assets.mjs && node scripts/sync-nitro-asset-manifest.mjs

static-build: .venv
	$(PYTHON) publish.py

publish: .venv
	$(PYTHON) deploy_sky.py --host "$(HOST)"

dry-run: .venv
	$(PYTHON) deploy_sky.py --dry-run --host "$(HOST)"
