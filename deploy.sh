#!/bin/bash

# Copy everything but ./node_modules.
rsync -avr -e "ssh -p 1121" *.py requirements.txt models meneillosa:~/intensyfier
