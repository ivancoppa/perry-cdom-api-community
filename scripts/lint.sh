#!/bin/bash
black .
isort .
ruff check
mypy .
