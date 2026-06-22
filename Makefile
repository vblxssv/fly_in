.PHONY: run clean lint

MAP ?= test_map.txt
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: venv
	$(PYTHON) main.py $(MAP)

lint: venv
	$(VENV)/bin/flake8 src/
	$(VENV)/bin/mypy src/ --disallow-untyped-defs

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
