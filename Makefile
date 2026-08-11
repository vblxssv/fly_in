MAP ?= maps/challenger/01_the_impossible_dream.txt
ALGORITHM ?= dijkstra
RENDERER ?= arcade
LOGGER ?= file

VENV = .venv

ifeq ($(OS),Windows_NT)
	PYTHON = python
	VENV_PYTHON = $(VENV)/Scripts/python.exe
else
	PYTHON = python3
	VENV_PYTHON = $(VENV)/bin/python3
endif

.PHONY: run clean lint install

install: $(VENV)/.installed

$(VENV)/.installed: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt
	touch $(VENV)/.installed

run: install
	$(VENV_PYTHON) main.py \
		--map $(MAP) \
		--algorithm $(ALGORITHM) \
		--renderer $(RENDERER) \
		--logger $(LOGGER)

lint: install
	$(VENV_PYTHON) -m flake8 src/
	$(VENV_PYTHON) -m mypy src/ --disallow-untyped-defs

clean:
	rm -rf $(VENV)
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +