# 🚀 Quick Start Guide

Get your Complete Media Converter Suite up and running in minutes!

## ⚡ Prerequisites Check

Before starting, ensure you have:

- ✅ **Python 3.8+** installed
- ✅ **FFmpeg** installed and in PATH
- ✅ **Git** (for cloning)

## 🎯 Quick Setup

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd video-to-mp3
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run main.py
```

### 4. Open Browser
Navigate to `http://localhost:8501`

## 🎵 What You Can Do

### YouTube Converter
- Download YouTube videos → MP3, WAV, FLAC, AAC, OGG
- Convert YouTube videos → MP4, AVI, MKV, WEBM, MOV
- Trim videos with start/end times

### Audio Converter
- Convert between audio formats
- Batch process multiple files
- Audio normalization and effects

### Video Converter
- Convert between video formats
- Quality presets and resolution control
- Advanced codec options

### Media Tools
- Extract audio from videos
- Compress video files
- Analyze media properties
- Format detection

## 🔧 Troubleshooting

### FFmpeg Not Found?
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Import Errors?
```bash
pip install --upgrade -r requirements.txt
```

### Port Already in Use?
```bash
streamlit run main.py --server.port 8502
```

## 📱 Usage Examples

### Convert YouTube to MP3
1. Select "🎥 YouTube Converter"
2. Paste YouTube URL
3. Choose "Audio Only" + "MP3"
4. Click "Download & Convert"

### Convert Audio File
1. Select "🎵 Audio Converter"
2. Upload audio file
3. Choose output format
4. Click "Convert Audio"

### Compress Video
1. Select "🛠️ Media Tools"
2. Choose "📹 Video Compression"
3. Upload video file
4. Set compression level
5. Click "Compress Video"

## 🎉 You're Ready!

Your Complete Media Converter Suite is now running! 

- **Need help?** Check the main README.md
- **Found a bug?** Create an issue
- **Want to contribute?** Submit a pull request

Happy converting! 🎵✨ 