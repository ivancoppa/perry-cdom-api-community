#!/bin/bash
black .
mypy .
ruff check
black --diff .
isort .
