import streamlit as st
import yt_dlp
import os
import tempfile
import time
import re
from pathlib import Path
import subprocess
import sys

# Configure Streamlit for large files (must be at the top)
try:
    st.set_page_config(
        page_title="Complete Media Converter",
        page_icon="🎵",
        layout="wide"
    )
except:
    pass  # Page config already set

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', ' ', filename)
    return filename.strip()

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_file_info(file_path):
    """Get basic file information using FFprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
            '-show_streams', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        info = json.loads(result.stdout)
        
        # Extract duration and format info
        duration = float(info.get('format', {}).get('duration', 0))
        format_name = info.get('format', {}).get('format_name', 'unknown')
        
        # Find audio/video streams
        streams = info.get('streams', [])
        has_video = any(stream.get('codec_type') == 'video' for stream in streams)
        has_audio = any(stream.get('codec_type') == 'audio' for stream in streams)
        
        # Get video info if available
        video_info = {}
        audio_info = {}
        
        for stream in streams:
            if stream.get('codec_type') == 'video' and not video_info:
                video_info = {
                    'codec': stream.get('codec_name', 'unknown'),
                    'width': stream.get('width', 0),
                    'height': stream.get('height', 0),
                    'fps': stream.get('r_frame_rate', '0/0')
                }
            elif stream.get('codec_type') == 'audio' and not audio_info:
                audio_info = {
                    'codec': stream.get('codec_name', 'unknown'),
                    'sample_rate': stream.get('sample_rate', 0),
                    'channels': stream.get('channels', 0)
                }
        
        return {
            'duration': duration,
            'format': format_name,
            'has_video': has_video,
            'has_audio': has_audio,
            'video_info': video_info,
            'audio_info': audio_info
        }
    except Exception as e:
        return None

def convert_audio_file(input_path, output_path, output_format, quality="192k"):
    """Convert audio file using FFmpeg"""
    try:
        if output_format.lower() == 'mp3':
            cmd = [
                'ffmpeg', '-i', input_path, '-vn', '-acodec', 'libmp3lame',
                '-ab', quality, '-ar', '44100', '-y', output_path
            ]
        elif output_format.lower() == 'wav':
            cmd = [
                'ffmpeg', '-i', input_path, '-vn', '-acodec', 'pcm_s16le',
                '-ar', '44100', '-ac', '2', '-y', output_path
            ]
        elif output_format.lower() == 'flac':
            cmd = [
                'ffmpeg', '-i', input_path, '-vn', '-acodec', 'flac',
                '-compression_level', '5', '-y', output_path
            ]
        elif output_format.lower() == 'aac':
            cmd = [
                'ffmpeg', '-i', input_path, '-vn', '-acodec', 'aac',
                '-b:a', quality, '-y', output_path
            ]
        elif output_format.lower() == 'ogg':
            cmd = [
                'ffmpeg', '-i', input_path, '-vn', '-acodec', 'libvorbis',
                '-q:a', '5', '-y', output_path
            ]
        else:
            return False, "Unsupported audio output format"
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True, "Audio conversion successful"
        else:
            return False, f"FFmpeg error: {result.stderr}"
            
    except Exception as e:
        return False, f"Audio conversion error: {str(e)}"

def convert_video_file(input_path, output_path, output_format, quality="medium"):
    """Convert video file using FFmpeg"""
    try:
        # Quality presets
        quality_settings = {
            "high": ["-crf", "18", "-preset", "slow"],
            "medium": ["-crf", "23", "-preset", "medium"],
            "low": ["-crf", "28", "-preset", "fast"],
            "ultrafast": ["-crf", "28", "-preset", "ultrafast"]
        }
        
        quality_params = quality_settings.get(quality, quality_settings["medium"])
        
        if output_format.lower() == 'mp4':
            cmd = [
                'ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'aac'
            ] + quality_params + ['-y', output_path]
        elif output_format.lower() == 'avi':
            cmd = [
                'ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'mp3'
            ] + quality_params + ['-y', output_path]
        elif output_format.lower() == 'mkv':
            cmd = [
                'ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'aac'
            ] + quality_params + ['-y', output_path]
        elif output_format.lower() == 'webm':
            cmd = [
                'ffmpeg', '-i', input_path, '-c:v', 'libvpx-vp9', '-c:a', 'libopus',
                '-crf', '30', '-b:v', '0', '-y', output_path
            ]
        elif output_format.lower() == 'mov':
            cmd = [
                'ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'aac'
            ] + quality_params + ['-y', output_path]
        else:
            return False, "Unsupported video output format"
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True, "Video conversion successful"
        else:
            return False, f"FFmpeg error: {result.stderr}"
            
    except Exception as e:
        return False, f"Video conversion error: {str(e)}"

def download_video_as_mp3(url, output_dir, cookies_file=None):
    """Download video as MP3"""
    
    if not check_ffmpeg():
        return {
            'success': False,
            'error': "❌ FFmpeg not found. FFmpeg is required for audio conversion."
        }
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
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
        }
        
        if cookies_file and os.path.exists(cookies_file):
            ydl_opts['cookiefile'] = cookies_file
        
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                error_msg = str(e).lower()
                if 'sign in' in error_msg or 'bot' in error_msg:
                    return {
                        'success': False,
                        'error': "⚠️ YouTube detected automated access. Try using cookies or waiting 10-15 minutes."
                    }
                elif 'unavailable' in error_msg or 'private' in error_msg:
                    return {
                        'success': False,
                        'error': "❌ Video is unavailable, private, or geo-blocked."
                    }
                else:
                    return {
                        'success': False,
                        'error': f"❌ Could not access video: {str(e)}"
                    }
            
            if not info:
                return {
                    'success': False,
                    'error': "❌ Could not extract video information."
                }
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            safe_title = sanitize_filename(title)
            if len(safe_title) > 100:
                safe_title = safe_title[:100] + "..."
            
            ydl_opts['outtmpl'] = os.path.join(output_dir, f'{safe_title}.%(ext)s')
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
                mp3_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
                
                if not mp3_files:
                    return {
                        'success': False,
                        'error': "❌ MP3 file was not created. Audio conversion may have failed."
                    }
                
                mp3_file = os.path.join(output_dir, mp3_files[0])
                
                if not os.path.exists(mp3_file) or os.path.getsize(mp3_file) == 0:
                    return {
                        'success': False,
                        'error': "❌ MP3 file is empty or corrupted."
                    }
                
                return {
                    'success': True,
                    'title': title,
                    'duration': duration,
                    'file_path': mp3_file,
                    'filename': mp3_files[0]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"❌ Conversion Error: {str(e)}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"❌ Unexpected Error: {str(e)}"
        }

def format_duration(seconds):
    """Format duration from seconds to MM:SS"""
    if not seconds:
        return "Unknown"
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"

def format_file_size(size_bytes):
    """Format file size in appropriate unit"""
    if size_bytes > 1024**3:  # > 1GB
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes > 1024**2:  # > 1MB
        return f"{size_bytes / (1024**2):.2f} MB"
    else:
        return f"{size_bytes // 1024} KB"

def youtube_to_mp3_tab():
    """YouTube to MP3 conversion tab"""
    st.header("🎥 YouTube to MP3")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input(
            "🔗 Enter YouTube URL:",
            placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            help="Paste a YouTube video URL here",
            key="youtube_url"
        )
        
        with st.expander("🍪 Advanced: Upload Cookies File (Optional)", expanded=False):
            st.markdown("""
            **For age-restricted or bot-detected videos:**
            - Export cookies from your browser using an extension like "Get cookies.txt"
            - Upload the cookies.txt file here
            """)
            
            cookies_file = st.file_uploader(
                "Upload cookies.txt file",
                type=['txt'],
                help="Optional: Upload browser cookies to access restricted content",
                key="youtube_cookies"
            )
        
        if st.button("🎵 Convert to MP3", type="primary", use_container_width=True, key="youtube_convert"):
            if not url or not url.strip():
                st.error("❌ Please enter a valid YouTube URL")
                return
            
            if not any(domain in url.lower() for domain in ['youtube.com', 'youtu.be']):
                st