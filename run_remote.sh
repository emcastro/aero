#!/bin/bash

if which mpremote.exe > /dev/null # for WSL without admin rights
then
    mpremote=mpremote.exe
else
    mpremote=mpremote
fi

echo Deploy libraries
$mpremote cp -r microzarr geolib.py microtyping.py logging.py :/sd/ 

echo Run
$mpremote run "$@"
