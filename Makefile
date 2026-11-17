PYTHON := .venv/bin/python
HOST ?= root@home

.PHONY: serve build setup publish dry-run

setup: .venv

.venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

serve: .venv
	$(PYTHON) serve.py

build: .venv
	$(PYTHON) publish.py

publish: .venv
	$(PYTHON) deploy_sky.py --host $(HOST)

dry-run: .venv
	$(PYTHON) deploy_sky.py --dry-run --host $(HOST)
