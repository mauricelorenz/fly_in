PYTHON = python3
VENV = .venv
PIP = pip

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/$(PIP) install -r requirements.txt

run:
	$(VENV)/bin/$(PYTHON) main.py

debug:
	$(VENV)/bin/$(PYTHON) -m pdb main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --strict

.PHONY: install run debug clean lint lint-strict
