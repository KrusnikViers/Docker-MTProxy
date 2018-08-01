#!/bin/sh

if [ -s "/configuration.json" ]
then
    python -u /src/entry.py
else
   echo "Configuration file is empty!"
fi
