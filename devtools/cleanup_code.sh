#!/bin/bash

uv sync
# shellcheck disable=SC1091
. .venv/bin/activate
echo black ===============
black .
echo isort ===============
isort .
echo pylint ==============
pylint .
echo pyright =============
pyright