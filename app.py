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
                'preferredquality': '192',  # More reliable than 320
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'extract_flat': False,
            # Remove quiet mode for debugging
            'quiet': False,
            'no_warnings': False,
            # Add some headers to avoid detection
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
            if len(safe_title) > 100:  # Limit filename length
                safe_title = safe_title[:100] + "..."
            
            # Update output template with safe title
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
                
                # Verify file exists and has content
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
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "sign in" in error_msg.lower() or "bot" in error_msg.lower():
                return {
                    'success': False,
                    'error': "⚠️ YouTube Bot Detection: Try uploading cookies from your browser or wait before retrying."
                }
            elif "unavailable" in error_msg.lower() or "private" in error_msg.lower():
                return {
                    'success': False,
                    'error': "❌ Video Not Available: This video may be private, age-restricted, or geo-blocked."
                }
            else:
                return {
                    'success': False,
                    'error': f"❌ Download Failed: {error_msg}"
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
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def install_requirements():
    """Install required packages"""
    required_packages = ['yt-dlp']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            st.error(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            st.rerun()

def main():
    # Install requirements if needed
    try:
        import yt_dlp
    except ImportError:
        install_requirements()
        return
    
    # Page config
    st.set_page_config(
        page_title="YouTube to MP3",
        page_icon="🎵",
        layout="wide"
    )
    
    # Header with branding
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: bold;">🎵 YouTube to MP3 Converter</h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 1.2em;">Convert YouTube videos to high-quality MP3</p>
        <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 0.9em; font-style: italic;">Built By Nepal Media Group</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check FFmpeg availability
    if not check_ffmpeg():
        st.error("⚠️ **FFmpeg not found!** This tool requires FFmpeg for audio conversion.")
        st.markdown("""
        **To install FFmpeg:**
        
        **On Ubuntu/Debian:**
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```
        
        **On macOS:**
        ```bash
        brew install ffmpeg
        ```
        
        **On Windows:**
        - Download from https://ffmpeg.org/download.html
        - Add to PATH environment variable
        
        **For Streamlit Cloud/Heroku:**
        - Add ffmpeg to requirements.txt or use buildpacks
        """)
        return
    
    # Create columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # URL input
        url = st.text_input(
            "🔗 Enter YouTube URL:",
            placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            help="Paste a YouTube video URL here"
        )
        
        # Cookie file upload (optional)
        with st.expander("🍪 Advanced: Upload Cookies File (Optional)", expanded=False):
            st.markdown("""
            **For age-restricted or bot-detected videos:**
            - Export cookies from your browser using an extension like "Get cookies.txt"
            - Upload the cookies.txt file here
            - File must be in Netscape/Mozilla format
            """)
            
            cookies_file = st.file_uploader(
                "Upload cookies.txt file",
                type=['txt'],
                help="Optional: Upload browser cookies to access restricted content"
            )
        
        # Convert button
        if st.button("🎵 Convert to MP3", type="primary", use_container_width=True):
            if not url or not url.strip():
                st.error("❌ Please enter a valid YouTube URL")
                return
            
            # Basic URL validation
            if not any(domain in url.lower() for domain in ['youtube.com', 'youtu.be']):
                st.warning("⚠️ This doesn't look like a YouTube URL. This tool works best with YouTube videos.")
            
            # Create progress placeholders
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            with status_placeholder:
                st.info("🔄 Starting conversion...")
            
            with progress_placeholder:
                progress_bar = st.progress(0)
            
            try:
                # Handle cookies file if uploaded
                cookies_path = None
                if cookies_file is not None:
                    temp_cookies_dir = tempfile.mkdtemp()
                    cookies_path = os.path.join(temp_cookies_dir, "cookies.txt")
                    with open(cookies_path, "wb") as f:
                        f.write(cookies_file.getvalue())
                
                # Update progress
                progress_bar.progress(20)
                status_placeholder.info("📋 Extracting video information...")
                
                # Create temporary directory
                temp_dir = tempfile.mkdtemp()
                
                progress_bar.progress(40)
                status_placeholder.info("⬇️ Downloading audio...")
                
                # Download and convert
                result = download_video_as_mp3(url, temp_dir, cookies_path)
                
                progress_bar.progress(80)
                status_placeholder.info("🎵 Converting to MP3...")
                
                progress_bar.progress(100)
                
                if result['success']:
                    status_placeholder.success("✅ Conversion completed successfully!")
                    
                    # Show success animation
                    st.balloons()
                    
                    # Display file info
                    st.success(f"**Title:** {result['title']}")
                    if result.get('duration'):
                        st.info(f"**Duration:** {format_duration(result['duration'])}")
                    
                    # Read file for download
                    if result['file_path'] and os.path.exists(result['file_path']):
                        with open(result['file_path'], 'rb') as file:
                            file_data = file.read()
                        
                        file_size = len(file_data) // 1024  # KB
                        st.write(f"**File size:** {file_size} KB")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download MP3 File",
                            data=file_data,
                            file_name=result['filename'],
                            mime="audio/mpeg",
                            use_container_width=True
                        )
                        
                        # Clean up temp file
                        try:
                            os.remove(result['file_path'])
                        except:
                            pass
                            
                    else:
                        st.error("❌ File was converted but could not be found for download")
                        
                else:
                    status_placeholder.error(result['error'])
                    
            except Exception as e:
                status_placeholder.error(f"❌ Unexpected error: {str(e)}")
                st.exception(e)  # Show full traceback for debugging
            
            finally:
                # Clear progress after delay
                time.sleep(2)
                progress_placeholder.empty()
    
    with col2:
        # Instructions
        st.markdown("### 📖 How to use:")
        st.markdown("""
        1. **Copy** a YouTube URL
        2. **Paste** it in the input field  
        3. **Click** Convert to MP3
        4. **Wait** for processing
        5. **Download** your MP3 file
        """)
        
        st.markdown("### ✨ Features:")
        st.markdown("""
        - 🎵 High quality MP3 (192kbps)
        - 🚀 Fast conversion
        - 📱 Works on any device
        - 🔒 Privacy focused
        - 📹 YouTube support
        """)
        
        st.markdown("### 🔧 Requirements:")
        st.markdown("""
        - **FFmpeg** must be installed
        - **Internet connection**
        - **Valid YouTube URL**
        """)
        
        st.markdown("### ⚠️ Troubleshooting:")
        st.markdown("""
        **"Bot detection" error:**
        - Upload cookies from your browser
        - Wait 10-15 minutes before retrying
        - Try a different video
        
        **"Video unavailable" error:**
        - Video may be private/geo-blocked
        - Check if video exists and is public
        - Try with cookies if age-restricted
        
        **"FFmpeg not found" error:**
        - Install FFmpeg on your system
        - Add FFmpeg to system PATH
        """)
        
        st.markdown("### 💡 Tips:")
        st.markdown("""
        - **Public videos**: Usually work without cookies
        - **Age-restricted**: Requires cookies
        - **Private videos**: Not accessible
        - **Long videos**: May take more time
        """)

if __name__ == "__main__":
    main()