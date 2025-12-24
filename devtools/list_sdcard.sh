#!/bin/bash

DIR="$(dirname "$(realpath "$0")")"
cd "$DIR"

if which mpremote.exe > /dev/null # for WSL without admin rights
then
    mpremote=mpremote.exe
else
    mpremote=mpremote
fi

# Create a temporary file
TEMP_FILE=$(mktemp)

# Copy the content of clean_sdcard.py to the temporary file and modify it to list files without deleting them
sed 's/delete=True/delete=False/g' clean_sdcard.py > $TEMP_FILE
# Run the temporary file
$mpremote run $TEMP_FILE

# Delete the temporary file after execution
rm $TEMP_FILE
