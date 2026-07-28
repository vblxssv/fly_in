MAP ?= maps/challenger/01_the_impossible_dream.txt
ALGORITHM ?= dijkstra
RENDERER ?= arcade
LOGGER ?= file
VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip


.PHONY: run clean lint install

install: $(VENV)/bin/python3

$(VENV)/bin/python3: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: install
	$(PYTHON) main.py --map $(MAP) --algorithm $(ALGORITHM) --renderer $(RENDERER) \
		--logger $(LOGGER)

lint: install
	$(VENV)/bin/flake8 src/
	$(VENV)/bin/mypy src/ --disallow-untyped-defs

clean:
	rm -rf $(VENV)
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
