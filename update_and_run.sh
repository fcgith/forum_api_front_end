#!/bin/bash

while true; do
    echo "[$(date)] Running git pull"
    # Reset any local changes and pull
    git reset --hard
    git clean -fd
    git pull origin main
    if [ $? -eq 0 ]; then
        echo "[$(date)] Git pull successful"
        # Kill any existing main.py process
        pkill -f "python main.py" || true
        # Wait briefly to ensure port is released
        sleep 2
        # Start main.py in the background
        python main.py &
    else
        echo "[$(date)] Git pull failed"
    fi
    echo "[$(date)] Sleeping for 300 seconds"
    sleep 60
done