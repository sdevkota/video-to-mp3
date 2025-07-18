#!/bin/bash

# NMG Video to MP3 Converter - Run Script
# Built by Nepal Media Group

echo "🎵 NMG Video to MP3 Converter"
echo "=============================="
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
    echo "❌ Python not found. Please install Python 3.7 or higher."
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
echo "📦 Checking dependencies..."

# Check if yt-dlp is installed
if $PYTHON_CMD -c "import yt_dlp" 2>/dev/null; then
    echo "✅ yt-dlp is installed"
else
    echo "📥 Installing yt-dlp..."
    $PIP_CMD install yt-dlp
fi

# Check if streamlit is installed
if $PYTHON_CMD -c "import streamlit" 2>/dev/null; then
    echo "✅ streamlit is installed"
else
    echo "📥 Installing streamlit..."
    $PIP_CMD install streamlit
fi

echo ""

# Check if ffmpeg is available (needed for audio conversion)
echo "🔍 Checking ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg found"
else
    echo "⚠️  ffmpeg not found - audio conversion may not work properly"
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

# Run the app
echo "🚀 Starting NMG Video to MP3 Converter..."
echo "📱 Your browser will open automatically"
echo "🌐 If not, visit: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run streamlit
$PYTHON_CMD -m streamlit run app.py

echo ""
echo "👋 Thank you for using NMG Video to MP3 Converter!"
