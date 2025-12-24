#!/bin/bash

DIR="$(dirname "$(realpath "$0")")"
cd "$DIR"

if which mpremote.exe > /dev/null # for WSL without admin rights
then
    mpremote=mpremote.exe
else
    mpremote=mpremote
fi

echo Run clean_sdcard.py
$mpremote run clean_sdcard.py 
