#!/bin/bash

set -e

DIR="$(dirname "$(realpath "$0")")"

SCRIPT="$(realpath --relative-to="$DIR/src" "$1")"
shift

# Build the Docker image if it doesn't exist
if ! docker image inspect macropython:latest >/dev/null 2>&1; then
    echo "Building Docker image macropython:latest..."
    docker build -t macropython:latest /home/ecastro/aero/macropython
    echo "Docker image built successfully. Remove it manually for rebuild"
fi

# Note current date for use when moving files produced by execution
CURRENT_DATE=$(date +%Y-%m-%d %H:%M:%S)

# Lance l'exécution sur un container temporaire micropython/unix en faisant en sorte que le réperoire du code sois /sd/
# -B: no __pycache__
#  -Xfrozen_modules=off: enhance debug capabilities
docker run --rm --interactive --tty \
    --volume /home/ecastro/aero/devdata:/sd \
    --volume /home/ecastro/aero/src:/flash \
    --publish 5678:5678 \
    --user "$(id -u "$USER"):$(id -g "$USER")" \
    --workdir /flash \
    --env PYTHONPATH=.:macropython \
    macropython:latest \
    python -B -Xfrozen_modules=off macropython/debug.py "$SCRIPT" "$@" | sed s:/flash:"$DIR/src":

# Find files newer than "$CURRENT_DATE" in "$DIR/src" and move them to "experiments"
find "$DIR/src" -type f -newermt "$CURRENT_DATE" -exec mv {} "$DIR/experiments" \;
