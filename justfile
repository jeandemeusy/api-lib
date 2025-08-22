#!/usr/bin/env just --justfile

default: list

fmt:
	@uvx black api_lib test
	@uvx ruff check api_lib test --fix --output-format=github
	@uvx ty check api_lib test

test:
	@uv run pytest --cov=api_lib --cov-report json --cov-report term --cov-report html
	@find . -name ".coverage*" -not -name ".coveragerc" -delete

specs:
	@uv run -m api_lib.from_specs -s .specs.json -n .generated.hoprd

list:
	@just --list