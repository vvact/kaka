#!/bin/bash
# Navigate to project directory
cd /kaka || exit

# Pull latest code from GitHub
git reset --hard
git pull origin master

# Rebuild Docker containers
docker-compose up -d --build

# Optional: prune unused Docker images
docker image prune -f

echo "Deployment finished!"
