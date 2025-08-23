#!/bin/bash

# Complete Media Converter Suite - Docker Stop Script
# Built by Nepal Media Group

echo "🛑 Complete Media Converter Suite - Docker Stop Script"
echo "======================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose not found."
    exit 1
fi

# Check if container is running
if docker ps | grep -q "media-converter-suite"; then
    echo "🔍 Found running container: media-converter-suite"
    echo "🛑 Stopping the application..."
    
    $COMPOSE_CMD down
    
    # Wait a moment and check if stopped
    sleep 3
    
    if docker ps | grep -q "media-converter-suite"; then
        echo "⚠️  Container still running. Force stopping..."
        docker stop media-converter-suite
        docker rm media-converter-suite
    fi
    
    echo "✅ Application stopped successfully!"
    echo "🌐 The app is no longer accessible at http://localhost:8501"
else
    echo "ℹ️  No running container found"
    
    # Check if there are stopped containers
    if docker ps -a | grep -q "media-converter-suite"; then
        echo "🧹 Found stopped container. Cleaning up..."
        docker rm media-converter-suite
        echo "✅ Cleanup completed"
    fi
fi

echo ""
echo "📋 Container status:"
docker ps -a | grep media-converter-suite || echo "No containers found"

echo ""
echo "💡 To start the app again, run: ./docker-run.sh" 