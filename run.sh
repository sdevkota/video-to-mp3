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

# Run the app
echo "🚀 Starting Complete Media Converter Suite..."
echo "📱 Your browser will open automatically"
echo "🌐 If not, visit: http://localhost:8501"
echo ""
echo "🎯 Available Tools:"
echo "   - 🎥 YouTube Converter"
echo "   - 🎵 Audio Converter"
echo "   - 🎬 Video Converter"
echo "   - 🛠️ Media Tools"
echo "   - 🇳🇵 English to Nepali"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run streamlit
$PYTHON_CMD -m streamlit run main.py

echo ""
echo "👋 Thank you for using Complete Media Converter Suite!"
