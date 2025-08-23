import streamlit as st
import os
from pathlib import Path

# Import our modules
from utils.file_utils import check_ffmpeg
from pages import youtube_converter, audio_converter, video_converter, media_tools
from config import APP_CONFIG

def main():
    """Main application entry point"""
    
    # Configure Streamlit
    st.set_page_config(
        page_title=APP_CONFIG["page_title"],
        page_icon=APP_CONFIG["page_icon"],
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        background: #f8f9fa;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🎵 Complete Media Converter Suite</h1>
        <p>Convert videos, extract audio, and transform media files with ease</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check FFmpeg availability
    ffmpeg_available = check_ffmpeg()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎛️ Navigation")
        
        # FFmpeg status
        if ffmpeg_available:
            st.markdown('<p class="status-success">✅ FFmpeg Available</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ FFmpeg Not Found</p>', unsafe_allow_html=True)
            st.error("FFmpeg is required for conversions. Please install FFmpeg to use this application.")
        
        st.markdown("---")
        
        # Navigation menu
        pages = {
            "🎥 YouTube Converter": "youtube",
            "🎵 Audio Converter": "audio",
            "🎬 Video Converter": "video", 
            "🛠️ Media Tools": "tools"
        }
        
        selected_page = st.radio("Select Tool:", list(pages.keys()))
        page_key = pages[selected_page]
        
        st.markdown("---")
        
        # App info
        st.markdown("### 📋 Features")
        st.markdown("""
        - **YouTube to MP3** - Download & convert
        - **Audio Converter** - Multiple formats
        - **Video Converter** - High quality output
        - **Media Tools** - Extract, compress, analyze
        """)
        
        st.markdown("### 🔧 Supported Formats")
        st.markdown("""
        **Audio:** MP3, WAV, FLAC, AAC, OGG
        **Video:** MP4, AVI, MKV, WEBM, MOV
        **Input:** Most common media formats
        """)
        
        st.markdown("---")
        st.markdown("*Built with Streamlit & FFmpeg*")
    
    # Main content area
    if not ffmpeg_available:
        st.error("🚫 FFmpeg is required but not found. Please install FFmpeg to use this application.")
        st.markdown("""
        ### How to install FFmpeg:
        
        **Windows:**
        1. Download from https://ffmpeg.org/download.html
        2. Extract and add to PATH
        
        **Mac:**
        ```bash
        brew install ffmpeg
        ```
        
        **Linux (Ubuntu/Debian):**
        ```bash
        sudo apt update
        sudo apt install ffmpeg
        ```
        """)
        return
    
    # Route to selected page
    if page_key == "youtube":
        youtube_converter.render_page()
    elif page_key == "audio":
        audio_converter.render_page()
    elif page_key == "video":
        video_converter.render_page()
    elif page_key == "tools":
        media_tools.render_page()

if __name__ == "__main__":
    main()