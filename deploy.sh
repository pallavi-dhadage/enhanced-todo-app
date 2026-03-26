#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Pull latest code
echo "📦 Pulling latest code..."
git pull origin main

# Build and start containers
echo "🐳 Building Docker images..."
docker compose -f docker-compose.prod.yml build

echo "🔄 Restarting services..."
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# Run database migrations
echo "🗄️ Running database migrations..."
docker compose -f docker-compose.prod.yml exec web python scripts/migrate.py

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✅ Deployment complete!"
echo "🌐 App is running at: http://localhost"
