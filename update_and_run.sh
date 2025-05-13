#!/bin/bash

while true; do
    # Pull the latest changes from Git
    git pull origin main

    # Run Uvicorn with reload (for development)
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload

    # Wait before checking for updates again (e.g., 5 minutes)
    sleep 60
done