#!/bin/bash

# Copy everything but ./node_modules.
rsync -avr -e "ssh -p 1121" intensyfier_bot.py requirements.txt meneillosa:~/intensyfier
