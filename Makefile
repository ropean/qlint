.PHONY: build lint format install

install:
	uv sync --extra dev

format:
	uv run ruff format qlint

lint:
	uv run ruff check qlint

build:
	uv run --with build python -m build

publish: build
	uv run --with twine twine upload dist/*
