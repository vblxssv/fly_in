MAP ?= maps/challenger/01_the_impossible_dream.txt
LOGGER ?= file

VENV := .venv
VENV_PYTHON := $(VENV)/bin/python3
FLAKE8_EXCLUDE := .venv,.mypy_cache,.pytest_cache,__pycache__
PYTHON := python3

.PHONY: run debug clean lint lint-strict install

install: $(VENV)/.installed

$(VENV)/.installed: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt
	touch $(VENV)/.installed

run: install
	$(VENV_PYTHON) main.py \
		--map $(MAP) \
		--logger $(LOGGER)

debug: install
	$(VENV_PYTHON) -m pdb main.py \
		--map $(MAP) \
		--logger $(LOGGER)

lint: install
	$(VENV_PYTHON) -m flake8 . --exclude=$(FLAKE8_EXCLUDE)
	$(VENV_PYTHON) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	$(VENV_PYTHON) -m flake8 . --exclude=$(FLAKE8_EXCLUDE)
	$(VENV_PYTHON) -m mypy . --strict

clean:
	rm -rf $(VENV)
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
