#!/bin/bash

DIR="$(dirname "$(realpath "$0")")"

SCRIPT="$(realpath --relative-to="$DIR" "$1")"
shift

if which mpremote.exe > /dev/null # for WSL without admin rights
then
    mpremote=mpremote.exe
else
    mpremote=mpremote
fi

echo Deploy libraries
# shellcheck disable=SC2046
$mpremote cp -r $(find src -mindepth 1 -maxdepth 1 ! -path 'src/macropython' ! -name '__pycache__') :/sd/

echo Run
$mpremote run "$SCRIPT" "$@" | sed -e s:'File "':"File \"$DIR/src/": -e s:'src/<stdin>':"$SCRIPT":
