#!/bin/bash

SCRIPT="$(realpath --relative-to=/home/ecastro/aero "$1")"
shift

# Build the Docker image if it doesn't exist
if ! docker image inspect macropython:latest >/dev/null 2>&1; then
    echo "Building Docker image macropython:latest..."
    docker build -t macropython:latest /home/ecastro/aero/macropython
    echo "Docker image built successfully. Remove it manually for rebuild"
fi

# Lance l'exécution sur un container temporaire micropython/unix en faisant en sorte que le réperoire du code sois /sd/
docker run --rm --interactive --tty \
    --volume /home/ecastro/aero/devdata:/sd \
    --volume /home/ecastro/aero:/flash \
    --publish 5678:5678 \
    --user "$(id -u "$USER"):$(id -g "$USER")" \
    --workdir /flash \
    --env PYTHONPATH=.:macropython \
    macropython:latest \
    python -Xfrozen_modules=off macropython/debug.py "$SCRIPT" "$@"
