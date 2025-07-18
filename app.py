import streamlit as st
import yt_dlp
import os
import tempfile
import time
from pathlib import Path

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    import re
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', ' ', filename)
    return filename.strip()

def download_video_as_mp3(url, output_dir, cookies_file=None):
    """Download video as MP3"""
    try:
        # Basic yt-dlp options without cookies
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            # Enhanced bot detection bypass
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs', 'webpage'],
                    'player_client': ['android', 'web'],
                }
            },
            # Headers to mimic real browser
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
        
        # If cookies file is provided, use it
        if cookies_file and os.path.exists(cookies_file):
            ydl_opts['cookiefile'] = cookies_file
        else:
            # Smart cookie handling - try different approaches based on environment
            try:
                # Check if we're in a containerized environment
                is_container = (
                    os.path.exists('/.dockerenv') or  # Docker
                    os.path.exists('/proc/1/cgroup') or  # Container
                    os.environ.get('STREAMLIT_SHARING_MODE') or  # Streamlit Cloud
                    os.environ.get('RAILWAY_ENVIRONMENT') or  # Railway
                    os.environ.get('HEROKU_APP_NAME') or  # Heroku
                    os.environ.get('VERCEL') or  # Vercel
                    not os.path.exists(os.path.expanduser('~'))  # No home directory
                )
                
                # Try to use cookies from various sources
                cookie_sources = []
                
                if not is_container:
                    # Local environment - try browser cookies
                    browser_configs = [
                        ('chrome', None),  # Default Chrome location
                        ('firefox', None),  # Default Firefox location
                        ('safari', None),  # Default Safari location (macOS)
                        ('edge', None),  # Default Edge location
                    ]
                    
                    # Also try common alternative Chrome locations
                    alt_chrome_paths = [
                        '~/.var/app/com.google.Chrome/',  # Flatpak Chrome
                        '~/.config/chromium/',  # Chromium
                        '~/snap/chromium/common/chromium/',  # Snap Chromium
                    ]
                    
                    for path in alt_chrome_paths:
                        expanded_path = os.path.expanduser(path)
                        if os.path.exists(expanded_path):
                            browser_configs.append(('chrome', expanded_path))
                    
                    cookie_sources.extend(browser_configs)
                
                # Try each cookie source
                for browser, path in cookie_sources:
                    try:
                        if path:
                            # Use specific path
                            ydl_opts['cookiesfrombrowser'] = (browser, path)
                        else:
                            # Use default path
                            ydl_opts['cookiesfrombrowser'] = (browser,)
                        
                        # Test if this cookie source works
                        test_opts = ydl_opts.copy()
                        test_opts['quiet'] = True
                        test_opts['no_warnings'] = True
                        
                        with yt_dlp.YoutubeDL(test_opts) as test_ydl:
                            # If we can create the YoutubeDL instance without error, cookies are working
                            break
                            
                    except Exception as e:
                        # This cookie source failed, try the next one
                        if 'cookiesfrombrowser' in ydl_opts:
                            del ydl_opts['cookiesfrombrowser']
                        continue
                
                # If no cookies worked, that's fine - continue without them
                
            except Exception as e:
                # If any error occurs with cookies, just continue without them
                if 'cookiesfrombrowser' in ydl_opts:
                    del ydl_opts['cookiesfrombrowser']
        
        # First attempt with current options
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info
                info = ydl.extract_info(url, download=False)
                
                # Check if info extraction was successful
                if info is None:
                    raise Exception("Failed to extract video information")
                
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                # Download and convert
                ydl.download([url])
                
                # Find the downloaded MP3 file
                mp3_file = None
                for file in os.listdir(output_dir):
                    if file.endswith('.mp3'):
                        mp3_file = os.path.join(output_dir, file)
                        break
                
                if mp3_file is None:
                    raise Exception("MP3 file was not created")
                
                return {
                    'success': True,
                    'title': title,
                    'duration': duration,
                    'file_path': mp3_file,
                    'filename': os.path.basename(mp3_file)
                }
                
        except Exception as first_error:
            # If first attempt fails, try with minimal options
            minimal_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',  # Lower quality for better compatibility
                }],
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': False,  # We want to catch errors in fallback
            }
            
            try:
                with yt_dlp.YoutubeDL(minimal_opts) as ydl:
                    # Get video info
                    info = ydl.extract_info(url, download=False)
                    
                    # Check if info extraction was successful
                    if info is None:
                        raise Exception("Failed to extract video information - video may be unavailable")
                    
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)
                    
                    # Download and convert
                    ydl.download([url])
                    
                    # Find the downloaded MP3 file
                    mp3_file = None
                    for file in os.listdir(output_dir):
                        if file.endswith('.mp3'):
                            mp3_file = os.path.join(output_dir, file)
                            break
                    
                    if mp3_file is None:
                        raise Exception("MP3 file was not created")
                    
                    return {
                        'success': True,
                        'title': title,
                        'duration': duration,
                        'file_path': mp3_file,
                        'filename': os.path.basename(mp3_file)
                    }
            except Exception as second_error:
                # If both attempts fail, try one more time with absolute minimal options
                ultra_minimal_opts = {
                    'format': 'worst',  # Try worst quality first
                    'outtmpl': os.path.join(output_dir, 'audio.%(ext)s'),
                    'noplaylist': True,
                    'quiet': True,
                }
                
                try:
                    with yt_dlp.YoutubeDL(ultra_minimal_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        if info is None:
                            raise Exception("Video is not accessible or does not exist")
                        
                        title = info.get('title', 'Unknown')
                        duration = info.get('duration', 0)
                        
                        # Download without conversion first
                        ydl.download([url])
                        
                        # Find any downloaded file and try to convert manually
                        downloaded_file = None
                        for file in os.listdir(output_dir):
                            if not file.endswith('.mp3'):
                                downloaded_file = os.path.join(output_dir, file)
                                break
                        
                        if downloaded_file:
                            # Try to convert using FFmpeg through yt-dlp
                            convert_opts = {
                                'format': 'bestaudio',
                                'postprocessors': [{
                                    'key': 'FFmpegExtractAudio',
                                    'preferredcodec': 'mp3',
                                    'preferredquality': '128',
                                }],
                                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                                'quiet': True,
                            }
                            
                            with yt_dlp.YoutubeDL(convert_opts) as convert_ydl:
                                convert_ydl.download([url])
                            
                            # Find the MP3 file
                            mp3_file = None
                            for file in os.listdir(output_dir):
                                if file.endswith('.mp3'):
                                    mp3_file = os.path.join(output_dir, file)
                                    break
                            
                            if mp3_file:
                                return {
                                    'success': True,
                                    'title': title,
                                    'duration': duration,
                                    'file_path': mp3_file,
                                    'filename': os.path.basename(mp3_file)
                                }
                        
                        raise Exception("Could not download or convert the video")
                        
                except Exception as third_error:
                    raise Exception(f"All download attempts failed. Last error: {str(third_error)}")
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg or "bot" in error_msg.lower():
            return {
                'success': False,
                'error': "⚠️ YouTube Bot Detection: This video requires authentication. Try:\n• Using a different YouTube video\n• Waiting 10-15 minutes before trying again\n• Using a direct MP4 URL instead"
            }
        elif "Video unavailable" in error_msg or "private" in error_msg.lower():
            return {
                'success': False,
                'error': "❌ Video Not Available: This video may be private, age-restricted, or geo-blocked."
            }
        elif "cookies" in error_msg.lower():
            return {
                'success': False,
                'error': "⚠️ Cookie Issue: Running in server environment without browser cookies. This is normal for deployed apps."
            }
        else:
            return {
                'success': False,
                'error': f"❌ Download Failed: {error_msg}"
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

def main():
    # Page config
    st.set_page_config(
        page_title="NMG Video to MP3",
        page_icon="🎵",
        layout="wide"
    )
    
    # Header with branding
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: bold;">🎵 Video to MP3 Converter</h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 1.2em;">Convert YouTube videos and MP4 files to high-quality MP3</p>
        <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 0.9em; font-style: italic;">Built By Nepal Media Group</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # URL input
        url = st.text_input(
            "🔗 Enter Video URL:",
            placeholder="https://www.youtube.com/watch?v=... or https://example.com/video.mp4",
            help="Paste a YouTube video URL or direct MP4 file URL here"
        )
        
        # Cookie file upload (optional)
        with st.expander("🍪 Advanced: Upload Cookies File (Optional)", expanded=False):
            st.markdown("""
            **For age-restricted or private videos:**
            - Export cookies from your browser using a browser extension
            - Upload the cookies.txt file here
            - File must be in Netscape/Mozilla format
            """)
            
            cookies_file = st.file_uploader(
                "Upload cookies.txt file",
                type=['txt'],
                help="Optional: Upload browser cookies to access restricted content"
            )
        
        # Convert button
        if url and st.button("🎵 Convert & Download MP3", type="primary", use_container_width=True):
            if not url.strip():
                st.error("Please enter a valid video URL")
                return
            
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
                    # Save uploaded cookies file temporarily
                    temp_cookies_dir = tempfile.mkdtemp()
                    cookies_path = os.path.join(temp_cookies_dir, "cookies.txt")
                    with open(cookies_path, "wb") as f:
                        f.write(cookies_file.getvalue())
                    
                    # Validate cookies file format
                    try:
                        with open(cookies_path, "r") as f:
                            first_line = f.readline().strip()
                            if not (first_line.startswith("# HTTP Cookie File") or 
                                   first_line.startswith("# Netscape HTTP Cookie File")):
                                st.warning("⚠️ Cookies file may not be in correct format. First line should be '# HTTP Cookie File' or '# Netscape HTTP Cookie File'")
                    except:
                        st.warning("⚠️ Could not validate cookies file format")
                
                # Update progress
                progress_bar.progress(25)
                status_placeholder.info("📋 Extracting video information...")
                time.sleep(0.5)
                
                progress_bar.progress(50)
                status_placeholder.info("⬇️ Downloading audio...")
                time.sleep(0.5)
                
                # Create temporary directory
                temp_dir = tempfile.mkdtemp()
                result = download_video_as_mp3(url, temp_dir, cookies_path)
                
                progress_bar.progress(75)
                status_placeholder.info("🎵 Converting to MP3...")
                time.sleep(0.5)
                
                progress_bar.progress(100)
                
                if result['success']:
                    status_placeholder.success("✅ Conversion completed successfully!")
                    
                    # Show success animation
                    st.balloons()
                    
                    # Display file info
                    st.success(f"**Title:** {result['title']}")
                    if result['duration']:
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
                    else:
                        st.error("File was converted but could not be found for download")
                        
                else:
                    status_placeholder.error(f"❌ Conversion failed: {result['error']}")
                    
            except Exception as e:
                status_placeholder.error(f"❌ Unexpected error: {str(e)}")
            
            finally:
                # Clear progress after delay
                time.sleep(2)
                progress_placeholder.empty()
    
    with col2:
        # Instructions
        st.markdown("### 📖 How to use:")
        st.markdown("""
        1. **Copy** a video URL
        2. **Paste** it in the input field  
        3. **Click** Convert to MP3
        4. **Wait** for processing
        5. **Download** your MP3 file
        """)
        
        st.markdown("### ✨ Features:")
        st.markdown("""
        - 🎵 High quality MP3 (320kbps)
        - 🚀 Fast conversion
        - 📱 Works on any device
        - 🔒 Privacy focused
        - 📹 YouTube & MP4 support
        """)
        
        st.markdown("### 🎯 Supported:")
        st.markdown("""
        - **YouTube videos**
        - **Direct MP4 URLs**
        - **Most video formats**
        """)
        
        st.markdown("### 🔒 Privacy:")
        st.markdown("""
        - No files stored permanently
        - Temporary processing only
        - Your downloads stay private
        """)
        
        st.markdown("### ⚠️ Important Notes:")
        st.markdown("""
        - Works best with public videos
        - Some videos may be geo-restricted
        - Age-restricted content may fail
        - Try direct MP4 URLs if YouTube fails
        """)
        
        st.markdown("### 🍪 For Restricted Content:")
        st.markdown("""
        **If you get bot detection or login errors:**
        1. **Export cookies** from your browser:
           - Chrome: Use "Get cookies.txt LOCALLY" extension
           - Firefox: Use "cookies.txt" extension
        2. **Upload the cookies.txt file** in the advanced section
        3. **Try the conversion again**
        
        **Cookie file format:**
        - Must start with `# HTTP Cookie File`
        - Must be in Netscape/Mozilla format
        - Contains your login session data
        """)
        
        st.markdown("### 💡 Tips:")
        st.markdown("""
        - **Public videos**: No cookies needed
        - **Age-restricted**: Cookies required
        - **Private videos**: Must be logged in
        - **Geo-blocked**: Use VPN + cookies
        - **Bot detection**: Wait 15 mins, try again
        """)

if __name__ == "__main__":
    main()