#!/bin/bash

# Complete Media Converter Suite - Run Script
# Built by Nepal Media Group

echo "🎵 Complete Media Converter Suite"
echo "================================="
echo ""

# Check if Python is installed
echo "🔍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Python found: $(python --version)"
else
    echo "❌ Python not found. Please install Python 3.8 or higher."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

echo ""

# Check if pip is available
echo "🔍 Checking pip installation..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    echo "✅ pip3 found"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
    echo "✅ pip found"
else
    echo "❌ pip not found. Please install pip."
    exit 1
fi

echo ""

# Check and install dependencies
echo "📦 Checking and installing dependencies..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo "📥 Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install all dependencies from requirements.txt
echo "📥 Installing all dependencies from requirements.txt..."
$PIP_CMD install -r requirements.txt

# Verify key dependencies
echo "🔍 Verifying key dependencies..."

# Check if yt-dlp is installed
if $PYTHON_CMD -c "import yt_dlp" 2>/dev/null; then
    echo "✅ yt-dlp is installed"
else
    echo "❌ yt-dlp installation failed"
    exit 1
fi

# Check if streamlit is installed
if $PYTHON_CMD -c "import streamlit" 2>/dev/null; then
    echo "✅ streamlit is installed"
else
    echo "❌ streamlit installation failed"
    exit 1
fi

# Check if googletrans is installed
if $PYTHON_CMD -c "import googletrans" 2>/dev/null; then
    echo "✅ googletrans is installed"
else
    echo "❌ googletrans installation failed"
    exit 1
fi

# Check if ffmpeg is available (needed for media conversion)
echo "🔍 Checking ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg found: $(ffmpeg -version | head -1)"
else
    echo "⚠️  ffmpeg not found - media conversion will not work properly"
    echo "   Install ffmpeg:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    read -p "   Continue anyway? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Test if the app can be imported
echo "🧪 Testing application imports..."
if $PYTHON_CMD -c "from main import main; print('✅ All modules imported successfully')" 2>/dev/null; then
    echo "✅ Application ready to run"
else
    echo "❌ Application import failed. Please check the error above."
    exit 1
fi

echo ""

# Check if app is already running
PID_FILE="streamlit.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Application is already running (PID: $PID)"
        echo "   Access it at: http://localhost:8501"
        echo ""
        read -p "   Stop existing instance and start new one? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🛑 Stopping existing instance..."
            kill $PID
            rm -f "$PID_FILE"
            sleep 2
        else
            echo "👋 Application is already running. Exiting."
            exit 0
        fi
    else
        echo "🧹 Cleaning up stale PID file..."
        rm -f "$PID_FILE"
    fi
fi

# Run the app in background
echo "🚀 Starting Complete Media Converter Suite in background..."
echo "📱 Your browser will open automatically"
echo "🌐 Access at: http://localhost:8501"
echo ""
echo "🎯 Available Tools:"
echo "   - 🎥 YouTube Converter"
echo "   - 🎵 Audio Converter"
echo "   - 🎬 Video Converter"
echo "   - 🛠️ Media Tools"
echo "   - 🇳🇵 English to Nepali"
echo ""

# Start Streamlit in background and save PID
nohup $PYTHON_CMD -m streamlit run main.py --server.port 8501 --server.headless true > streamlit.log 2>&1 &
STREAMLIT_PID=$!

# Save PID to file
echo $STREAMLIT_PID > "$PID_FILE"

# Wait a moment for the app to start
sleep 3

# Check if the app started successfully
if ps -p $STREAMLIT_PID > /dev/null 2>&1; then
    echo "✅ Application started successfully (PID: $STREAMLIT_PID)"
    echo "📝 Log file: streamlit.log"
    echo "🆔 PID file: $PID_FILE"
    echo ""
    echo "💡 Management commands:"
    echo "   - View logs: tail -f streamlit.log"
    echo "   - Stop app: kill $STREAMLIT_PID"
    echo "   - Check status: ps -p $STREAMLIT_PID"
    echo ""
    echo "🌐 Open your browser and go to: http://localhost:8501"
    echo ""
    echo "Press Enter to view logs, or Ctrl+C to exit (app will continue running)"
    read -p ""
    
    # Show logs if user pressed Enter
    if [ $? -eq 0 ]; then
        echo "📋 Showing recent logs (Ctrl+C to exit logs):"
        tail -f streamlit.log
    fi
else
    echo "❌ Failed to start application"
    echo "📝 Check streamlit.log for error details"
    rm -f "$PID_FILE"
    exit 1
fi
