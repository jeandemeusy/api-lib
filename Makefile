.PHONY: fmt
fmt:
	@uvx black .
	@uvx ruff check
	@uvx ty check

.PHONY: test
test:
	@uv run pytest --cov=src --cov-report html:.coveragehtml