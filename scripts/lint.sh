#!/bin/bash -e
echo "BLACK"
black .
echo "isort"
isort .
echo "ruff"
ruff check
echo "mypy"
mypy .
