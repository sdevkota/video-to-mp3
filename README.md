# 🎵 Complete Media Converter Suite

A comprehensive web application for converting, downloading, and processing media files. Built with Streamlit and powered by FFmpeg.

## ✨ Features

### 🎥 YouTube Converter
- Download YouTube videos and convert to various formats
- Extract audio from YouTube videos (MP3, WAV, FLAC, AAC, OGG)
- Convert videos to different formats (MP4, AVI, MKV, WEBM, MOV)
- Quality presets and advanced options
- Time-based trimming and editing

### 🎵 Audio Converter
- Convert between audio formats (MP3, WAV, FLAC, AAC, OGG)
- Quality control and sample rate adjustment
- Audio normalization and fade effects
- Batch conversion for multiple files
- Support for video files with audio extraction

### 🎬 Video Converter
- Convert between video formats (MP4, AVI, MKV, WEBM, MOV)
- Quality presets and resolution control
- Frame rate adjustment and deinterlacing
- Advanced codec selection
- Batch processing capabilities

### 🛠️ Media Tools
- **Audio Extraction**: Extract audio from video files
- **Video Compression**: Reduce file size while maintaining quality
- **Media Analysis**: Detailed file information and codec analysis
- **Media Trimming**: Cut videos and audio to specific time ranges
- **Format Detection**: Identify file types and properties

## 🚀 Installation

### Prerequisites

1. **Python 3.8+** installed on your system
2. **FFmpeg** installed and available in your system PATH

### FFmpeg Installation

#### Windows
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the archive
3. Add the `bin` folder to your system PATH

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install ffmpeg
# or
sudo dnf install ffmpeg
```

### Application Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd video-to-mp3
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

## 🎯 Usage

### Starting the App

1. Navigate to the project directory
2. Activate your virtual environment
3. Run `streamlit run main.py`
4. Open your browser to the displayed URL (usually `http://localhost:8501`)

### Using the YouTube Converter

1. Select "🎥 YouTube Converter" from the sidebar
2. Paste a YouTube URL
3. Choose conversion type (Audio/Video/Both)
4. Select output format and quality
5. Click "Download & Convert"
6. Download your converted file

### Using the Audio Converter

1. Select "🎵 Audio Converter" from the sidebar
2. Upload an audio or video file
3. Choose output format and quality settings
4. Adjust advanced options if needed
5. Click "Convert Audio"
6. Download your converted file

### Using the Video Converter

1. Select "🎬 Video Converter" from the sidebar
2. Upload a video file
3. Choose output format and quality
4. Adjust resolution and frame rate
5. Click "Convert Video"
6. Download your converted file

### Using Media Tools

1. Select "🛠️ Media Tools" from the sidebar
2. Choose the specific tool you need
3. Upload your media file
4. Configure tool-specific options
5. Process your file
6. Download the result

## 🔧 Configuration

### Supported Formats

#### Input Formats
- **Audio**: MP3, WAV, FLAC, M4A, AAC, OGG, WMA
- **Video**: MP4, MOV, AVI, MKV, WEBM, FLV, WMV, M4V, 3GP
- **YouTube**: Any publicly accessible YouTube video

#### Output Formats
- **Audio**: MP3, WAV, FLAC, AAC, OGG
- **Video**: MP4, AVI, MKV, WEBM, MOV

### Quality Presets

#### Audio Quality
- **Low (128k)**: Small file size, basic quality
- **Medium (192k)**: Balanced size and quality
- **High (256k)**: Good quality, larger file
- **Maximum (320k)**: Best quality, largest file

#### Video Quality
- **Ultrafast**: Fastest conversion, lower quality
- **Fast**: Quick conversion, good quality
- **Medium**: Balanced speed and quality
- **Slow**: Slower conversion, better quality
- **High**: Best quality, slowest conversion

## 📁 Project Structure

```
video-to-mp3/
├── main.py                 # Main application entry point
├── config.py              # Configuration and constants
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── pages/                # Application pages
│   ├── __init__.py
│   ├── youtube_converter.py
│   ├── audio_converter.py
│   ├── video_converter.py
│   └── media_tools.py
├── utils/                # Utility modules
│   ├── file_utils.py     # File handling utilities
│   ├── ffmped_utils.py   # FFmpeg operations
│   └── youtube_utils.py  # YouTube download utilities
├── downloads/            # Output directory for converted files
├── run.sh               # Linux/macOS run script
├── run.bat              # Windows run script
├── docker-run.sh        # Docker run script
├── docker-run.bat       # Docker run script
├── Dockerfile           # Docker configuration
└── docker-compose.yml   # Docker Compose configuration
```

## 🐳 Docker Support

### Using Docker Compose (Recommended)

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

### Using Docker directly

```bash
# Build image
docker build -t media-converter .

# Run container
docker run -p 8501:8501 media-converter
```

## 🔒 Security & Legal

### Important Notes

- **YouTube Downloads**: Only download content you own or have permission to download
- **Copyright**: Respect copyright laws and YouTube's Terms of Service
- **File Handling**: Files are processed locally and not uploaded to external servers
- **Temporary Storage**: Temporary files are automatically cleaned up after processing

### Privacy

- No user data is collected or stored
- All processing happens locally on your machine
- No files are sent to external services (except YouTube for downloads)

## 🐛 Troubleshooting

### Common Issues

#### FFmpeg Not Found
- Ensure FFmpeg is installed and in your system PATH
- Restart your terminal/command prompt after installation
- Verify installation with `ffmpeg -version`

#### YouTube Download Errors
- Check if the video is publicly accessible
- Verify your internet connection
- Some videos may have download restrictions

#### Conversion Failures
- Ensure input file is not corrupted
- Check if input format is supported
- Verify sufficient disk space for output

#### Performance Issues
- Use lower quality presets for faster conversion
- Close other applications to free up system resources
- Consider using batch processing for multiple files

### Getting Help

1. Check the error messages displayed in the app
2. Verify FFmpeg installation and PATH configuration
3. Check file format compatibility
4. Ensure sufficient disk space and permissions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FFmpeg**: For powerful media processing capabilities
- **yt-dlp**: For YouTube download functionality
- **Streamlit**: For the web application framework
- **Python Community**: For excellent libraries and tools

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed information
4. Include error messages and system information

---

**Happy Converting! 🎵✨**
