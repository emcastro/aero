#!/bin/bash

uv sync
# shellcheck disable=SC1091
. .venv/bin/activate
rm -rf src/*.egg-info
rm -rf src/__pycache__

echo black ===============
black .
echo isort ===============
isort .
echo pylint ==============
pylint .
echo pyright =============
pyright