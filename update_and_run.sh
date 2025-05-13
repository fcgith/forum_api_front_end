#!/bin/bash

while true; do
    echo "[$(date)] Running git pull"
    git pull origin main
    if [ $? -eq 0 ]; then
        echo "[$(date)] Git pull successful"
        # Kill any existing main.py process
        pkill -f "python main.py"
        # Start main.py in the background
        python main.py &
    else
        echo "[$(date)] Git pull failed"
    fi
    echo "[$(date)] Sleeping for 300 seconds"
    sleep 300
done