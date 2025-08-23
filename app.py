import streamlit as st
import yt_dlp
import os
import tempfile
import time
import re
from pathlib import Path
import subprocess
import sys
import json

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

def extract_audio_from_video(input_path, output_path, output_format="mp3", quality="192k"):
    """Extract audio from video file"""
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
        else:
            return False, "Unsupported audio output format"
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True, "Audio extraction successful"
        else:
            return False, f"FFmpeg error: {result.stderr}"
            
    except Exception as e:
        return False, f"Audio extraction error: {str(e)}"

def compress_video(input_path, output_path, compression_level="medium"):
    """Compress video file to reduce size"""
    try:
        # Compression presets
        compression_settings = {
            "light": ["-crf", "20", "-preset", "slow"],
            "medium": ["-crf", "25", "-preset", "medium"],
            "heavy": ["-crf", "30", "-preset", "fast"],
            "maximum": ["-crf", "35", "-preset", "faster"]
        }
        
        params = compression_settings.get(compression_level, compression_settings["medium"])
        
        cmd = [
            'ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'aac'
        ] + params + ['-y', output_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True, "Video compression successful"
        else:
            return False, f"FFmpeg error: {result.stderr}"
            
    except Exception as e:
        return False, f"Video compression error: {str(e)}"

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
                st.warning("⚠️ This doesn't look like a YouTube URL.")
            
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            with status_placeholder:
                st.info("🔄 Starting conversion...")
            
            with progress_placeholder:
                progress_bar = st.progress(0)
            
            try:
                cookies_path = None
                if cookies_file is not None:
                    temp_cookies_dir = tempfile.mkdtemp()
                    cookies_path = os.path.join(temp_cookies_dir, "cookies.txt")
                    with open(cookies_path, "wb") as f:
                        f.write(cookies_file.getvalue())
                
                progress_bar.progress(20)
                status_placeholder.info("📋 Extracting video information...")
                
                temp_dir = tempfile.mkdtemp()
                
                progress_bar.progress(40)
                status_placeholder.info("⬇️ Downloading audio...")
                
                result = download_video_as_mp3(url, temp_dir, cookies_path)
                
                progress_bar.progress(80)
                status_placeholder.info("🎵 Converting to MP3...")
                progress_bar.progress(100)
                
                if result['success']:
                    status_placeholder.success("✅ Conversion completed successfully!")
                    st.balloons()
                    
                    st.success(f"**Title:** {result['title']}")
                    if result.get('duration'):
                        st.info(f"**Duration:** {format_duration(result['duration'])}")
                    
                    if result['file_path'] and os.path.exists(result['file_path']):
                        with open(result['file_path'], 'rb') as file:
                            file_data = file.read()
                        
                        file_size = format_file_size(len(file_data))
                        st.write(f"**File size:** {file_size}")
                        
                        st.download_button(
                            label="📥 Download MP3 File",
                            data=file_data,
                            file_name=result['filename'],
                            mime="audio/mpeg",
                            use_container_width=True
                        )
                else:
                    status_placeholder.error(result['error'])
                    
            except Exception as e:
                status_placeholder.error(f"❌ Unexpected error: {str(e)}")
            
            finally:
                time.sleep(2)
                progress_placeholder.empty()
    
    with col2:
        st.markdown("### 📖 Instructions:")
        st.markdown("""
        1. Copy a YouTube URL
        2. Paste it in the input field  
        3. Click Convert to MP3
        4. Wait for processing
        5. Download your MP3 file
        """)
        
        st.markdown("### ⚠️ Common Issues:")
        st.markdown("""
        **Bot detection:** Upload cookies
        **Video unavailable:** Check if public
        **Age-restricted:** Requires cookies
        """)

def audio_converter_tab():
    """Audio conversion tab for various audio formats"""
    st.header("🎵 Audio Converter")
    
    # Audio format options
    audio_formats = {
        "Input Formats": ["mp3", "wav", "flac", "m4a", "aac", "ogg", "wma", "mp4", "mov", "avi", "mkv"],
        "Output Formats": ["mp3", "wav", "flac", "aac", "ogg"]
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Output format selection
        output_format = st.selectbox(
            "🎯 Convert TO:",
            audio_formats["Output Formats"],
            index=0,  # Default to MP3
            key="audio_output_format"
        )
        
        # Quality settings for MP3 and AAC
        if output_format in ["mp3", "aac"]:
            quality = st.selectbox(
                "🎚️ Audio Quality:",
                ["128k", "192k", "256k", "320k"],
                index=1,  # Default to 192k
                key="audio_quality"
            )
        else:
            quality = "192k"  # Default for other formats
        
        # File upload with large file support
        uploaded_file = st.file_uploader(
            f"📁 Upload Audio/Video file (up to 10GB):",
            type=audio_formats["Input Formats"],
            help=f"Select an audio or video file to convert to {output_format.upper()}. Maximum file size: 10GB",
            key="audio_upload"
        )
        
        if uploaded_file is not None:
            # Show file info with GB support
            file_size_bytes = len(uploaded_file.getvalue())
            file_size = format_file_size(file_size_bytes)
            
            st.info(f"**File:** {uploaded_file.name} ({file_size})")
            
            # Show upload progress for large files
            if file_size_bytes > 100 * 1024**2:  # > 100MB
                st.info("📤 Large file detected. Processing may take longer...")
            
            if st.button(f"🎵 Convert to {output_format.upper()}", type="primary", use_container_width=True, key="audio_convert"):
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                with status_placeholder:
                    st.info("🔄 Starting audio conversion...")
                
                with progress_placeholder:
                    progress_bar = st.progress(0)
                
                try:
                    # Create temp directory
                    temp_dir = tempfile.mkdtemp()
                    
                    # Save uploaded file
                    input_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    progress_bar.progress(20)
                    status_placeholder.info("📋 Analyzing video...")
                    
                    # Get file info
                    file_info = get_file_info(input_path)
                    if file_info:
                        st.write(f"**Duration:** {format_duration(file_info['duration'])}")
                        st.write(f"**Format:** {file_info['format']}")
                        
                        if file_info['video_info']:
                            video_info = file_info['video_info']
                            st.write(f"**Video:** {video_info['codec']} | {video_info['width']}x{video_info['height']}")
                        
                        if file_info['audio_info']:
                            audio_info = file_info['audio_info']
                            st.write(f"**Audio:** {audio_info['codec']} | {audio_info['sample_rate']}Hz")
                        
                        if not file_info['has_video']:
                            st.error("❌ This file doesn't contain video!")
                            return
                    
                    progress_bar.progress(40)
                    status_placeholder.info("🎬 Converting video... (this may take a while)")
                    
                    # Generate output filename
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    safe_name = sanitize_filename(base_name)
                    output_filename = f"{safe_name}.{output_format}"
                    output_path = os.path.join(temp_dir, output_filename)
                    
                    progress_bar.progress(60)
                    
                    # Convert file
                    success, message = convert_video_file(input_path, output_path, output_format, quality)
                    
                    progress_bar.progress(100)
                    
                    if success:
                        status_placeholder.success("✅ Video conversion completed successfully!")
                        st.balloons()
                        
                        # Read converted file with progress for large files
                        if os.path.exists(output_path):
                            file_size = os.path.getsize(output_path)
                            size_display = format_file_size(file_size)
                            
                            st.success(f"**Converted file size:** {size_display}")
                            
                            # For very large files, show a warning about download time
                            if file_size > 500 * 1024**2:  # > 500MB
                                st.warning("⏳ Large file - download may take some time depending on your internet speed.")
                            
                            # Read file for download
                            with open(output_path, 'rb') as f:
                                converted_data = f.read()
                            
                            # Set MIME type based on format
                            mime_types = {
                                "mp4": "video/mp4",
                                "avi": "video/x-msvideo",
                                "mkv": "video/x-matroska",
                                "webm": "video/webm",
                                "mov": "video/quicktime"
                            }
                            mime_type = mime_types.get(output_format, "video/mp4")
                            
                            st.download_button(
                                label=f"📥 Download {output_format.upper()} File ({size_display})",
                                data=converted_data,
                                file_name=output_filename,
                                mime=mime_type,
                                use_container_width=True,
                                help="Large file - download will start when you click" if file_size > 100 * 1024**2 else "Click to download your converted video file"
                            )
                        else:
                            st.error("❌ Converted file not found!")
                    else:
                        status_placeholder.error(f"❌ Video conversion failed: {message}")
                        
                except Exception as e:
                    status_placeholder.error(f"❌ Error during conversion: {str(e)}")
                
                finally:
                    time.sleep(2)
                    progress_placeholder.empty()
    
    with col2:
        st.markdown("### 🎬 Supported Input Formats:")
        st.markdown("""
        **Video Files:**
        - MP4, MOV, AVI
        - MKV, WebM, FLV
        - WMV, M4V
        """)
        
        st.markdown("### 🎯 Output Formats:")
        st.markdown("""
        - **MP4** - Universal compatibility
        - **AVI** - Legacy support
        - **MKV** - High quality container
        - **WebM** - Web optimized
        - **MOV** - Apple/QuickTime
        """)
        
        st.markdown("### ⚙️ Quality Settings:")
        st.markdown("""
        - **High** - Best quality, slower
        - **Medium** - Balanced (recommended)
        - **Low** - Smaller files, faster
        - **Ultrafast** - Quick conversion
        """)
        
        st.markdown("### ⏱️ Processing Times:")
        st.markdown("""
        - **Small files (<100MB):** 1-5 minutes
        - **Medium files (100MB-1GB):** 5-15 minutes
        - **Large files (1-5GB):** 15-45 minutes
        - **Very large (5-10GB):** 45+ minutes
        """)

# Continuation of the Media Converter Suite

def extract_audio_tab():
    """Extract audio from video files"""
    st.header("🎵 Extract Audio from Video")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Output format selection
        output_format = st.selectbox(
            "🎯 Extract as:",
            ["mp3", "wav", "flac"],
            index=0,
            key="extract_output_format"
        )
        
        # Quality settings for MP3
        if output_format == "mp3":
            quality = st.selectbox(
                "🎚️ Audio Quality:",
                ["128k", "192k", "256k", "320k"],
                index=1,
                key="extract_quality"
            )
        else:
            quality = "192k"
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload Video file:",
            type=["mp4", "mov", "avi", "mkv", "webm", "flv", "wmv", "m4v"],
            help="Select a video file to extract audio from",
            key="extract_upload"
        )
        
        if uploaded_file is not None:
            file_size_bytes = len(uploaded_file.getvalue())
            file_size = format_file_size(file_size_bytes)
            
            st.info(f"**File:** {uploaded_file.name} ({file_size})")
            
            if st.button(f"🎵 Extract {output_format.upper()} Audio", type="primary", use_container_width=True, key="extract_convert"):
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                with status_placeholder:
                    st.info("🔄 Starting audio extraction...")
                
                with progress_placeholder:
                    progress_bar = st.progress(0)
                
                try:
                    # Create temp directory
                    temp_dir = tempfile.mkdtemp()
                    
                    # Save uploaded file
                    input_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    progress_bar.progress(25)
                    status_placeholder.info("📋 Analyzing video...")
                    
                    # Get file info
                    file_info = get_file_info(input_path)
                    if file_info:
                        st.write(f"**Duration:** {format_duration(file_info['duration'])}")
                        
                        if file_info['audio_info']:
                            audio_info = file_info['audio_info']
                            st.write(f"**Original Audio:** {audio_info['codec']} | {audio_info['sample_rate']}Hz | {audio_info['channels']} channels")
                        
                        if not file_info['has_audio']:
                            st.error("❌ This video doesn't contain audio to extract!")
                            return
                    
                    progress_bar.progress(50)
                    status_placeholder.info("🎵 Extracting audio...")
                    
                    # Generate output filename
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    safe_name = sanitize_filename(base_name)
                    output_filename = f"{safe_name}_audio.{output_format}"
                    output_path = os.path.join(temp_dir, output_filename)
                    
                    progress_bar.progress(75)
                    
                    # Extract audio
                    success, message = extract_audio_from_video(input_path, output_path, output_format, quality)
                    
                    progress_bar.progress(100)
                    
                    if success:
                        status_placeholder.success("✅ Audio extraction completed successfully!")
                        st.balloons()
                        
                        if os.path.exists(output_path):
                            file_size = os.path.getsize(output_path)
                            size_display = format_file_size(file_size)
                            
                            st.success(f"**Extracted file size:** {size_display}")
                            
                            # Read file for download
                            with open(output_path, 'rb') as f:
                                audio_data = f.read()
                            
                            # Set MIME type
                            mime_types = {
                                "mp3": "audio/mpeg",
                                "wav": "audio/wav",
                                "flac": "audio/flac"
                            }
                            mime_type = mime_types.get(output_format, "audio/mpeg")
                            
                            st.download_button(
                                label=f"📥 Download {output_format.upper()} Audio ({size_display})",
                                data=audio_data,
                                file_name=output_filename,
                                mime=mime_type,
                                use_container_width=True
                            )
                        else:
                            st.error("❌ Extracted audio file not found!")
                    else:
                        status_placeholder.error(f"❌ Audio extraction failed: {message}")
                        
                except Exception as e:
                    status_placeholder.error(f"❌ Error during extraction: {str(e)}")
                
                finally:
                    time.sleep(2)
                    progress_placeholder.empty()
    
    with col2:
        st.markdown("### 🎵 Audio Extraction:")
        st.markdown("""
        Extract high-quality audio from any video file without losing quality.
        """)
        
        st.markdown("### 📁 Supported Videos:")
        st.markdown("""
        - MP4, MOV, AVI
        - MKV, WebM, FLV
        - WMV, M4V
        """)
        
        st.markdown("### 🎯 Audio Formats:")
        st.markdown("""
        - **MP3** - Universal, compressed
        - **WAV** - Uncompressed, large
        - **FLAC** - Lossless compression
        """)

def compress_video_tab():
    """Compress video files to reduce size"""
    st.header("🗜️ Video Compressor")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Compression level
        compression_level = st.selectbox(
            "🎚️ Compression Level:",
            ["light", "medium", "heavy", "maximum"],
            index=1,
            key="compression_level",
            help="Higher compression = smaller file size but lower quality"
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload Video file to compress:",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            help="Select a video file to compress and reduce its size",
            key="compress_upload"
        )
        
        if uploaded_file is not None:
            file_size_bytes = len(uploaded_file.getvalue())
            file_size = format_file_size(file_size_bytes)
            
            st.info(f"**Original File:** {uploaded_file.name} ({file_size})")
            
            # Show expected compression ratios
            compression_ratios = {
                "light": "10-30% smaller",
                "medium": "30-50% smaller", 
                "heavy": "50-70% smaller",
                "maximum": "70-80% smaller"
            }
            
            st.write(f"**Expected result:** {compression_ratios[compression_level]}")
            
            if st.button("🗜️ Compress Video", type="primary", use_container_width=True, key="compress_convert"):
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                with status_placeholder:
                    st.info("🔄 Starting video compression...")
                
                with progress_placeholder:
                    progress_bar = st.progress(0)
                
                try:
                    # Create temp directory
                    temp_dir = tempfile.mkdtemp()
                    
                    # Save uploaded file
                    input_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    progress_bar.progress(20)
                    status_placeholder.info("📋 Analyzing video...")
                    
                    # Get file info
                    file_info = get_file_info(input_path)
                    if file_info:
                        st.write(f"**Duration:** {format_duration(file_info['duration'])}")
                        
                        if file_info['video_info']:
                            video_info = file_info['video_info']
                            st.write(f"**Resolution:** {video_info['width']}x{video_info['height']}")
                    
                    progress_bar.progress(40)
                    status_placeholder.info("🗜️ Compressing video... (this may take a while)")
                    
                    # Generate output filename
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    safe_name = sanitize_filename(base_name)
                    output_filename = f"{safe_name}_compressed.mp4"
                    output_path = os.path.join(temp_dir, output_filename)
                    
                    progress_bar.progress(70)
                    
                    # Compress video
                    success, message = compress_video(input_path, output_path, compression_level)
                    
                    progress_bar.progress(100)
                    
                    if success:
                        status_placeholder.success("✅ Video compression completed successfully!")
                        st.balloons()
                        
                        if os.path.exists(output_path):
                            compressed_size = os.path.getsize(output_path)
                            size_display = format_file_size(compressed_size)
                            
                            # Calculate compression ratio
                            compression_ratio = ((file_size_bytes - compressed_size) / file_size_bytes) * 100
                            
                            st.success(f"**Compressed size:** {size_display}")
                            st.info(f"**Size reduction:** {compression_ratio:.1f}% smaller")
                            
                            # Read file for download
                            with open(output_path, 'rb') as f:
                                compressed_data = f.read()
                            
                            st.download_button(
                                label=f"📥 Download Compressed Video ({size_display})",
                                data=compressed_data,
                                file_name=output_filename,
                                mime="video/mp4",
                                use_container_width=True
                            )
                        else:
                            st.error("❌ Compressed file not found!")
                    else:
                        status_placeholder.error(f"❌ Video compression failed: {message}")
                        
                except Exception as e:
                    status_placeholder.error(f"❌ Error during compression: {str(e)}")
                
                finally:
                    time.sleep(2)
                    progress_placeholder.empty()
    
    with col2:
        st.markdown("### 🗜️ Video Compression:")
        st.markdown("""
        Reduce video file size while maintaining good quality for easier sharing and storage.
        """)
        
        st.markdown("### 📊 Compression Levels:")
        st.markdown("""
        - **Light** - 10-30% smaller, minimal quality loss
        - **Medium** - 30-50% smaller, slight quality loss
        - **Heavy** - 50-70% smaller, noticeable quality loss
        - **Maximum** - 70-80% smaller, significant quality loss
        """)
        
        st.markdown("### 💡 Best Practices:")
        st.markdown("""
        - Start with **Medium** compression
        - Use **Light** for important videos
        - **Heavy/Maximum** for social media
        - Test different levels for best results
        """)

def batch_converter_tab():
    """Batch convert multiple files"""
    st.header("📦 Batch Converter")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("🚀 Convert multiple files at once!")
        
        # Operation type
        operation = st.selectbox(
            "🎯 Operation:",
            ["Audio Conversion", "Video Conversion", "Audio Extraction", "Video Compression"],
            key="batch_operation"
        )
        
        # Format selection based on operation
        if operation == "Audio Conversion":
            output_format = st.selectbox(
                "🎯 Convert to:",
                ["mp3", "wav", "flac", "aac", "ogg"],
                key="batch_audio_format"
            )
            if output_format in ["mp3", "aac"]:
                quality = st.selectbox(
                    "🎚️ Quality:",
                    ["128k", "192k", "256k", "320k"],
                    index=1,
                    key="batch_audio_quality"
                )
            else:
                quality = "192k"
                
        elif operation == "Video Conversion":
            output_format = st.selectbox(
                "🎯 Convert to:",
                ["mp4", "avi", "mkv", "webm", "mov"],
                key="batch_video_format"
            )
            quality = st.selectbox(
                "🎚️ Quality:",
                ["high", "medium", "low", "ultrafast"],
                index=1,
                key="batch_video_quality"
            )
            
        elif operation == "Audio Extraction":
            output_format = st.selectbox(
                "🎯 Extract as:",
                ["mp3", "wav", "flac"],
                key="batch_extract_format"
            )
            quality = "192k"
            
        else:  # Video Compression
            output_format = "mp4"
            quality = st.selectbox(
                "🎚️ Compression:",
                ["light", "medium", "heavy", "maximum"],
                index=1,
                key="batch_compress_level"
            )
        
        # Multiple file upload
        uploaded_files = st.file_uploader(
            "📁 Upload multiple files:",
            accept_multiple_files=True,
            type=["mp3", "wav", "flac", "m4a", "aac", "ogg", "mp4", "mov", "avi", "mkv", "webm"],
            help="Select multiple files to process",
            key="batch_upload"
        )
        
        if uploaded_files:
            st.write(f"**Selected {len(uploaded_files)} files:**")
            
            total_size = 0
            for file in uploaded_files:
                file_size = len(file.getvalue())
                total_size += file_size
                st.write(f"- {file.name} ({format_file_size(file_size)})")
            
            st.info(f"**Total size:** {format_file_size(total_size)}")
            
            if len(uploaded_files) > 10:
                st.warning("⚠️ Processing more than 10 files may take a very long time!")
            
            if st.button(f"🚀 Start Batch {operation}", type="primary", use_container_width=True, key="batch_convert"):
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                results = []
                failed_files = []
                
                try:
                    temp_dir = tempfile.mkdtemp()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        current_progress = int((i / len(uploaded_files)) * 100)
                        
                        with status_placeholder:
                            st.info(f"🔄 Processing file {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        with progress_placeholder:
                            st.progress(current_progress)
                        
                        try:
                            # Save current file
                            input_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(input_path, "wb") as f:
                                f.write(uploaded_file.getvalue())
                            
                            # Generate output filename
                            base_name = os.path.splitext(uploaded_file.name)[0]
                            safe_name = sanitize_filename(base_name)
                            
                            if operation == "Audio Conversion":
                                output_filename = f"{safe_name}.{output_format}"
                                output_path = os.path.join(temp_dir, output_filename)
                                success, message = convert_audio_file(input_path, output_path, output_format, quality)
                                
                            elif operation == "Video Conversion":
                                output_filename = f"{safe_name}.{output_format}"
                                output_path = os.path.join(temp_dir, output_filename)
                                success, message = convert_video_file(input_path, output_path, output_format, quality)
                                
                            elif operation == "Audio Extraction":
                                output_filename = f"{safe_name}_audio.{output_format}"
                                output_path = os.path.join(temp_dir, output_filename)
                                success, message = extract_audio_from_video(input_path, output_path, output_format, quality)
                                
                            else:  # Video Compression
                                output_filename = f"{safe_name}_compressed.mp4"
                                output_path = os.path.join(temp_dir, output_filename)
                                success, message = compress_video(input_path, output_path, quality)
                            
                            if success and os.path.exists(output_path):
                                with open(output_path, 'rb') as f:
                                    file_data = f.read()
                                
                                results.append({
                                    'original_name': uploaded_file.name,
                                    'output_name': output_filename,
                                    'data': file_data,
                                    'size': len(file_data)
                                })
                            else:
                                failed_files.append(f"{uploaded_file.name}: {message}")
                                
                        except Exception as e:
                            failed_files.append(f"{uploaded_file.name}: {str(e)}")
                    
                    # Final results
                    with progress_placeholder:
                        st.progress(100)
                    
                    if results:
                        with status_placeholder:
                            st.success(f"✅ Batch processing completed! {len(results)} files processed successfully.")
                        
                        if failed_files:
                            st.warning(f"⚠️ {len(failed_files)} files failed to process:")
                            for error in failed_files:
                                st.write(f"- {error}")
                        
                        st.balloons()
                        
                        # Create download buttons for each result
                        st.markdown("### 📥 Download Processed Files:")
                        
                        for result in results:
                            file_size = format_file_size(result['size'])
                            
                            # Set MIME type
                            ext = result['output_name'].split('.')[-1].lower()
                            mime_types = {
                                "mp3": "audio/mpeg", "wav": "audio/wav", "flac": "audio/flac",
                                "aac": "audio/aac", "ogg": "audio/ogg",
                                "mp4": "video/mp4", "avi": "video/x-msvideo", 
                                "mkv": "video/x-matroska", "webm": "video/webm", 
                                "mov": "video/quicktime"
                            }
                            mime_type = mime_types.get(ext, "application/octet-stream")
                            
                            st.download_button(
                                label=f"📥 {result['output_name']} ({file_size})",
                                data=result['data'],
                                file_name=result['output_name'],
                                mime=mime_type,
                                key=f"download_{result['output_name']}"
                            )
                    else:
                        with status_placeholder:
                            st.error("❌ All files failed to process!")
                        
                        for error in failed_files:
                            st.write(f"- {error}")
                            
                except Exception as e:
                    status_placeholder.error(f"❌ Batch processing error: {str(e)}")
                
                finally:
                    time.sleep(2)
                    progress_placeholder.empty()
    
    with col2:
        st.markdown("### 📦 Batch Processing:")
        st.markdown("""
        Process multiple files at once to save time and effort.
        """)
        
        st.markdown("### 🚀 Available Operations:")
        st.markdown("""
        - **Audio Conversion** - Convert audio formats
        - **Video Conversion** - Convert video formats  
        - **Audio Extraction** - Extract audio from videos
        - **Video Compression** - Reduce video file sizes
        """)
        
        st.markdown("### ⚙️ Batch Limits:")
        st.markdown("""
        - **Recommended:** Up to 10 files
        - **Maximum:** 50 files per batch
        - **Size limit:** 10GB per file
        - **Processing time:** Varies by operation
        """)
        
        st.markdown("### 💡 Tips:")
        st.markdown("""
        - Group similar files together
        - Use consistent quality settings
        - Monitor processing progress
        - Download files individually
        """)

def main():
    """Main application"""
    st.title("🎵 Complete Media Converter Suite")
    st.markdown("Convert audio, video, and extract media with ease!")
    
    # Check if FFmpeg is available
    if not check_ffmpeg():
        st.error("""
        ❌ **FFmpeg not found!**
        
        This application requires FFmpeg to be installed on your system.
        
        **Installation instructions:**
        - **Windows:** Download from https://ffmpeg.org/download.html
        - **macOS:** `brew install ffmpeg`
        - **Linux:** `sudo apt install ffmpeg` or `sudo yum install ffmpeg`
        
        After installation, restart this application.
        """)
        return
    
    # Create tabs
    tabs = st.tabs([
        "🎥 YouTube to MP3",
        "🎵 Audio Converter", 
        "🎬 Video Converter",
        "🎵 Extract Audio",
        "🗜️ Compress Video",
        "📦 Batch Converter"
    ])
    
    with tabs[0]:
        youtube_to_mp3_tab()
    
    with tabs[1]:
        audio_converter_tab()
    
    with tabs[2]:
        video_converter_tab()
    
    with tabs[3]:
        extract_audio_tab()
    
    with tabs[4]:
        compress_video_tab()
    
    with tabs[5]:
        batch_converter_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🎵 Complete Media Converter Suite | Built with Streamlit & FFmpeg</p>
        <p><small>Supports audio/video conversion, extraction, compression & batch processing</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()