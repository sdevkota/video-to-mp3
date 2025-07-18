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

def download_video_as_mp3(url, output_dir):
    """Download video as MP3"""
    try:
        # Configure yt-dlp options
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
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # Download and convert
            ydl.download([url])
            
            # Find the downloaded MP3 file
            safe_title = sanitize_filename(title)
            mp3_file = None
            for file in os.listdir(output_dir):
                if file.endswith('.mp3') and safe_title[:20] in file:
                    mp3_file = os.path.join(output_dir, file)
                    break
            
            return {
                'success': True,
                'title': title,
                'duration': duration,
                'file_path': mp3_file,
                'filename': os.path.basename(mp3_file) if mp3_file else None
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
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
                # Update progress
                progress_bar.progress(25)
                status_placeholder.info("📋 Extracting video information...")
                time.sleep(0.5)
                
                progress_bar.progress(50)
                status_placeholder.info("⬇️ Downloading audio...")
                time.sleep(0.5)
                
                # Create temporary directory
                temp_dir = tempfile.mkdtemp()
                result = download_video_as_mp3(url, temp_dir)
                
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

if __name__ == "__main__":
    main()
