install:
	poetry install --no-root

run:
	poetry run python -m src.main --host $(host) --user $(user)

test:
	poetry run pytest --cov=src --cov-report=term-missing

check: 
	@echo "\n=== Autofomatting (black) ====================" 
	poetry run black src/ tests/
	@echo "=================================================="
	@echo "\n\n=== Linting (ruff) ==========================="

	poetry run ruff check src/ --fix 
	@echo "=================================================="

	@echo "\n\n=== Type checking (mypy) ====================="
	PYTHONPATH=src poetry run mypy src/
	@echo "==================================================\n"

doc:
	poetry run mkdocs serve   


all: check test run