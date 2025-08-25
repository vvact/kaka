#!/bin/bash
cd "$(dirname "$0")" || exit

# Pull latest code
git reset --hard
git pull origin master

# Step 1: Start nginx-proxy alone
docker-compose up -d nginx-proxy
echo "Waiting 5-10 seconds for nginx-proxy to initialize..."
sleep 10

# Step 2: Start the rest of the containers
docker-compose up -d --build api celery_worker flower redis postgres-db

# Optional: prune unused Docker images
docker image prune -f

echo "Deployment finished!"
