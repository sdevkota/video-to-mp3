import streamlit as st
import os
from pathlib import Path

# Import our modules
from utils.file_utils import check_ffmpeg
from tools import youtube_converter, audio_converter, video_converter, media_tools

APP_CONFIG = {
    "page_title": "🎵 Complete Media Converter Suite",
    "page_icon": "🎵",
}

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
    .tool-card {
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: transform 0.2s;
    }
    .tool-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .get-started-btn {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        text-decoration: none;
        display: inline-block;
        margin: 1rem 0;
        font-weight: bold;
        transition: all 0.3s;
    }
    .get-started-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check FFmpeg availability
    ffmpeg_available = check_ffmpeg()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎛️ Navigation")
        
        
        # Navigation menu
        pages = {
            "🏠 Home": "home",
            "🎥 YouTube Converter": "youtube",
            "🎵 Audio Converter": "audio",
            "🎬 Video Converter": "video", 
            "🛠️ Media Tools": "tools",
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
        st.markdown("*Built with Love by Nepal Media Group - For internal use only*")
    
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
    if page_key == "home":
        # Home page content
        st.markdown("""
        <div class="main-header">
            <h1>🎵 Complete Media Converter Suite</h1>
            <p>Convert videos, extract audio, and transform media files with ease</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Welcome section
        st.markdown("## 🚀 Welcome to Your Complete Media Conversion Solution!")
        st.markdown("""
        Transform your media files with our comprehensive suite of conversion tools. 
        Whether you need to convert videos, extract audio, or translate text, we've got you covered!
        """)
        
        # Features overview
        st.markdown("## ✨ What You Can Do")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="tool-card">
                <h3>🎥 YouTube Converter</h3>
                <p>Download YouTube videos and convert them to various audio formats like MP3, WAV, FLAC, and more.</p>
                <ul>
                    <li>High-quality audio extraction</li>
                    <li>Multiple output formats</li>
                    <li>Batch processing support</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="tool-card">
                <h3>🎵 Audio Converter</h3>
                <p>Convert between audio formats with advanced options for quality, sample rate, and effects.</p>
                <ul>
                    <li>Support for MP3, WAV, FLAC, AAC, OGG</li>
                    <li>Audio normalization and effects</li>
                    <li>Batch conversion capabilities</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="tool-card">
                <h3>🎬 Video Converter</h3>
                <p>Convert videos between formats with control over quality, resolution, and codecs.</p>
                <ul>
                    <li>Multiple video formats supported</li>
                    <li>Quality and resolution control</li>
                    <li>Two-pass encoding for best quality</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="tool-card">
                <h3>🛠️ Media Tools</h3>
                <p>Extract audio from videos, compress media files, and analyze media properties.</p>
                <ul>
                    <li>Audio extraction from videos</li>
                    <li>Video compression</li>
                    <li>Media analysis and metadata</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            

            
            st.markdown("""
            <div class="tool-card">
                <h3>📊 Batch Processing</h3>
                <p>Process multiple files at once to save time and effort.</p>
                <ul>
                    <li>Multiple file uploads</li>
                    <li>Consistent settings</li>
                    <li>Progress tracking</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Supported formats
        st.markdown("## 🔧 Supported Formats")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎵 Audio Formats")
            st.markdown("""
            **Input:** MP3, WAV, FLAC, AAC, OGG, M4A, WMA
            **Output:** MP3, WAV, FLAC, AAC, OGG, M4A
            """)
        
        with col2:
            st.markdown("### 🎬 Video Formats")
            st.markdown("""
            **Input:** MP4, AVI, MKV, WEBM, MOV, WMV, FLV
            **Output:** MP4, AVI, MKV, WEBM, MOV
            """)
        
        with col3:
            st.markdown("### 📱 Other Sources")
            st.markdown("""
            **YouTube:** Direct video/audio download
            **URLs:** Remote media files
            **Batch:** Multiple files processing
            """)
        
        # How to use
        st.markdown("## 📖 How to Get Started")
        
        st.markdown("""
        1. **Install FFmpeg** (if not already installed)
        2. **Run the application** using the run script
        3. **Choose your tool** from the available options
        4. **Upload or provide input** (file, URL, or text)
        5. **Configure settings** for your desired output
        6. **Convert and download** your processed files
        """)
        
        # Quick start button
  
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666;">
            <p>Built with ❤️ By Nepal Media Group</p>
            <p>Complete Media Converter Suite - Your all-in-one media solution</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif page_key == "youtube":
        youtube_converter.render_page()
    elif page_key == "audio":
        audio_converter.render_page()
    elif page_key == "video":
        video_converter.render_page()
    elif page_key == "tools":
        media_tools.render_page()

if __name__ == "__main__":
    main()