#!/bin/bash

# Stop Complete Media Converter Suite
# Built by Nepal Media Group

echo "🛑 Complete Media Converter Suite - Stop Script"
echo "==============================================="
echo ""

PID_FILE="streamlit.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ No PID file found. Application may not be running."
    exit 1
fi

PID=$(cat "$PID_FILE")

if [ -z "$PID" ]; then
    echo "❌ Invalid PID file. Removing it."
    rm -f "$PID_FILE"
    exit 1
fi

echo "🔍 Checking if application is running (PID: $PID)..."

if ps -p $PID > /dev/null 2>&1; then
    echo "✅ Application is running. Stopping it..."
    
    # Try graceful shutdown first
    kill $PID
    
    # Wait for graceful shutdown
    sleep 3
    
    # Check if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Graceful shutdown failed. Force stopping..."
        kill -9 $PID
        sleep 1
    fi
    
    # Final check
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Failed to stop application"
        exit 1
    else
        echo "✅ Application stopped successfully"
        rm -f "$PID_FILE"
        echo "🧹 PID file cleaned up"
    fi
else
    echo "⚠️  Application is not running (PID: $PID)"
    echo "🧹 Cleaning up stale PID file..."
    rm -f "$PID_FILE"
fi

echo ""
echo "👋 Application stopped. You can start it again with ./run.sh" 