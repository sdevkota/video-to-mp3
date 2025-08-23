#!/bin/bash

# Complete Media Converter Suite - Docker Status Script
# Built by Nepal Media Group

echo "📊 Complete Media Converter Suite - Docker Status"
echo "================================================"
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

echo "🔍 Checking container status..."
echo ""

# Check running containers
if docker ps | grep -q "media-converter-suite"; then
    echo "✅ Container Status: RUNNING"
    echo "🌐 Application URL: http://localhost:8501"
    echo ""
    
    # Show container details
    echo "📋 Container Details:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep media-converter-suite
    
    echo ""
    echo "📊 Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | grep media-converter-suite
    
    echo ""
    echo "📝 Recent Logs (last 10 lines):"
    $COMPOSE_CMD logs --tail=10 media-converter-suite
    
    echo ""
    echo "💡 Management Commands:"
    echo "   View all logs:    $COMPOSE_CMD logs -f media-converter-suite"
    echo "   Stop app:         ./docker-stop.sh"
    echo "   Restart:          $COMPOSE_CMD restart media-converter-suite"
    
else
    echo "❌ Container Status: NOT RUNNING"
    echo ""
    
    # Check if there are stopped containers
    if docker ps -a | grep -q "media-converter-suite"; then
        echo "⚠️  Found stopped container:"
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep media-converter-suite
        
        echo ""
        echo "💡 To start the app, run: ./docker-run.sh"
    else
        echo "ℹ️  No containers found"
        echo ""
        echo "💡 To start the app, run: ./docker-run.sh"
    fi
fi

echo ""
echo "🔧 System Information:"
echo "   Docker Version: $(docker --version)"
echo "   Docker Compose: $($COMPOSE_CMD --version)"
echo "   Available Ports: $(netstat -tlnp 2>/dev/null | grep :8501 || echo 'Port 8501 not in use')" 