# Set MIME type based on format
                            mime_types = {
                                "mp3": "audio/mpeg",
                                "wav": "audio/wav",
                                "flac": "audio/flac",
                                "aac": "audio/aac",
                                "ogg": "audio/ogg"
                            }
                            mime_type = mime_types.get(output_format, "audio/mpeg")import streamlit as st
import yt_dlp
import os
import tempfile
import time
import re
from pathlib import Path
import subprocess
import sys

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
                        
                        file_size = len(file_data) // 1024
                        st.write(f"**File size:** {file_size} KB")
                        
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
            if file_size_bytes > 1024**3:  # > 1GB
                file_size = f"{file_size_bytes / (1024**3):.2f} GB"
            elif file_size_bytes > 1024**2:  # > 1MB
                file_size = f"{file_size_bytes / (1024**2):.2f} MB"
            else:
                file_size = f"{file_size_bytes // 1024} KB"
            
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
                    
                    progress_bar.progress(25)
                    status_placeholder.info("📋 Analyzing file...")
                    
                    # Get file info
                    file_info = get_file_info(input_path)
                    if file_info:
                        st.write(f"**Duration:** {format_duration(file_info['duration'])}")
                        st.write(f"**Format:** {file_info['format']}")
                        
                        if file_info['audio_info']:
                            audio_info = file_info['audio_info']
                            st.write(f"**Audio:** {audio_info['codec']} | {audio_info['sample_rate']}Hz | {audio_info['channels']} channels")
                        
                        if not file_info['has_audio']:
                            st.error("❌ This file doesn't contain audio to extract!")
                            return
                    
                    progress_bar.progress(50)
                    status_placeholder.info("🎵 Converting audio...")
                    
                    # Generate output filename
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    safe_name = sanitize_filename(base_name)
                    output_filename = f"{safe_name}.{output_format}"
                    output_path = os.path.join(temp_dir, output_filename)
                    
                    progress_bar.progress(75)
                    
                    # Convert file
                    success, message = convert_audio_file(input_path, output_path, output_format, quality)
                    
                    progress_bar.progress(100)
                    
                    if success:
                        status_placeholder.success("✅ Audio conversion completed successfully!")
                        st.balloons()
                        
                        # Read converted file with progress for large files
                        if os.path.exists(output_path):
                            file_size = os.path.getsize(output_path)
                            
                            # Show file size in appropriate unit
                            if file_size > 1024**3:  # > 1GB
                                size_display = f"{file_size / (1024**3):.2f} GB"
                            elif file_size > 1024**2:  # > 1MB
                                size_display = f"{file_size / (1024**2):.2f} MB"
                            else:
                                size_display = f"{file_size // 1024} KB"
                            
                            st.success(f"**Converted file size:** {size_display}")
                            
                            # For very large files, show a warning about download time
                            if file_size > 500 * 1024**2:  # > 500MB
                                st.warning("⏳ Large file - download may take some time depending on your internet speed.")
                            
                            # Read file in chunks for large files to avoid memory issues
                            def read_file_in_chunks(file_path, chunk_size=8192):
                                with open(file_path, 'rb') as f:
                                    while True:
                                        chunk = f.read(chunk_size)
                                        if not chunk:
                                            break
                                        yield chunk
                            
                            # For files < 100MB, read normally. For larger files, inform user
                            if file_size < 100 * 1024**2:  # < 100MB
                                with open(output_path, 'rb') as f:
                                    converted_data = f.read()
                                
                                st.download_button(
                                    label=f"📥 Download {output_format.upper()} File",
                                    data=converted_data,
                                    file_name=output_filename,
                                    mime=mime_type,
                                    use_container_width=True
                                )
                            else:
                                # For large files, read in chunks and provide download
                                with open(output_path, 'rb') as f:
                                    converted_data = f.read()
                                
                                st.download_button(
                                    label=f"📥 Download {output_format.upper()} File ({size_display})",
                                    data=converted_data,
                                    file_name=output_filename,
                                    mime=mime_type,
                                    use_container_width=True,
                                    help="Large file - download will start when you click"
                                )
                        else:
                            st.error("❌ Converted file not found!")
                    else:
                        status_placeholder.error(f"❌ Audio conversion failed: {message}")
                        
                except Exception as e:
                    status_placeholder.error(f"❌ Error during conversion: {str(e)}")
                
                finally:
                    time.sleep(2)
                    progress_placeholder.empty()
    
    with col2:
        st.markdown("### 🎵 Supported Input Formats:")
        st.markdown("""
        **Audio Files:**
        - MP3, WAV, FLAC
        - M4A, AAC, OGG, WMA
        
        **Video Files (extract audio):**
        - MP4, MOV, AVI, MKV
        """)
        
        st.markdown("### 🎯 Output Formats:")
        st.markdown("""
        - **MP3** - Universal compatibility
        - **WAV** - Uncompressed quality
        - **FLAC** - Lossless compression
        - **AAC** - Modern, efficient
        - **OGG** - Open source format
        """)
        
        st.markdown("### ⚙️ Quality Settings:")
        st.markdown("""
        - **128k** - Small size, good quality
        - **192k** - Balanced (recommended)
        - **256k** - High quality
        - **320k** - Maximum quality
        """)
        
        st.markdown("### 💡 Tips:")
        st.markdown("""
        - Higher quality = larger file size
        - WAV and FLAC are lossless
        - MP3 is most compatible
        - Use 192k for good balance
        """)

def video_converter_tab():
    """Video conversion tab for various video formats"""
    st.header("🎬 Video Converter")
    
    # Video format options
    video_formats = {
        "Input Formats": ["mp4", "mov", "avi", "mkv", "webm", "flv", "wmv", "m4v"],
        "Output Formats": ["mp4", "avi", "mkv", "webm", "mov"]
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Output format selection
        output_format = st.selectbox(
            "🎯 Convert TO:",
            video_formats["Output Formats"],
            index=0,  # Default to MP4
            key="video_output_format"
        )
        
        # Quality settings
        quality = st.selectbox(
            "🎚️ Video Quality:",
            ["high", "medium", "low", "ultrafast"],
            index=1,  # Default to medium
            key="video_quality",
            help="Higher quality = better video but larger file and slower conversion"
        )
        
        # File upload with large file support
        uploaded_file = st.file_uploader(
            f"📁 Upload Video file (up to 10GB):",
            type=video_formats["Input Formats"],
            help=f"Select a video file to convert to {output_format.upper()}. Maximum file size: 10GB",
            key="video_upload"
        )
        
        if uploaded_file is not None:
            # Show file info with GB support
            file_size_bytes = len(uploaded_file.getvalue())
            if file_size_bytes > 1024**3:  # > 1GB
                file_size = f"{file_size_bytes / (1024**3):.2f} GB"
            elif file_size_bytes > 1024**2:  # > 1MB
                file_size = f"{file_size_bytes / (1024**2):.2f} MB"
            else:
                file_size = f"{file_size_bytes // 1024} KB"
            
            st.info(f"**File:** {uploaded_file.name} ({file_size})")
            
            # Show upload progress for large files
            if file_size_bytes > 100 * 1024**2:  # > 100MB
                st.info("📤 Large file detected. Video processing may take 10-30 minutes...")
            
            
            if st.button(f"🎬 Convert to {output_format.upper()}", type="primary", use_container_width=True, key="video_convert"):
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                with status_placeholder:
                    st.info("🔄 Starting video conversion...")
                
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
                            
                            # Show file size in appropriate unit
                            if file_size > 1024**3:  # > 1GB
                                size_display = f"{file_size / (1024**3):.2f} GB"
                            elif file_size > 1024**2:  # > 1MB
                                size_display = f"{file_size / (1024**2):.2f} MB"
                            else:
                                size_display = f"{file_size // 1024} KB"
                            
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
                                "avi": "video/avi",
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
                                help="Click to download your converted video file"
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
        - **MP4** - Most common format
        - **MOV** - QuickTime videos
        - **AVI** - Windows format
        - **MKV** - High-quality container
        - **WEBM** - Web optimized
        - **FLV** - Flash videos
        - **WMV** - Windows Media
        """)
        
        st.markdown("### 🎯 Output Formats:")
        st.markdown("""
        - **MP4** - Universal compatibility
        - **AVI** - Windows standard
        - **MKV** - High quality container
        - **WEBM** - Web streaming
        - **MOV** - QuickTime format
        """)
        
        st.markdown("### ⚙️ Quality Settings:")
        st.markdown("""
        - **High** - Best quality, large file
        - **Medium** - Balanced (recommended)
        - **Low** - Smaller file, lower quality
        - **Ultrafast** - Quick conversion
        """)
        
        st.markdown("### ⏱️ Processing Time:")
        st.markdown("""
        - **Short videos** - Few minutes
        - **Long videos** - May take 10+ minutes
        - **High quality** - Takes longer
        - **File size** affects speed
        """)
        
        st.markdown("### 💡 Tips:")
        st.markdown("""
        - MP4 works on most devices
        - Higher quality = longer processing
        - Large files may timeout
        - Keep originals as backup
        """)

def main():
    # Page config
    st.set_page_config(
        page_title="Complete Media Converter",
        page_icon="🎵",
        layout="wide"
    )
    
    # Configure Streamlit for large files
    st._config.set_option("server.maxUploadSize", 10240)  # 10GB in MB
    
    # Header with branding
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: bold;">🎵 Complete Media Converter Suite</h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 1.2em;">Convert YouTube videos, audio files, and video files to any format</p>
        <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 0.9em; font-style: italic;">Built By Nepal Media Group</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check FFmpeg availability
    if not check_ffmpeg():
        st.error("⚠️ **FFmpeg not found!** This tool requires FFmpeg for media conversion.")
        st.markdown("""
        **To install FFmpeg:**
        
        **Ubuntu/Debian:**
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```
        
        **macOS:**
        ```bash
        brew install ffmpeg
        ```
        
        **Windows:**
        - Download from https://ffmpeg.org/download.html
        - Add to PATH environment variable
        
        **Streamlit Cloud/Heroku:**
        - Add to packages.txt or use buildpacks
        """)
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🎥 YouTube to MP3", "🎵 Audio Converter", "🎬 Video Converter"])
    
    with tab1:
        youtube_to_mp3_tab()
    
    with tab2:
        audio_converter_tab()
    
    with tab3:
        video_converter_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🔒 <strong>Privacy:</strong> Files are processed temporarily and not stored permanently</p>
        <p>⚡ <strong>Performance:</strong> Conversion speed depends on file size and server resources</p>
        <p>💻 <strong>Open Source:</strong> Built with Streamlit, yt-dlp, and FFmpeg</p>
        <p>🎯 <strong>Formats Supported:</strong> MP3, WAV, FLAC, AAC, OGG | MP4, AVI, MKV, WEBM, MOV</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()