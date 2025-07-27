#!/bin/bash

# Lance l'exécution sur un container temporaire micropython/unix en faisant en sorte que le réperoire du code sois /sd/
docker run --rm -it \
    -v /home/ecastro/aero/devdata:/sd \
    -v /home/ecastro/aero:/flash \
    micropython/unix \
    /usr/local/bin/micropython /flash/zarr_test.py
