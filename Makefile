.PHONY: fmt
fmt:
	@uvx black .
	@uvx ruff check --output-format=github
	@uvx ty check

.PHONY: test
test:
	@uv run pytest --cov=src --cov-report json