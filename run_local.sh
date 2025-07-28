#!/bin/bash

DIR="$(dirname "$(realpath "$0")")"

SCRIPT="$(realpath --relative-to="$DIR/src" "$1")"
shift

# Launches execution in a temporary micropython/unix container
# data directory mounted on /sd/
# code directory mounted on /flash/
docker run --rm -it \
    -v "$DIR/devdata:/sd" \
    -v "$DIR/src:/flash" \
    -w /flash \
    micropython/unix \
    /usr/local/bin/micropython "$SCRIPT" "$@" | sed s:/flash:"$DIR/src":
