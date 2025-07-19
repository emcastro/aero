#!/bin/bash

if which mpremote.exe > /dev/null # for WSL without admin rights
then
    mpremote=mpremote.exe
else
    mpremote=mpremote
fi

echo Deploy
$mpremote cp -r  microzarr geolib.py macropython.py microtyping.py :/sd/ 

echo Run
$mpremote run "$@"
