#!/bin/bash
# Navigate to the script's directory
cd "$(dirname "$0")" || exit

# Pull latest code from GitHub
git reset --hard
git pull origin master

# Rebuild Docker containers
docker-compose up -d --build

# Optional: prune unused Docker images
docker image prune -f

echo "Deployment finished!"
