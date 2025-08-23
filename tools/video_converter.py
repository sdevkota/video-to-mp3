import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from utils.file_utils import sanitize_filename, get_file_info, check_file_format
from utils.ffmped_utils import convert_video
from config import SUPPORTED_FORMATS, QUALITY_PRESETS, MIME_TYPES

def render_page():
    """Render the video converter page"""
    
    st.title("🎬 Video Converter")
    st.markdown("Convert video files between different formats with quality control")
    
    # Initialize variables
    submitted = False
    uploaded_file = None
    batch_submitted = False
    uploaded_files = None
    batch_output_format = "mp4"
    batch_quality = "medium"
    batch_resolution = "Original"
    batch_audio_codec = "aac"
    
    # Always show format information
    st.info("""
    **Supported Input Formats:** MP4, MOV, AVI, MKV, WEBM, FLV, WMV, M4V, 3GP  
    **Supported Output Formats:** MP4, AVI, MKV, WEBM, MOV
    """)
    
    # File upload section
    with st.form("video_form"):
        st.subheader("📁 Upload Video File")
        
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=SUPPORTED_FORMATS["video_input"],
            help="Supported formats: MP4, MOV, AVI, MKV, WEBM, FLV, WMV, M4V, 3GP"
        )
        
        # Always show conversion settings
        st.subheader("⚙️ Conversion Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            output_format = st.selectbox(
                "🎯 Output Format",
                SUPPORTED_FORMATS["video_output"],
                index=0,
                help="Select the desired output format (MP4, AVI, MKV, WEBM, MOV)"
            )
            
            quality = st.selectbox(
                "🎚️ Video Quality",
                list(QUALITY_PRESETS["video"].keys()),
                index=2,
                help="Select video quality preset (Ultrafast: fastest, High: best quality)"
            )
        
        with col2:
            resolution = st.selectbox(
                "📺 Resolution",
                ["Original", "4K (3840x2160)", "2K (2560x1440)", "1080p (1920x1080)", "720p (1280x720)", "480p (854x480)"],
                index=0,
                help="Select output resolution (Original keeps input resolution)"
            )
            
            fps = st.selectbox(
                "🎬 Frame Rate (FPS)",
                ["Original", "60", "30", "25", "24"],
                index=0,
                help="Select output frame rate (Original keeps input frame rate)"
            )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.text_input(
                    "⏱️ Start Time (HH:MM:SS)",
                    placeholder="00:00:00",
                    help="Start time for trimming (format: HH:MM:SS)"
                )
                
                end_time = st.text_input(
                    "⏱️ End Time (HH:MM:SS)",
                    placeholder="00:00:00",
                    help="End time for trimming (format: HH:MM:SS)"
                )
                
                crop_width = st.number_input(
                    "✂️ Crop Width (pixels)",
                    min_value=0,
                    value=0,
                    help="Crop video width in pixels (0 = no crop)"
                )
                
                crop_height = st.number_input(
                    "✂️ Crop Height (pixels)",
                    min_value=0,
                    value=0,
                    help="Crop video height in pixels (0 = no crop)"
                )
            
            with col2:
                audio_codec = st.selectbox(
                    "🎵 Audio Codec",
                    ["aac", "mp3", "copy", "none"],
                    index=0,
                    help="Select audio codec (copy = keep original, none = no audio)"
                )
                
                video_codec = st.selectbox(
                    "🎬 Video Codec",
                    ["libx264", "libx265", "libvpx-vp9", "copy"],
                    index=0,
                    help="Select video codec (copy = keep original)"
                )
                
                two_pass = st.checkbox(
                    "🔄 Two-Pass Encoding",
                    value=False,
                    help="Better quality but slower (H.264/H.265 only)"
                )
                
                deinterlace = st.checkbox(
                    "📺 Deinterlace",
                    value=False,
                    help="Remove interlacing artifacts from interlaced video"
                )
        
        # Show file info if uploaded
        if uploaded_file is not None:
            st.subheader("📋 File Information")
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / (1024*1024):.2f} MB",
                "File type": uploaded_file.type or "Unknown"
            }
            st.json(file_details)
        
        # Submit button - always enabled, validation happens in processing
        submitted = st.form_submit_button("🔄 Convert Video")
    
    # Process form submission
    if submitted:
        if uploaded_file is None:
            st.error("⚠️ Please upload a video file first")
        else:
            try:
                with st.spinner("🔄 Converting video..."):
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        input_path = tmp_file.name
                    
                    # Prepare output filename
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    output_filename = f"{base_name}_converted.{output_format}"
                    output_filename = sanitize_filename(output_filename)
                    
                    # Create output directory
                    output_dir = Path("downloads")
                    output_dir.mkdir(exist_ok=True)
                    output_path = output_dir / output_filename
                    
                    # Parse resolution
                    target_resolution = None
                    if resolution != "Original":
                        if "4K" in resolution:
                            target_resolution = (3840, 2160)
                        elif "2K" in resolution:
                            target_resolution = (2560, 1440)
                        elif "1080p" in resolution:
                            target_resolution = (1920, 1080)
                        elif "720p" in resolution:
                            target_resolution = (1280, 720)
                        elif "480p" in resolution:
                            target_resolution = (854, 480)
                    
                    # Parse frame rate
                    target_fps = None
                    if fps != "Original":
                        target_fps = int(fps)
                    
                    # Parse time inputs
                    start_seconds = None
                    end_seconds = None
                    if start_time and start_time != "00:00:00":
                        try:
                            time_parts = start_time.split(":")
                            start_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                        except:
                            st.warning("Invalid start time format, using 00:00:00")
                    
                    if end_time and end_time != "00:00:00":
                        try:
                            time_parts = end_time.split(":")
                            end_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                        except:
                            st.warning("Invalid end time format, using full duration")
                    
                    # Convert video
                    success = convert_video(
                        input_path=input_path,
                        output_path=str(output_path),
                        output_format=output_format,
                        quality_preset=quality,
                        resolution=target_resolution,
                        fps=target_fps,
                        start_time=start_seconds,
                        end_time=end_seconds,
                        crop_width=crop_width if crop_width > 0 else None,
                        crop_height=crop_height if crop_height > 0 else None,
                        audio_codec=audio_codec,
                        video_codec=video_codec,
                        two_pass=two_pass,
                        deinterlace=deinterlace
                    )
                    
                    # Clean up input file
                    try:
                        os.unlink(input_path)
                    except:
                        pass
                    
                    if success and output_path.exists():
                        st.success("✅ Video conversion completed successfully!")
                        
                        # Get file info
                        file_info = get_file_info(str(output_path))
                        if file_info:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("File Size", f"{file_info['file_size_mb']:.1f} MB")
                            with col2:
                                st.metric("Duration", f"{file_info['duration_min']:.1f} min")
                            with col3:
                                st.metric("Format", output_format.upper())
                        
                        # Download button
                        with open(output_path, 'rb') as f:
                            file_data = f.read()
                        
                        st.download_button(
                            label="📥 Download Converted Video",
                            data=file_data,
                            file_name=output_filename
                        )
                        
                        # Video preview
                        st.subheader("🎬 Video Preview")
                        st.video(file_data)
                        
                    else:
                        st.error("❌ Video conversion failed. Please check the file and try again.")
                        
            except Exception as e:
                st.error(f"❌ Error during conversion: {str(e)}")
                st.exception(e)
    
    # Batch conversion section
    st.markdown("---")
    st.subheader("📦 Batch Conversion")
    
    with st.form("batch_video_form"):
        st.markdown("Convert multiple video files at once")
        
        uploaded_files = st.file_uploader(
            "Choose multiple video files",
            type=SUPPORTED_FORMATS["video_input"],
            accept_multiple_files=True,
            help="Select multiple files for batch conversion"
        )
        
        if uploaded_files:
            col1, col2 = st.columns(2)
            
            with col1:
                batch_output_format = st.selectbox(
                    "Output Format",
                    SUPPORTED_FORMATS["video_output"],
                    index=0,
                    key="batch_video_format"
                )
                
                batch_quality = st.selectbox(
                    "Video Quality",
                    list(QUALITY_PRESETS["video"].keys()),
                    index=2,
                    key="batch_video_quality"
                )
            
            with col2:
                batch_resolution = st.selectbox(
                    "Resolution",
                    ["Original", "1080p (1920x1080)", "720p (1280x720)", "480p (854x480)"],
                    index=0,
                    key="batch_resolution"
                )
                
                batch_audio_codec = st.selectbox(
                    "Audio Codec",
                    ["aac", "mp3", "copy"],
                    index=0,
                    key="batch_audio_codec"
                )
            
            batch_submitted = st.form_submit_button("🔄 Convert All Videos")
    
    # Process batch form submission
    if batch_submitted and uploaded_files:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            converted_files = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Converting {uploaded_file.name}...")
                
                try:
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        input_path = tmp_file.name
                    
                    # Prepare output filename
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    output_filename = f"{base_name}_converted.{batch_output_format}"
                    output_filename = sanitize_filename(output_filename)
                    
                    # Create output directory
                    output_dir = Path("downloads")
                    output_dir.mkdir(exist_ok=True)
                    output_path = output_dir / output_filename
                    
                    # Parse resolution
                    target_resolution = None
                    if batch_resolution != "Original":
                        if "1080p" in batch_resolution:
                            target_resolution = (1920, 1080)
                        elif "720p" in batch_resolution:
                            target_resolution = (1280, 720)
                        elif "480p" in batch_resolution:
                            target_resolution = (854, 480)
                    
                    # Convert video
                    success = convert_video(
                        input_path=input_path,
                        output_path=str(output_path),
                        output_format=batch_output_format,
                        quality_preset=batch_quality,
                        resolution=target_resolution,
                        audio_codec=batch_audio_codec
                    )
                    
                    # Clean up input file
                    try:
                        os.unlink(input_path)
                    except:
                        pass
                    
                    if success and output_path.exists():
                        converted_files.append(str(output_path))
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                except Exception as e:
                    st.error(f"Error converting {uploaded_file.name}: {str(e)}")
            
            status_text.text("Batch conversion completed!")
            
            if converted_files:
                st.success(f"✅ Successfully converted {len(converted_files)} videos!")
                
                # Create zip file for batch download
                import zipfile
                zip_path = output_dir / "converted_video_files.zip"
                
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_path in converted_files:
                        zipf.write(file_path, os.path.basename(file_path))
                
                # Download zip button
                with open(zip_path, 'rb') as f:
                    zip_data = f.read()
                
                st.download_button(
                    label="📦 Download All Converted Videos (ZIP)",
                    data=zip_data,
                    file_name="converted_video_files.zip"
                )
                
                # Clean up zip file
                try:
                    os.unlink(zip_path)
                except:
                    pass
            else:
                st.error("❌ No videos were successfully converted")
                
        except Exception as e:
            st.error(f"❌ Error during batch conversion: {str(e)}")
            st.exception(e)
    
    # Format comparison
    with st.expander("📊 Format Comparison"):
        st.markdown("""
        | Format | Quality | File Size | Compatibility | Best For |
        |--------|---------|-----------|---------------|----------|
        | **MP4** | Excellent | Medium | Universal | General use, streaming |
        | **AVI** | Good | Large | Good | Windows, legacy systems |
        | **MKV** | Excellent | Medium | Limited | High quality, multiple audio tracks |
        | **WEBM** | Very Good | Small | Good | Web, open source |
        | **MOV** | Excellent | Large | Apple devices | Mac, iOS, professional editing |
        
        **💡 Recommendation:** MP4 is best for most uses due to universal compatibility and good quality-to-size ratio.
        """)
    
    # Codec information
    with st.expander("🔧 Codec Information"):
        st.markdown("""
        ### Video Codecs:
        - **H.264 (libx264):** Widely compatible, good quality
        - **H.265 (libx265):** Better compression, newer devices
        - **VP9 (libvpx-vp9):** Open source, good compression
        
        ### Audio Codecs:
        - **AAC:** High quality, widely supported
        - **MP3:** Universal compatibility
        - **Copy:** Keep original audio (faster conversion)
        
        ### Quality vs Speed:
        - **Faster presets:** Quick conversion, larger files
        - **Slower presets:** Better compression, smaller files
        """)
    
    # Help section
    with st.expander("❓ How to use"):
        st.markdown("""
        ### Steps to convert video files:
        
        1. **Upload a video file** using the file uploader above
        2. **Select output format** (MP4, AVI, MKV, WEBM, MOV)
        3. **Choose quality settings** based on your needs
        4. **Adjust resolution and frame rate** if needed
        5. **Set advanced options** for specialized needs
        6. **Click Convert** to start the process
        
        ### Supported input formats:
        - **Video:** MP4, MOV, AVI, MKV, WEBM, FLV, WMV, M4V, 3GP
        
        ### Quality presets:
        - **Ultrafast:** Fastest conversion, lower quality
        - **Fast:** Quick conversion, good quality
        - **Medium:** Balanced speed and quality
        - **Slow:** Slower conversion, better quality
        - **High:** Best quality, slowest conversion
        
        ### Tips:
        - Use batch conversion for multiple files
        - Higher quality = better output but slower conversion
        - Two-pass encoding improves quality for H.264/H.265
        - Consider resolution for file size vs quality trade-off
        """) 