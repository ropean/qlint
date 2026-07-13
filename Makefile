.PHONY: build lint format install

install:
	pip install -e ".[dev]"

format:
	ruff format qlint

lint:
	ruff check qlint

build:
	python -m build

publish: build
	twine upload dist/*
