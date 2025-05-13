#!/bin/bash

# Start main.py in the background once
echo "[$(date)] Starting main.py"
python main.py &

# Periodically pull updates
while true; do
    echo "[$(date)] Running git pull"
    # Reset any local changes and pull
    git reset --hard
    git clean -fd
    git pull origin main
    if [ $? -eq 0 ]; then
        echo "[$(date)] Git pull successful"
    else
        echo "[$(date)] Git pull failed"
    fi
    echo "[$(date)] Sleeping for 300 seconds"
    sleep 60
done