#!/bin/bash

# BOM Comparison Tool Deployment Script
set -e

echo "🚀 Starting BOM Comparison Tool deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Stop existing containers if running
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Pull latest images and build
echo "🔨 Building containers..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Test connectivity
echo "🧪 Testing connectivity..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "⚠️  Backend health check failed, but continuing..."
fi

if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️  Frontend check failed, but continuing..."
fi

echo ""
echo "🎉 Deployment complete!"
echo "📊 BOM Comparison Tool is now available at: http://localhost"
echo ""
echo "🔧 Management commands:"
echo "  View logs:     docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart:       docker-compose restart"
echo ""
echo "📁 Data is persisted in Docker volumes"
echo "📝 Logs are available in ./logs/nginx/"