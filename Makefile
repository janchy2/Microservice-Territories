SRC = application
TESTS = tests

all: clean format lint type-check test

format:
	@echo "Formatting code with black..."
	black $(SRC) $(TESTS)

lint:
	@echo "Running ruff..."
	ruff check $(SRC) $(TESTS)

type-check:
	@echo "Running mypy for type checking..."
	mypy $(SRC) $(TESTS)

clean:
	@echo "Cleaning cache..."
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type d -name '.pytest_cache' -exec rm -r {} +
	find . -type d -name '.mypy_cache' -exec rm -r {} +
	find . -type d -name '.ruff_cache' -exec rm -r {} +

test:
	@echo "Running tests..."
	pytest $(TESTS)
