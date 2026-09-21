PYTHON := .venv/bin/python

.PHONY: serve build setup

setup: .venv

.venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

serve: .venv
	$(PYTHON) serve.py

build: .venv
	$(PYTHON) publish.py
