#!/bin/bash

if [ -s "/configuration.json" ]
then
    service cron start
    python /src/entry.py
else
   echo "Configuration file is empty!"
fi
