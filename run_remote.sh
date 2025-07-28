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
$mpremote cp -r $(find src -mindepth 1 -maxdepth 1 ! -path 'src/macropython') :/sd/

echo Run
$mpremote run "$SCRIPT" "$@" | sed s:/sd:"$DIR/src":
