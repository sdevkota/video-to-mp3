import streamlit as st
import os
import tempfile
from pathlib import Path
import yt_dlp
from typing import Dict, Any, Optional

from utils.youtube_utils import download_youtube_audio, download_youtube_video
from utils.file_utils import sanitize_filename, get_file_info
from config import SUPPORTED_FORMATS, YT_DLP_OPTIONS, QUALITY_PRESETS

def render_page():
    """Render the YouTube converter page"""
    
    st.title("🎥 YouTube Converter")
    st.markdown("Download and convert YouTube videos to various formats")
    
    # Input section
    with st.form("youtube_form"):
        st.subheader("📺 Video Information")
        
        # URL input
        url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste the YouTube video URL here"
        )
        
        # Format selection
        col1, col2 = st.columns(2)
        
        with col1:
            conversion_type = st.selectbox(
                "Conversion Type",
                ["Audio Only", "Video Only", "Both"],
                help="Choose what to download and convert"
            )
        
        with col2:
            if conversion_type == "Audio Only":
                output_format = st.selectbox(
                    "Audio Format",
                    SUPPORTED_FORMATS["audio_output"],
                    index=0,
                    help="Select output audio format"
                )
            elif conversion_type == "Video Only":
                output_format = st.selectbox(
                    "Video Format",
                    SUPPORTED_FORMATS["video_output"],
                    index=0,
                    help="Select output video format"
                )
            else:
                output_format = "mp4"
        
        # Quality selection
        if conversion_type == "Audio Only":
            quality = st.selectbox(
                "Audio Quality",
                list(QUALITY_PRESETS["audio"].keys()),
                index=1,
                help="Select audio quality preset"
            )
        elif conversion_type == "Video Only":
            quality = st.selectbox(
                "Video Quality",
                list(QUALITY_PRESETS["video"].keys()),
                index=2,
                help="Select video quality preset"
            )
        else:
            quality = "medium"
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.text_input(
                    "Start Time (HH:MM:SS)",
                    placeholder="00:00:00",
                    help="Start time for trimming (optional)"
                )
                
                end_time = st.text_input(
                    "End Time (HH:MM:SS)",
                    placeholder="00:00:00", 
                    help="End time for trimming (optional)"
                )
            
            with col2:
                extract_audio = st.checkbox(
                    "Extract Audio Track",
                    value=True,
                    help="Extract audio from video"
                )
                
                keep_original = st.checkbox(
                    "Keep Original",
                    value=False,
                    help="Keep original downloaded file"
                )
        
        submitted = st.form_submit_button("🚀 Download & Convert")
    
    if submitted and url:
        if not url.strip():
            st.error("Please enter a valid YouTube URL")
            return
        
        try:
            with st.spinner("🔍 Analyzing video..."):
                # Get video info first
                ydl_opts = YT_DLP_OPTIONS["base"].copy()
                ydl_opts.update({
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True
                })
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                        video_title = info.get('title', 'Unknown Title')
                        duration = info.get('duration', 0)
                        uploader = info.get('uploader', 'Unknown')
                        
                        st.success(f"✅ Video found: {video_title}")
                        
                        # Display video info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Title", video_title[:30] + "..." if len(video_title) > 30 else video_title)
                        with col2:
                            st.metric("Duration", f"{duration//60}:{duration%60:02d}" if duration else "Unknown")
                        with col3:
                            st.metric("Uploader", uploader[:20] + "..." if len(uploader) > 20 else uploader)
                        
                    except Exception as e:
                        st.error(f"❌ Error extracting video info: {str(e)}")
                        return
            
            # Download and convert
            with st.spinner("📥 Downloading and converting..."):
                try:
                    if conversion_type == "Audio Only":
                        output_file = download_youtube_audio(
                            url, 
                            output_format, 
                            QUALITY_PRESETS["audio"][quality],
                            start_time=start_time if start_time else None,
                            end_time=end_time if end_time else None
                        )
                    elif conversion_type == "Video Only":
                        output_file = download_youtube_video(
                            url,
                            output_format,
                            QUALITY_PRESETS["video"][quality],
                            start_time=start_time if start_time else None,
                            end_time=end_time if end_time else None
                        )
                    else:  # Both
                        audio_file = download_youtube_audio(
                            url,
                            "mp3",
                            QUALITY_PRESETS["audio"]["medium"],
                            start_time=start_time if start_time else None,
                            end_time=end_time if end_time else None
                        )
                        video_file = download_youtube_video(
                            url,
                            "mp4",
                            QUALITY_PRESETS["video"]["medium"],
                            start_time=start_time if start_time else None,
                            end_time=end_time if end_time else None
                        )
                        output_file = video_file
                    
                    if output_file and os.path.exists(output_file):
                        st.success("✅ Conversion completed successfully!")
                        
                        # Get file info
                        file_info = get_file_info(output_file)
                        if file_info:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("File Size", f"{file_info['file_size_mb']:.1f} MB")
                            with col2:
                                st.metric("Duration", f"{file_info['duration_min']:.1f} min")
                        
                        # Download button
                        with open(output_file, 'rb') as f:
                            file_data = f.read()
                        
                        filename = os.path.basename(output_file)
                        st.download_button(
                            label="📥 Download File",
                            data=file_data,
                            file_name=filename
                        )
                        
                        # Clean up if not keeping original
                        if not keep_original:
                            try:
                                os.remove(output_file)
                                st.info("🗑️ Temporary file cleaned up")
                            except:
                                pass
                    else:
                        st.error("❌ Conversion failed. Please check the URL and try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during conversion: {str(e)}")
                    st.exception(e)
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
    
    elif submitted:
        st.warning("⚠️ Please enter a YouTube URL")
    
    # Help section
    with st.expander("❓ How to use"):
        st.markdown("""
        ### Steps to convert YouTube videos:
        
        1. **Copy the URL** from any YouTube video
        2. **Paste it** in the input field above
        3. **Choose format** (Audio/Video/Both)
        4. **Select quality** based on your needs
        5. **Click Download** to start conversion
        
        ### Supported formats:
        - **Audio:** MP3, WAV, FLAC, AAC, OGG
        - **Video:** MP4, AVI, MKV, WEBM, MOV
        
        ### Tips:
        - Use start/end time to trim videos
        - Higher quality = larger file size
        - Audio-only is faster and smaller
        """)
    
    # Legal notice
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        ⚠️ <strong>Legal Notice:</strong> Only download content you own or have permission to download. 
        Respect copyright laws and YouTube's Terms of Service.
    </div>
    """, unsafe_allow_html=True) 