# 🎵 Video to MP3 Converter

A simple, standalone video to MP3 converter with both CLI and web interface. Supports YouTube videos and direct MP4 file URLs.

## 🚀 Quick Start (Web UI)

### macOS/Linux
```bash
./run_app.sh
```

### Windows
```cmd
run_app.bat
```

Then open http://localhost:8501 in your browser.

## 📋 Manual Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg
**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**Windows:**
```cmd
winget install ffmpeg
```

## 💻 Usage

### Web Interface (Recommended)
```bash
streamlit run app.py
```

### Command Line
```bash
python main.py
```

## ✨ Features

- 🎵 High quality MP3 conversion (320kbps)
- 🖥️ Modern web interface
- 📱 Mobile-friendly design
- 🚀 Fast processing
- 🔒 Privacy-focused (runs locally)
- 📥 Direct browser downloads
- 👀 Video preview before download
- 🧹 No server storage (temporary processing only)
- 📹 YouTube & MP4 URL support

## 🏗️ Deployment

### Local Development
```bash
# Option 1: Direct run
./run_app.sh

# Option 2: Docker Compose
docker-compose up -d
```

### Cloud Deployment

#### Google Cloud Run (Recommended)
```bash
# Edit deploy.sh with your project ID
./deploy.sh
```

#### Streamlit Cloud (Easiest)
```bash
./deploy_streamlit.sh
# Then follow the instructions to push to GitHub
```

#### Other Options
- **Railway**: Simple Python app deployment
- **Heroku**: With ffmpeg buildpack
- **DigitalOcean**: App Platform

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📁 File Structure

```
youtube-to-mp3/
├── app.py              # Streamlit web interface
├── main.py             # Core download functions
├── requirements.txt    # Python dependencies
├── run_app.sh         # macOS/Linux launcher
├── run_app.bat        # Windows launcher
├── downloads/         # Output folder (auto-created)
└── README.md          # This file
```