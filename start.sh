#!/bin/bash

uv run intensifyer &
INTENSIFYER_BOT_PID=$!

echo "> Intensifyer_bot started (pid: ${INTENSIFYER_BOT_PID})!"
uv run ./src/intensifyer/health_server.py $INTENSIFYER_BOT_PID
