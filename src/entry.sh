#!/bin/sh

if [ -s "/configuration.json" ]
then
    service cron start
    python -u /src/entry.py
else
   echo "Configuration file is empty!"
fi
