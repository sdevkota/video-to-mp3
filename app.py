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

def convert_wav_to_mp3(wav_file_path, output_dir, quality='320k'):
    """Convert WAV file to MP3 using FFmpeg with maximum quality"""
    
    if not check_ffmpeg():
        return {
            'success': False,
            'error': "❌ FFmpeg not found. FFmpeg is required for audio conversion. Please install FFmpeg first."
        }
    
    try:
        # Get original filename without extension
        wav_filename = os.path.basename(wav_file_path)
        name_without_ext = os.path.splitext(wav_filename)[0]
        
        # Sanitize filename
        safe_name = sanitize_filename(name_without_ext)
        
        # Create output path
        output_path = os.path.join(output_dir, f"{safe_name}.mp3")
        
        # FFmpeg command for maximum quality conversion
        # Using libmp3lame encoder with highest quality settings
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', wav_file_path,          # Input WAV file
            '-codec:a', 'libmp3lame',     # Use LAME MP3 encoder
            '-b:a', quality,              # Audio bitrate (320k for max quality)
            '-q:a', '0',                  # Highest quality setting (0 is best)
            '-ar', '44100',               # Sample rate 44.1kHz
            '-ac', '2',                   # Stereo channels
            '-y',                         # Overwrite output file if exists
            output_path
        ]
        
        # Run FFmpeg conversion
        result = subprocess.run(
            ffmpeg_cmd, 
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            return {
                'success': False,
                'error': f"❌ FFmpeg conversion failed: {error_msg}"
            }
        
        # Verify output file exists and has content
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {
                'success': False,
                'error': "❌ MP3 file was not created or is empty."
            }
        
        # Get file size for info
        file_size = os.path.getsize(output_path)
        
        return {
            'success': True,
            'output_path': output_path,
            'filename': f"{safe_name}.mp3",
            'file_size': file_size,
            'original_name': wav_filename
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "❌ Conversion timeout. The file may be too large or corrupted."
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"❌ Conversion error: {str(e)}"
        }

def get_audio_info(file_path):
    """Get audio file information using FFprobe"""
    try:
        ffprobe_cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            
            audio_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
            
            if audio_stream:
                duration = float(info.get('format', {}).get('duration', 0))
                sample_rate = audio_stream.get('sample_rate', 'Unknown')
                channels = audio_stream.get('channels', 'Unknown')
                bit_rate = audio_stream.get('bit_rate', 'Unknown')
                
                return {
                    'duration': duration,
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'bit_rate': bit_rate
                }
    except:
        pass
    
    return None

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

def format_file_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

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
        page_title="Audio Converter Pro",
        page_icon="🎵",
        layout="wide"
    )
    
    # Header with branding
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: bold;">🎵 Audio Converter Pro</h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 1.2em;">YouTube to MP3 & WAV to MP3 Converter</p>
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
    
    # Add tabs for different conversion modes
    tab1, tab2 = st.tabs(["🎬 YouTube to MP3", "🎵 WAV to MP3"])
    
    with tab1:
        # Original YouTube to MP3 functionality
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
                    help="Optional: Upload browser cookies to access restricted content",
                    key="youtube_cookies"
                )
            
            # Convert button
            if st.button("🎵 Convert to MP3", type="primary", use_container_width=True, key="youtube_convert"):
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
            # Instructions for YouTube conversion
            st.markdown("### 📖 YouTube to MP3:")
            st.markdown("""
            1. **Copy** a YouTube URL
            2. **Paste** it in the input field  
            3. **Click** Convert to MP3
            4. **Wait** for processing
            5. **Download** your MP3 file
            """)
            
            st.markdown("### 🔧 YouTube Requirements:")
            st.markdown("""
            - **FFmpeg** must be installed
            - **Internet connection**
            - **Valid YouTube URL**
            """)
    
    with tab2:
        # New WAV to MP3 conversion functionality
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎵 WAV to MP3 Converter")
            st.markdown("Convert your WAV files to high-quality MP3 format with maximum audio fidelity.")
            
            # File uploader for WAV files
            uploaded_wav = st.file_uploader(
                "📁 Choose WAV file(s)",
                type=['wav'],
                accept_multiple_files=True,
                help="Upload one or more WAV files to convert to MP3"
            )
            
            # Quality settings
            quality_option = st.selectbox(
                "🎚️ Audio Quality",
                options=['320k', '256k', '192k', '128k'],
                index=0,
                help="Higher bitrate = better quality = larger file size"
            )
            
            quality_info = {
                '320k': "Maximum Quality (Recommended)",
                '256k': "High Quality", 
                '192k': "Good Quality",
                '128k': "Standard Quality"
            }
            st.info(f"**Selected:** {quality_info[quality_option]}")
            
            if uploaded_wav and st.button("🔄 Convert WAV to MP3", type="primary", use_container_width=True, key="wav_convert"):
                # Create temporary directory for processing
                temp_dir = tempfile.mkdtemp()
                
                # Process each uploaded file
                for i, wav_file in enumerate(uploaded_wav):
                    st.markdown(f"---")
                    st.markdown(f"### Processing file {i+1}/{len(uploaded_wav)}: {wav_file.name}")
                    
                    # Create progress indicators
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    with status_placeholder:
                        st.info(f"🔄 Processing {wav_file.name}...")
                    
                    with progress_placeholder:
                        progress_bar = st.progress(0)
                    
                    try:
                        # Save uploaded WAV file temporarily
                        temp_wav_path = os.path.join(temp_dir, f"temp_{i}_{wav_file.name}")
                        with open(temp_wav_path, "wb") as f:
                            f.write(wav_file.getvalue())
                        
                        progress_bar.progress(20)
                        status_placeholder.info("📊 Analyzing audio file...")
                        
                        # Get audio information
                        audio_info = get_audio_info(temp_wav_path)
                        if audio_info:
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.metric("Duration", format_duration(audio_info['duration']))
                                st.metric("Sample Rate", f"{audio_info['sample_rate']} Hz")
                            with col_info2:
                                st.metric("Channels", audio_info['channels'])
                                if audio_info['bit_rate'] != 'Unknown':
                                    st.metric("Original Bitrate", f"{int(audio_info['bit_rate'])//1000}k")
                        
                        progress_bar.progress(50)
                        status_placeholder.info("🎵 Converting to MP3...")
                        
                        # Convert WAV to MP3
                        result = convert_wav_to_mp3(temp_wav_path, temp_dir, quality_option)
                        
                        progress_bar.progress(90)
                        
                        if result['success']:
                            progress_bar.progress(100)
                            status_placeholder.success("✅ Conversion completed!")
                            
                            # Display conversion results
                            col_result1, col_result2 = st.columns(2)
                            with col_result1:
                                st.success(f"**Original:** {result['original_name']}")
                                st.success(f"**Converted:** {result['filename']}")
                            with col_result2:
                                st.info(f"**Quality:** {quality_option} ({quality_info[quality_option]})")
                                st.info(f"**File Size:** {format_file_size(result['file_size'])}")
                            
                            # Read converted file for download
                            if os.path.exists(result['output_path']):
                                with open(result['output_path'], 'rb') as file:
                                    mp3_data = file.read()
                                
                                # Download button for this file
                                st.download_button(
                                    label=f"📥 Download {result['filename']}",
                                    data=mp3_data,
                                    file_name=result['filename'],
                                    mime="audio/mpeg",
                                    use_container_width=True,
                                    key=f"download_{i}"
                                )
                                
                                # Clean up files
                                try:
                                    os.remove(result['output_path'])
                                    os.remove(temp_wav_path)
                                except:
                                    pass
                            else:
                                st.error("❌ Converted file not found")
                        else:
                            status_placeholder.error(result['error'])
                            
                    except Exception as e:
                        status_placeholder.error(f"❌ Error processing {wav_file.name}: {str(e)}")
                    
                    finally:
                        # Clear progress indicators
                        time.sleep(1)
                        progress_placeholder.empty()
                
                # Show completion message
                if len(uploaded_wav) > 1:
                    st.success(f"🎉 All {len(uploaded_wav)} files processed!")
                    st.balloons()
        
        with col2:
            # Instructions for WAV conversion
            st.markdown("### 📖 WAV to MP3:")
            st.markdown("""
            1. **Upload** WAV file(s)
            2. **Select** audio quality
            3. **Click** Convert WAV to MP3
            4. **Wait** for processing
            5. **Download** MP3 file(s)
            """)
            
            st.markdown("### ✨ WAV Features:")
            st.markdown("""
            - 🎵 Maximum quality (up to 320kbps)
            - 📁 Batch processing
            - 📊 Audio analysis
            - 🔧 Quality selection
            - 📱 Any WAV format
            """)
            
            st.markdown("### 🎚️ Quality Guide:")
            st.markdown("""
            - **320k**: CD quality, largest file
            - **256k**: Near-CD quality
            - **192k**: High quality, good balance
            - **128k**: Standard quality, smallest
            """)
            
            st.markdown("### 📝 Supported:")
            st.markdown("""
            - **Input**: WAV files (any sample rate)
            - **Output**: MP3 (LAME encoder)
            - **Channels**: Mono, Stereo, Multi-channel
            - **Sample Rate**: Auto-optimized to 44.1kHz
            """)
    
    # Common sidebar with general info
    with st.sidebar:
        st.markdown("### 🎵 Audio Converter Pro")
        st.markdown("**Two powerful tools in one:**")
        st.markdown("• YouTube to MP3 converter")
        st.markdown("• WAV to MP3 converter")
        
        st.markdown("### 🔧 Requirements:")
        st.markdown("• FFmpeg installed")
        st.markdown("• Internet connection (YouTube)")
        
        st.markdown("### 💡 Pro Tips:")
        st.markdown("• Use 320k for maximum quality")
        st.markdown("• Batch convert multiple WAVs")
        st.markdown("• Use cookies for restricted YouTube videos")
        
        st.markdown("### ⚠️ Troubleshooting:")
        st.markdown("**YouTube issues:**")
        st.markdown("• Upload cookies for age-restricted")
        st.markdown("• Wait if bot detection occurs")
        
        st.markdown("**WAV issues:**")
        st.markdown("• Ensure file is valid WAV format")
        st.markdown("• Check file isn't corrupted")
        st.markdown("• Try lower quality if conversion fails")
        
        st.markdown("---")
        st.markdown("*Built with ❤️ by Nepal Media Group*")

if __name__ == "__main__":
    main()