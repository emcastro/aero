#!/bin/bash

DIR="$(dirname "$(realpath "$0")")"

SCRIPT="$(realpath --relative-to="$DIR/src" "$1")"
shift

# Note current date for use when moving files produced by execution
CURRENT_DATE=$(date +%Y-%m-%d)

# Launches execution in a temporary micropython/unix container
# data directory mounted on /sd/
# code directory mounted on /flash/
docker run --rm  --interactive --tty \
    --volume "$DIR/devdata:/sd" \
    --volume "$DIR/src:/flash" \
    --user "$(id -u "$USER"):$(id -g "$USER")" \
    --workdir /flash \
    micropython/unix \
    /usr/local/bin/micropython -X heapsize=103936 "$SCRIPT" "$@" | sed s:/flash:"$DIR/src":

# Find files newer than "$CURRENT_DATE" in "$DIR/src" and move them to "experiments"
find "$DIR/src" -type f -newermt "$CURRENT_DATE" -exec mv {} "$DIR/experiments" \;
