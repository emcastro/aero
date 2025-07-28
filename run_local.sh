#!/bin/bash

SCRIPT="$(realpath --relative-to=/home/ecastro/aero "$1")"
shift

# Launches execution in a temporary micropython/unix container
# data directory mounted on /sd/
# code directory mounted on /flash/
docker run --rm -it \
    -v /home/ecastro/aero/devdata:/sd \
    -v /home/ecastro/aero:/flash \
    -w /flash \
    micropython/unix \
    /usr/local/bin/micropython "$SCRIPT" "$@"
