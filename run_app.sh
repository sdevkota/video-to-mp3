#!/bin/bash

# Video to MP3 Converter Web App Launcher
echo "🎵 Starting Video to MP3 Converter..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found! Please install FFmpeg first:"
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
    echo "   CentOS: sudo yum install ffmpeg"
    exit 1
fi

# Create downloads directory
mkdir -p downloads

# Start the Streamlit app
echo "🚀 Starting web interface..."
echo "📱 Open http://localhost:8501 in your browser"
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
