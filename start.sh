#!/bin/bash

./intensyfier_bot.py &
INTENSYFIER_BOT_PID=$!

echo "> Intensyfier_bot started (pid: ${INTENSYFIER_BOT_PID})!"
./health_server.py $INTENSYFIER_BOT_PID
