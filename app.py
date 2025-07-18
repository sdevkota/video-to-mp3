import streamlit as st
import os
import tempfile
import shutil
from main import download_video_as_mp3, get_video_info
import time

# Configure Streamlit page
st.set_page_config(
    page_title="NMG Video to Mp3",
    page_icon="🎵",
    layout="wide"
)

# Add SEO meta tags
st.markdown("""
<head>
    <meta property="og:title" content="NMG Video to Mp3">
    <meta property="og:description" content="Convert YouTube videos and MP4 files to high-quality MP3 files - Built by Nepal Media Group">
    <meta property="og:type" content="website">
    <meta name="description" content="Convert YouTube videos and MP4 files to high-quality MP3 files - Built by Nepal Media Group">
    <meta name="keywords" content="video to mp3, youtube converter, mp3 converter, nepal media group, nmg">
</head>
""", unsafe_allow_html=True)

def format_duration(seconds):
    """Format duration from seconds to MM:SS"""
    if not seconds:
        return "Unknown"
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def format_view_count(count):
    """Format view count with K, M notation"""
    if not count:
        return "Unknown"
    if count >= 1000000:
        return f"{count/1000000:.1f}M"
    elif count >= 1000:
        return f"{count/1000:.1f}K"
    else:
        return str(count)

def main():
    # Header with branding
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: bold;">🎵 Video to MP3 Converter</h1>
        <p style="color: white; margin: 10px 0 0 0; font-size: 1.2em;">Convert YouTube videos and MP4 files to high-quality MP3 files</p>
        <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 0.9em; font-style: italic;">Built By Nepal Media Group</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # URL input
        url = st.text_input(
            "Enter Video URL:",
            placeholder="https://www.youtube.com/watch?v=... or https://example.com/video.mp4",
            help="Paste a YouTube video URL or direct MP4 file URL here"
        )
        
        # Preview button
        if url and st.button("📋 Preview Video Info", use_container_width=True):
            with st.spinner("Fetching video information..."):
                info = get_video_info(url)
                
                if info['success']:
                    st.success("Video found!")
                    
                    # Display video info
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.write("**Title:**", info['title'])
                        st.write("**Duration:**", format_duration(info['duration']))
                    
                    with col_info2:
                        st.write("**Uploader:**", info['uploader'])
                        st.write("**Views:**", format_view_count(info['view_count']))
                    
                    # Show thumbnail if available
                    if info['thumbnail']:
                        st.image(info['thumbnail'], caption="Video Thumbnail", width=300)
                else:
                    st.error(f"Failed to fetch video info: {info['error']}")
        
        # Download section
        st.markdown("---")
        
        # Download button
        if url and st.button("🎵 Convert & Download MP3", type="primary", use_container_width=True):
            if not url.strip():
                st.error("Please enter a valid video URL")
                return
            
            # Create progress placeholder
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            with status_placeholder:
                st.info("Starting conversion...")
            
            with progress_placeholder:
                progress_bar = st.progress(0)
                
            try:
                # Update progress
                progress_bar.progress(25)
                status_placeholder.info("Extracting video information...")
                time.sleep(0.5)
                
                progress_bar.progress(50)
                status_placeholder.info("Downloading audio...")
                time.sleep(0.5)
                
                # Start download with temporary directory
                temp_dir = tempfile.mkdtemp()
                result = download_video_as_mp3(url, temp_dir)
                
                progress_bar.progress(75)
                status_placeholder.info("Converting to MP3...")
                time.sleep(0.5)
                
                progress_bar.progress(100)
                
                if result['success']:
                    status_placeholder.success(result['message'])
                    
                    # Show download info
                    st.balloons()
                    
                    # Read the MP3 file for download
                    with open(result['file_path'], 'rb') as file:
                        file_data = file.read()
                    
                    file_size = len(file_data)
                    st.write(f"**File ready:** {result['filename']} ({file_size // 1024} KB)")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download MP3 File",
                        data=file_data,
                        file_name=result['filename'],
                        mime="audio/mpeg",
                        use_container_width=True
                    )
                    
                    # Clean up temporary files after a delay
                    @st.cache_data
                    def cleanup_temp_dir(temp_path):
                        try:
                            shutil.rmtree(temp_path)
                        except:
                            pass
                    
                    # Schedule cleanup (will happen when user navigates away or after cache expires)
                    cleanup_temp_dir(temp_dir)
                    
                else:
                    status_placeholder.error(result['message'])
                    # Clean up on failure
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass
                    
            except Exception as e:
                status_placeholder.error(f"Unexpected error: {str(e)}")
                # Clean up on error
                try:
                    if 'temp_dir' in locals():
                        shutil.rmtree(temp_dir)
                except:
                    pass
            finally:
                # Clear progress bar after a delay
                time.sleep(2)
                progress_placeholder.empty()
    
    with col2:
        # Instructions
        st.markdown("### 📖 How to use:")
        st.markdown("""
        1. **Copy** a video URL (YouTube or MP4)
        2. **Paste** it in the input field
        3. **Preview** video info (optional)
        4. **Click** Convert to MP3
        5. **Wait** for the download to complete
        """)
        
        st.markdown("### ✨ Features:")
        st.markdown("""
        - 🎵 High quality MP3 (320kbps)
        - 🚀 Fast conversion
        - 📱 Simple interface
        - 🔒 Privacy focused
        - 💾 Local processing
        - 📹 YouTube & MP4 support
        """)
        
        st.markdown("### 📱 Mobile Friendly:")
        st.markdown("""
        - Works on phones & tablets
        - Direct download to device
        - No file management needed
        """)
        
        st.markdown("### 🔒 Privacy:")
        st.markdown("""
        - No files stored on server
        - Temporary processing only
        - Your downloads stay private
        """)

if __name__ == "__main__":
    main()
