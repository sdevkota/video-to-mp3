# Configuration file for Media Converter Suite

APP_CONFIG = {
    "page_title": "Complete Media Converter Suite",
    "page_icon": "🎵",
    "max_file_size": 10 * 1024**3,  # 10GB in bytes
    "temp_dir_prefix": "media_converter_",
    "version": "1.0.0"
}

# Supported formats
SUPPORTED_FORMATS = {
    "audio_input": ["mp3", "wav", "flac", "m4a", "aac", "ogg", "wma", "mp4", "mov", "avi", "mkv", "webm"],
    "audio_output": ["mp3", "wav", "flac", "aac", "ogg"],
    "video_input": ["mp4", "mov", "avi", "mkv", "webm", "flv", "wmv", "m4v", "3gp"],
    "video_output": ["mp4", "avi", "mkv", "webm", "mov"]
}

# Quality presets
QUALITY_PRESETS = {
    "audio": {
        "low": "128k",
        "medium": "192k", 
        "high": "256k",
        "maximum": "320k"
    },
    "video": {
        "ultrafast": {"crf": "28", "preset": "ultrafast"},
        "fast": {"crf": "26", "preset": "fast"},
        "medium": {"crf": "23", "preset": "medium"},
        "slow": {"crf": "20", "preset": "slow"},
        "high": {"crf": "18", "preset": "slow"}
    },
    "compression": {
        "light": {"crf": "20", "preset": "slow"},
        "medium": {"crf": "25", "preset": "medium"},
        "heavy": {"crf": "30", "preset": "fast"},
        "maximum": {"crf": "35", "preset": "faster"}
    }
}

# MIME types for downloads
MIME_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav", 
    "flac": "audio/flac",
    "aac": "audio/aac",
    "ogg": "audio/ogg",
    "mp4": "video/mp4",
    "avi": "video/x-msvideo",
    "mkv": "video/x-matroska",
    "webm": "video/webm",
    "mov": "video/quicktime"
}

# FFmpeg command templates
FFMPEG_COMMANDS = {
    "audio_convert": {
        "mp3": ["-vn", "-acodec", "libmp3lame", "-ab", "{quality}", "-ar", "44100"],
        "wav": ["-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2"],
        "flac": ["-vn", "-acodec", "flac", "-compression_level", "5"],
        "aac": ["-vn", "-acodec", "aac", "-b:a", "{quality}"],
        "ogg": ["-vn", "-acodec", "libvorbis", "-q:a", "5"]
    },
    "video_convert": {
        "mp4": ["-c:v", "libx264", "-c:a", "aac"],
        "avi": ["-c:v", "libx264", "-c:a", "mp3"],
        "mkv": ["-c:v", "libx264", "-c:a", "aac"],
        "webm": ["-c:v", "libvpx-vp9", "-c:a", "libopus", "-crf", "30", "-b:v", "0"],
        "mov": ["-c:v", "libx264", "-c:a", "aac"]
    }
}

# YouTube-dl options
YT_DLP_OPTIONS = {
    "base": {
        'noplaylist': True,
        'extract_flat': False,
        'quiet': False,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    },
    "audio": {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    },
    "video": {
        'format': 'best[height<=720]/best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    }
}