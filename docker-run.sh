#!/bin/bash

# Complete Media Converter Suite - Docker Run Script
# Built by Nepal Media Group

echo "🐳 Complete Media Converter Suite - Docker Edition"
echo "=================================================="
echo ""

# Check if Docker is installed
echo "🔍 Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "✅ Docker found: $(docker --version)"
else
    echo "❌ Docker not found. Please install Docker Desktop."
    echo "   Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo ""

# Check if Docker Compose is available
echo "🔍 Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "✅ docker-compose found"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "✅ docker compose (plugin) found"
else
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo ""

# Create downloads directory
echo "📁 Creating downloads directory..."
mkdir -p downloads
echo "✅ Downloads directory ready: ./downloads"

echo ""

# Check if container is already running
echo "🔍 Checking for existing container..."
if docker ps | grep -q "media-converter-suite"; then
    echo "⚠️  Container is already running!"
    echo "🌐 Access the app at: http://localhost:8501"
    echo ""
    read -p "   Stop and restart? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 Stopping existing container..."
        $COMPOSE_CMD down
        sleep 3
    else
        echo "✅ Keeping existing container running"
        echo "🌐 Visit: http://localhost:8501"
        exit 0
    fi
fi

echo ""

# Build and run the container
echo "🏗️  Building and starting the application..."
echo "📦 This may take a few minutes on first run..."
echo ""

$COMPOSE_CMD up --build -d

# Check if container started successfully
echo ""
echo "🔍 Checking container status..."
sleep 5

if docker ps | grep -q "media-converter-suite"; then
    echo "✅ Container started successfully!"
    echo ""
    echo "🎉 Complete Media Converter Suite is now running!"
    echo "🌐 Open your browser and visit: http://localhost:8501"
    echo "📁 Downloads will be saved to: ./downloads"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:        $COMPOSE_CMD logs -f"
    echo "   Stop container:   $COMPOSE_CMD down"
    echo "   Restart:          $COMPOSE_CMD restart"
    echo "   Check status:     docker ps | grep media-converter-suite"
    echo ""
    echo "💡 The app is running as a background service"
    echo "   You can close this terminal and the app will continue running"
    echo ""
    echo "🚀 Available Tools:"
    echo "   - 🎥 YouTube Converter"
    echo "   - 🎵 Audio Converter"
    echo "   - 🎬 Video Converter"
    echo "   - 🛠️ Media Tools"
    echo "   - 🇳🇵 Advanced Nepali Unicode Converter"
    echo ""
else
    echo "❌ Container failed to start. Checking logs..."
    $COMPOSE_CMD logs
    exit 1
fi
