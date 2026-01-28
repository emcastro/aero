#!/bin/bash

set -e

DIR="$(dirname "$(realpath "$0")")"

SCRIPT="$(realpath --relative-to="$DIR" "$1")"
shift

if which mpremote.exe > /dev/null # for WSL without admin rights
then
    mpremote=mpremote.exe
else
    mpremote=mpremote
fi

echo Deploy libraries from src
(   
    # Note: we should first make a package (without macropython) and deploy it
    # For now, we do it simple
    cd src
    find . -name '__pycache__' -exec rm -r {} + # delete residual __pycache__
    $mpremote cp -r . :/sd
)

echo Run
$mpremote run "$SCRIPT" "$@" | sed -e s:'File "':"File \"$DIR/src/": -e s:'src/<stdin>':"$SCRIPT":


echo Retreive produced files

# Move any file that is not source back to experiments
# asking mpremote to compute le file list
$mpremote exec "
import os
import sys

# files in the sources
sources = set('''
$(cd src; find . -mindepth 1 -maxdepth 1 -printf "%P\n")
'''.strip().split('\n'))

# files in the remote
locals = set(os.listdir('/sd')) - {'dem.zarr'}

for file in locals - sources:
    print(file, end='\0')
" | xargs -0 -I {} $mpremote cp ":/sd/{}" ./experiments/
# copying files back with mpremote

