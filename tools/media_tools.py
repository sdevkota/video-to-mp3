import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import json

from utils.file_utils import sanitize_filename, get_file_info, check_file_format
from utils.ffmped_utils import extract_audio_from_video, compress_video, analyze_media
from config import SUPPORTED_FORMATS, QUALITY_PRESETS, MIME_TYPES

def render_page():
    """Render the media tools page"""
    
    st.title("🛠️ Media Tools")
    st.markdown("Advanced media processing tools and utilities")
    
    # Tool selection
    tool = st.sidebar.selectbox(
        "Select Tool",
        ["🎵 Audio Extraction", "📹 Video Compression", "📊 Media Analysis", "✂️ Media Trimming", "🔄 Format Detection"]
    )
    
    if tool == "🎵 Audio Extraction":
        render_audio_extraction()
    elif tool == "📹 Video Compression":
        render_video_compression()
    elif tool == "📊 Media Analysis":
        render_media_analysis()
    elif tool == "✂️ Media Trimming":
        render_media_trimming()
    elif tool == "🔄 Format Detection":
        render_format_detection()

def render_audio_extraction():
    """Render audio extraction tool"""
    st.subheader("🎵 Extract Audio from Video")
    st.markdown("Extract audio tracks from video files")
    
    # Initialize variables
    submitted = False
    uploaded_file = None
    
    with st.form("audio_extraction_form"):
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=SUPPORTED_FORMATS["video_input"],
            help="Select a video file to extract audio from"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                audio_format = st.selectbox(
                    "Audio Format",
                    SUPPORTED_FORMATS["audio_output"],
                    index=0
                )
                
                quality = st.selectbox(
                    "Audio Quality",
                    list(QUALITY_PRESETS["audio"].keys()),
                    index=1
                )
            
            with col2:
                sample_rate = st.selectbox(
                    "Sample Rate",
                    ["44100", "48000", "22050", "16000"],
                    index=0
                )
                
                channels = st.selectbox(
                    "Channels",
                    ["2 (Stereo)", "1 (Mono)"],
                    index=0
                )
            
            submitted = st.form_submit_button("🎵 Extract Audio")
    
    # Process form submission
    if submitted and uploaded_file is not None:
        try:
            with st.spinner("🎵 Extracting audio..."):
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    input_path = tmp_file.name
                
                # Prepare output filename
                base_name = os.path.splitext(uploaded_file.name)[0]
                output_filename = f"{base_name}_audio.{audio_format}"
                output_filename = sanitize_filename(output_filename)
                
                # Create output directory
                output_dir = Path("downloads")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / output_filename
                
                # Extract audio
                success = extract_audio_from_video(
                    input_path=input_path,
                    output_path=str(output_path),
                    audio_format=audio_format,
                    quality=QUALITY_PRESETS["audio"][quality],
                    sample_rate=int(sample_rate),
                    channels=1 if channels.startswith("1") else 2
                )
                
                # Clean up input file
                try:
                    os.unlink(input_path)
                except:
                    pass
                
                if success and output_path.exists():
                    st.success("✅ Audio extraction completed successfully!")
                    
                    # Get file info
                    file_info = get_file_info(str(output_path))
                    if file_info:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("File Size", f"{file_info['file_size_mb']:.1f} MB")
                        with col2:
                            st.metric("Duration", f"{file_info['duration_min']:.1f} min")
                    
                    # Download button
                    with open(output_path, 'rb') as f:
                        file_data = f.read()
                    
                    st.download_button(
                        label="📥 Download Extracted Audio",
                        data=file_data,
                        file_name=output_filename
                    )
                    
                    # Audio preview
                    st.subheader("🎧 Audio Preview")
                    st.audio(file_data, format=f"audio/{audio_format}")
                    
                else:
                    st.error("❌ Audio extraction failed. Please check the file and try again.")
                    
        except Exception as e:
            st.error(f"❌ Error during extraction: {str(e)}")
            st.exception(e)
    
    elif submitted:
        st.warning("⚠️ Please upload a video file first")

def render_video_compression():
    """Render video compression tool"""
    st.subheader("📹 Video Compression")
    st.markdown("Compress video files to reduce size while maintaining quality")
    
    # Initialize variables
    submitted = False
    uploaded_file = None
    
    with st.form("compression_form"):
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=SUPPORTED_FORMATS["video_input"],
            help="Select a video file to compress"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                compression_level = st.selectbox(
                    "Compression Level",
                    list(QUALITY_PRESETS["compression"].keys()),
                    index=1,
                    help="Higher compression = smaller file but lower quality"
                )
                
                output_format = st.selectbox(
                    "Output Format",
                    ["mp4", "mkv", "webm"],
                    index=0
                )
            
            with col2:
                target_size = st.number_input(
                    "Target Size (MB)",
                    min_value=1,
                    max_value=1000,
                    value=100,
                    help="Approximate target file size"
                )
                
                maintain_quality = st.checkbox(
                    "Maintain Quality",
                    value=False,
                    help="Prioritize quality over file size"
                )
            
            submitted = st.form_submit_button("📹 Compress Video")
    
    # Process form submission
    if submitted and uploaded_file is not None:
        try:
            with st.spinner("📹 Compressing video..."):
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    input_path = tmp_file.name
                
                # Prepare output filename
                base_name = os.path.splitext(uploaded_file.name)[0]
                output_filename = f"{base_name}_compressed.{output_format}"
                output_filename = sanitize_filename(output_filename)
                
                # Create output directory
                output_dir = Path("downloads")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / output_filename
                
                # Get compression settings
                compression_settings = QUALITY_PRESETS["compression"][compression_level]
                
                # Compress video
                success = compress_video(
                    input_path=input_path,
                    output_path=str(output_path),
                    output_format=output_format,
                    crf=compression_settings["crf"],
                    preset=compression_settings["preset"],
                    target_size_mb=target_size,
                    maintain_quality=maintain_quality
                )
                
                # Clean up input file
                try:
                    os.unlink(input_path)
                except:
                    pass
                
                if success and output_path.exists():
                    st.success("✅ Video compression completed successfully!")
                    
                    # Get file info
                    original_size = uploaded_file.size / (1024*1024)
                    compressed_info = get_file_info(str(output_path))
                    
                    if compressed_info:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Original Size", f"{original_size:.1f} MB")
                        with col2:
                            st.metric("Compressed Size", f"{compressed_info['file_size_mb']:.1f} MB")
                        with col3:
                            compression_ratio = ((original_size - compressed_info['file_size_mb']) / original_size) * 100
                            st.metric("Size Reduction", f"{compression_ratio:.1f}%")
                    
                    # Download button
                    with open(output_path, 'rb') as f:
                        file_data = f.read()
                    
                    st.download_button(
                        label="📥 Download Compressed Video",
                        data=file_data,
                        file_name=output_filename
                    )
                    
                    # Video preview
                    st.subheader("🎬 Compressed Video Preview")
                    st.video(file_data)
                    
                else:
                    st.error("❌ Video compression failed. Please check the file and try again.")
                    
        except Exception as e:
            st.error(f"❌ Error during compression: {str(e)}")
            st.exception(e)
    
    elif submitted:
        st.warning("⚠️ Please upload a video file first")

def render_media_analysis():
    """Render media analysis tool"""
    st.subheader("📊 Media Analysis")
    st.markdown("Analyze media files for detailed information")
    
    with st.form("analysis_form"):
        uploaded_file = st.file_uploader(
            "Choose a media file",
            type=SUPPORTED_FORMATS["audio_input"] + SUPPORTED_FORMATS["video_input"],
            help="Select any media file to analyze"
        )
        
        if uploaded_file is not None:
            analysis_type = st.selectbox(
                "Analysis Type",
                ["Basic Info", "Detailed Analysis", "Codec Information", "Stream Analysis"],
                index=0
            )
            
            submitted = st.form_submit_button("📊 Analyze Media")
    
    if submitted and uploaded_file is not None:
        try:
            with st.spinner("📊 Analyzing media file..."):
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    input_path = tmp_file.name
                
                # Analyze media
                analysis_result = analyze_media(input_path, analysis_type)
                
                # Clean up input file
                try:
                    os.unlink(input_path)
                except:
                    pass
                
                if analysis_result:
                    st.success("✅ Media analysis completed!")
                    
                    # Display results
                    if analysis_type == "Basic Info":
                        display_basic_info(analysis_result)
                    elif analysis_type == "Detailed Analysis":
                        display_detailed_analysis(analysis_result)
                    elif analysis_type == "Codec Information":
                        display_codec_info(analysis_result)
                    elif analysis_type == "Stream Analysis":
                        display_stream_analysis(analysis_result)
                    
                    # Download analysis report
                    report_json = json.dumps(analysis_result, indent=2)
                    st.download_button(
                        label="📥 Download Analysis Report (JSON)",
                        data=report_json,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_analysis.json",
                        mime_type="application/json"
                    )
                    
                else:
                    st.error("❌ Media analysis failed. Please check the file and try again.")
                    
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.exception(e)
    
    elif submitted:
        st.warning("⚠️ Please upload a media file first")

def render_media_trimming():
    """Render media trimming tool"""
    st.subheader("✂️ Media Trimming")
    st.markdown("Trim audio and video files to specific time ranges")
    
    with st.form("trimming_form"):
        uploaded_file = st.file_uploader(
            "Choose a media file",
            type=SUPPORTED_FORMATS["audio_input"] + SUPPORTED_FORMATS["video_input"],
            help="Select any media file to trim"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.text_input(
                    "Start Time (HH:MM:SS)",
                    placeholder="00:00:00",
                    help="Start time for trimming"
                )
                
                end_time = st.text_input(
                    "End Time (HH:MM:SS)",
                    placeholder="00:00:00",
                    help="End time for trimming"
                )
            
            with col2:
                output_format = st.selectbox(
                    "Output Format",
                    ["Original", "mp3", "mp4", "wav"],
                    index=0,
                    help="Output format (Original keeps input format)"
                )
                
                fade_in = st.number_input(
                    "Fade In (seconds)",
                    min_value=0.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.1
                )
                
                fade_out = st.number_input(
                    "Fade Out (seconds)",
                    min_value=0.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.1
                )
            
            submitted = st.form_submit_button("✂️ Trim Media")
    
    if submitted and uploaded_file is not None:
        st.info("🔄 Media trimming functionality will be implemented in the next version")
        st.markdown("This feature will allow you to trim audio and video files to specific time ranges with fade effects.")

def render_format_detection():
    """Render format detection tool"""
    st.subheader("🔄 Format Detection")
    st.markdown("Detect and analyze media file formats")
    
    with st.form("detection_form"):
        uploaded_file = st.file_uploader(
            "Choose a media file",
            type=["*"],
            help="Select any file to detect its format"
        )
        
        if uploaded_file is not None:
            submitted = st.form_submit_button("🔄 Detect Format")
    
    if submitted and uploaded_file is not None:
        try:
            with st.spinner("🔄 Detecting file format..."):
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    input_path = tmp_file.name
                
                # Detect format
                file_info = get_file_info(input_path)
                
                # Clean up input file
                try:
                    os.unlink(input_path)
                except:
                    pass
                
                if file_info:
                    st.success("✅ Format detection completed!")
                    
                    # Display format information
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("File Type", file_info.get('format_name', 'Unknown').upper())
                        st.metric("File Size", f"{file_info.get('file_size_mb', 0):.1f} MB")
                        st.metric("Duration", f"{file_info.get('duration_min', 0):.1f} min")
                    
                    with col2:
                        st.metric("Has Video", "Yes" if file_info.get('has_video', False) else "No")
                        st.metric("Has Audio", "Yes" if file_info.get('has_audio', False) else "No")
                        st.metric("Bitrate", f"{file_info.get('bitrate_kbps', 0):.0f} kbps")
                    
                    # Detailed format info
                    st.subheader("📋 Detailed Format Information")
                    st.json(file_info)
                    
                else:
                    st.error("❌ Format detection failed. Please check the file and try again.")
                    
        except Exception as e:
            st.error(f"❌ Error during format detection: {str(e)}")
            st.exception(e)
    
    elif submitted:
        st.warning("⚠️ Please upload a file first")

def display_basic_info(info):
    """Display basic media information"""
    st.subheader("📋 Basic Information")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Format", info.get('format_name', 'Unknown'))
        st.metric("Duration", f"{info.get('duration_min', 0):.1f} min")
    with col2:
        st.metric("File Size", f"{info.get('file_size_mb', 0):.1f} MB")
        st.metric("Bitrate", f"{info.get('bitrate_kbps', 0):.0f} kbps")
    with col3:
        st.metric("Video Streams", info.get('video_streams_count', 0))
        st.metric("Audio Streams", info.get('audio_streams_count', 0))

def display_detailed_analysis(info):
    """Display detailed media analysis"""
    st.subheader("🔍 Detailed Analysis")
    
    # Video information
    if info.get('has_video'):
        st.markdown("### 🎬 Video Information")
        video_info = info.get('video_info', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Resolution", f"{video_info.get('width', 0)}x{video_info.get('height', 0)}")
            st.metric("Frame Rate", f"{video_info.get('fps', 0):.2f} fps")
        with col2:
            st.metric("Codec", video_info.get('codec_name', 'Unknown'))
            st.metric("Bitrate", f"{video_info.get('bitrate_kbps', 0):.0f} kbps")
        with col3:
            st.metric("Color Space", video_info.get('color_space', 'Unknown'))
            st.metric("Aspect Ratio", video_info.get('aspect_ratio', 'Unknown'))
    
    # Audio information
    if info.get('has_audio'):
        st.markdown("### 🎵 Audio Information")
        audio_info = info.get('audio_info', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Codec", audio_info.get('codec_name', 'Unknown'))
            st.metric("Sample Rate", f"{audio_info.get('sample_rate', 0)} Hz")
        with col2:
            st.metric("Channels", audio_info.get('channels', 0))
            st.metric("Bitrate", f"{audio_info.get('bitrate_kbps', 0):.0f} kbps")
        with col3:
            st.metric("Language", audio_info.get('language', 'Unknown'))
            st.metric("Duration", f"{audio_info.get('duration_sec', 0):.1f} sec")

def display_codec_info(info):
    """Display codec information"""
    st.subheader("🔧 Codec Information")
    
    # Video codecs
    if info.get('has_video'):
        st.markdown("### 🎬 Video Codecs")
        video_streams = info.get('video_streams', [])
        
        for i, stream in enumerate(video_streams):
            with st.expander(f"Video Stream {i+1}"):
                st.json(stream)
    
    # Audio codecs
    if info.get('has_audio'):
        st.markdown("### 🎵 Audio Codecs")
        audio_streams = info.get('audio_streams', [])
        
        for i, stream in enumerate(audio_streams):
            with st.expander(f"Audio Stream {i+1}"):
                st.json(stream)

def display_stream_analysis(info):
    """Display stream analysis"""
    st.subheader("📊 Stream Analysis")
    
    # Stream overview
    st.markdown("### 📋 Stream Overview")
    
    total_streams = len(info.get('streams', []))
    video_streams = len([s for s in info.get('streams', []) if s.get('codec_type') == 'video'])
    audio_streams = len([s for s in info.get('streams', []) if s.get('codec_type') == 'audio'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Streams", total_streams)
    with col2:
        st.metric("Video Streams", video_streams)
    with col3:
        st.metric("Audio Streams", audio_streams)
    
    # Individual stream details
    st.markdown("### 🔍 Stream Details")
    streams = info.get('streams', [])
    
    for i, stream in enumerate(streams):
        stream_type = stream.get('codec_type', 'unknown')
        codec_name = stream.get('codec_name', 'Unknown')
        
        with st.expander(f"{stream_type.title()} Stream {i+1} - {codec_name}"):
            st.json(stream) 