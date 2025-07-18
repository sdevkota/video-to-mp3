# NMG Video to MP3 Converter

A simple Streamlit web application to convert YouTube videos and MP4 files to MP3 format.

## Features

- Convert YouTube videos to MP3
- Convert MP4 files to MP3
- Clean web interface
- Real-time conversion progress
- Direct download from browser
- High quality MP3 output (320kbps)

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 🐳 Docker (Recommended)

**Option 1: Use Docker run script**
```bash
# On Mac/Linux
./docker-run.sh

# On Windows
docker-run.bat
```

**Option 2: Manual Docker**
```bash
# Build and run with docker-compose
docker-compose up --build -d

# Or with Docker Compose plugin
docker compose up --build -d
```

### 🐍 Python Local Install

**Option 3: Use the Python run script**
```bash
# On Mac/Linux
./run.sh

# On Windows
run.bat
```

**Option 4: Manual Python setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Usage

1. Run the application using one of the methods above
2. Open your browser to the provided URL (usually http://localhost:8501)
3. Enter a YouTube URL or MP4 file URL
4. Click "Convert to MP3"
5. Wait for conversion to complete
6. Download your MP3 file

## Requirements

### Docker (Recommended)
- Docker Desktop
- Docker Compose

### Python Local Install
- Python 3.7 or higher
- ffmpeg (for audio conversion)
  - **Mac**: `brew install ffmpeg`
  - **Ubuntu/Debian**: `sudo apt install ffmpeg`
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Docker Commands

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Rebuild and start
docker-compose up --build -d
```

## Supported Formats

- **Input**: YouTube videos, MP4 files
- **Output**: MP3 (320kbps)

## Killl Docker Container
sudo kill -9 $(sudo docker inspect --format '{{.State.Pid}}' nmg-video-converter)

## Built By

Nepal Media Group
