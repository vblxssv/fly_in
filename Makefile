.PHONY: run clean

# MAP = "maps/easy/01_linear_path.txt"
MAP = "test_map.txt"

run:
	python3 main.py $(MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

lint:
	flake8 src/
	mypy -p src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

