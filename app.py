import streamlit as st
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
        
        return {
            'duration': duration,
            'format': format_name,
            'has_video': has_video,
            'has_audio': has_audio
        }
    except:
        return None

def convert_file_with_ffmpeg(input_path, output_path, output_format):
    """Convert file using FFmpeg directly"""
    try:
        if output_format.lower() == 'mp3':
            # Convert to MP3
            cmd = [
                'ffmpeg', '-i', input_path, '-vn', '-acodec', 'libmp3lame',
                '-ab', '192k', '-ar', '44100', '-y', output_path
            ]
        elif output_format.lower() == 'mp4':
            # Convert to MP4
            cmd = [
                'ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'aac',
                '-strict', 'experimental', '-b:a', '192k', '-y', output_path
            ]
        else:
            return False, "Unsupported output format"
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True, "Conversion successful"
        else:
            return False, f"FFmpeg error: {result.stderr}"
            
    except Exception as e:
        return False, f"Conversion error: {str(e)}"

def download_video_as_mp3(url, output_dir, cookies_file=None):
    """Download video as MP3"""
    
    # Check if FFmpeg is available
    if not check_ffmpeg():
        return {
            'success': False,
            'error': "❌ FFmpeg not found. FFmpeg is required for audio conversion. Please install FFmpeg first."
        }
    
    try:
        # Start with basic options
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
        
        # Add cookies if provided
        if cookies_file and os.path.exists(cookies_file):
            ydl_opts['cookiefile'] = cookies_file
        
        # Try to extract info first
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                error_msg = str(e).lower()
                if 'sign in' in error_msg or 'bot' in error_msg:
                    return {
                        'success': False,
                        'error': "⚠️ YouTube detected automated access. This video may require authentication. Try:\n• Using cookies from your browser\n• Waiting 10-15 minutes\n• Using a different video"
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
            
            # Sanitize title for filename
            safe_title = sanitize_filename(title)
            if len(safe_title) > 100:
                safe_title = safe_title[:100] + "..."
            
            ydl_opts['outtmpl'] = os.path.join(output_dir, f'{safe_title}.%(ext)s')
        
        # Now download with conversion
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
                # Find the downloaded MP3 file
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
    st.header("🎵 YouTube to MP3")
    
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

def file_converter_tab():
    """File conversion tab for various formats"""
    st.header("🔄 File Converter")
    
    # Conversion options
    conversion_options = {
        "M4A to MP3": {"input": "m4a", "output": "mp3"},
        "MP4 to MP3": {"input": "mp4", "output": "mp3"},
        "MOV to MP4": {"input": "mov", "output": "mp4"},
        "MOV to MP3": {"input": "mov", "output": "mp3"},
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Conversion type selection
        conversion_type = st.selectbox(
            "🎯 Select Conversion Type:",
            list(conversion_options.keys()),
            key="conversion_type"
        )
        
        input_format = conversion_options[conversion_type]["input"]
        output_format = conversion_options[conversion_type]["output"]
        
        # File upload
        uploaded_file = st.file_uploader(
            f"📁 Upload {input_format.upper()} file:",
            type=[input_format],
            help=f"Select a {input_format.upper()} file to convert to {output_format.upper()}",
            key="file_upload"
        )
        
        if uploaded_file is not None:
            # Show file info
            file_size = len(uploaded_file.getvalue()) // 1024  # KB
            st.info(f"**File:** {uploaded_file.name} ({file_size} KB)")
            
            if st.button(f"🔄 Convert to {output_format.upper()}", type="primary", use_container_width=True, key="file_convert"):
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                
                with status_placeholder:
                    st.info("🔄 Starting conversion...")
                
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
                        
                        if output_format == 'mp3' and not file_info['has_audio']:
                            st.error("❌ This file doesn't contain audio to extract!")
                            return
                    
                    progress_bar.progress(50)
                    status_placeholder.info("🔄 Converting file...")
                    
                    # Generate output filename
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    safe_name = sanitize_filename(base_name)
                    output_filename = f"{safe_name}.{output_format}"
                    output_path = os.path.join(temp_dir, output_filename)
                    
                    progress_bar.progress(75)
                    
                    # Convert file
                    success, message = convert_file_with_ffmpeg(input_path, output_path, output_format)
                    
                    progress_bar.progress(100)
                    
                    if success:
                        status_placeholder.success("✅ Conversion completed successfully!")
                        st.balloons()
                        
                        # Read converted file
                        if os.path.exists(output_path):
                            with open(output_path, 'rb') as f:
                                converted_data = f.read()
                            
                            converted_size = len(converted_data) // 1024
                            st.success(f"**Converted file size:** {converted_size} KB")
                            
                            # Set MIME type
                            mime_type = "audio/mpeg" if output_format == "mp3" else "video/mp4"
                            
                            st.download_button(
                                label=f"📥 Download {output_format.upper()} File",
                                data=converted_data,
                                file_name=output_filename,
                                mime=mime_type,
                                use_container_width=True
                            )
                        else:
                            st.error("❌ Converted file not found!")
                    else:
                        status_placeholder.error(f"❌ Conversion failed: {message}")
                        
                except Exception as e:
                    status_placeholder.error(f"❌ Error during conversion: {str(e)}")
                
                finally:
                    time.sleep(2)
                    progress_placeholder.empty()
    
    with col2:
        st.markdown("### 🎯 Supported Conversions:")
        st.markdown("""
        - **M4A → MP3** (Audio only)
        - **MP4 → MP3** (Extract audio)
        - **MOV → MP4** (Video format)
        - **MOV → MP3** (Extract audio)
        """)
        
        st.markdown("### 📋 Instructions:")
        st.markdown("""
        1. Select conversion type
        2. Upload your file
        3. Click convert
        4. Download result
        """)
        
        st.markdown("### ⚙️ Technical Details:")
        st.markdown("""
        - **Audio quality:** 192 kbps
        - **Video codec:** H.264
        - **Audio codec:** AAC/MP3
        - **Max file size:** Platform dependent
        """)
        
        st.markdown("### 💡 Tips:")
        st.markdown("""
        - Larger files take longer
        - Keep original files as backup
        - Check audio quality before deleting originals
        """)

def main():
    # Page config
    st.set_page_config(
        page_title="Media Converter",
        page_icon="🎵",
        layout="wide"
    )
    
    # Header with branding
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: bold;">🎵 Multi-Format Media Converter</h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 1.2em;">Convert YouTube videos and media files to MP3/MP4</p>
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
    tab1, tab2 = st.tabs(["🎥 YouTube to MP3", "🔄 File Converter"])
    
    with tab1:
        youtube_to_mp3_tab()
    
    with tab2:
        file_converter_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🔒 <strong>Privacy:</strong> Files are processed temporarily and not stored permanently</p>
        <p>⚡ <strong>Performance:</strong> Conversion speed depends on file size and server resources</p>
        <p>💻 <strong>Open Source:</strong> Built with Streamlit, yt-dlp, and FFmpeg</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()