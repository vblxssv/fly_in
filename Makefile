MAP ?= maps/challenger/01_the_impossible_dream.txt
ALGORITHM ?= dijkstra
RENDERER ?= arcade
LOGGER ?= file

VENV = .venv

ifeq ($(OS),Windows_NT)
	PYTHON = $(VENV)/Scripts/python.exe
else
	PYTHON = $(VENV)/bin/python3
endif


.PHONY: run clean lint install

install: $(VENV)/.installed

$(VENV)/.installed: requirements.txt
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	touch $(VENV)/.installed


run: install
	$(PYTHON) main.py --map $(MAP) --algorithm $(ALGORITHM) --renderer $(RENDERER) \
		--logger $(LOGGER)


lint: install
	$(PYTHON) -m flake8 src/
	$(PYTHON) -m mypy src/ --disallow-untyped-defs


clean:
	rm -rf $(VENV)
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +