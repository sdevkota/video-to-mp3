import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from utils.file_utils import sanitize_filename, get_file_info, check_file_format
from utils.ffmped_utils import convert_audio
from config import SUPPORTED_FORMATS, QUALITY_PRESETS, MIME_TYPES

def render_page():
    """Render the audio converter page"""
    
    st.title("🎵 Audio Converter")
    st.markdown("Convert audio files between different formats with quality control")
    
    # Initialize variables
    submitted = False
    uploaded_file = None
    batch_submitted = False
    uploaded_files = None
    batch_output_format = "mp3"
    batch_quality = "medium"
    batch_sample_rate = "44100"
    batch_normalize = True
    
    # Updated supported formats to include DAT files
    supported_input_formats = SUPPORTED_FORMATS["audio_input"] + ["dat"]
    
    # Always show format information
    st.info("""
    **Supported Input Formats:** MP3, WAV, FLAC, M4A, AAC, OGG, WMA, MP4, MOV, AVI, MKV, WEBM, **DAT**  
    **Supported Output Formats:** MP3, WAV, FLAC, AAC, OGG
    """)
    
    # File upload section
    with st.form("audio_form"):
        st.subheader("📁 Upload Audio File")
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=supported_input_formats,
            help="Supported formats: MP3, WAV, FLAC, M4A, AAC, OGG, WMA, DAT, and video files with audio"
        )
        
        # Always show conversion settings
        st.subheader("⚙️ Conversion Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            output_format = st.selectbox(
                "🎯 Output Format",
                SUPPORTED_FORMATS["audio_output"],
                index=0,
                help="Select the desired output format (MP3, WAV, FLAC, AAC, OGG)"
            )
            
            quality = st.selectbox(
                "🎚️ Audio Quality",
                list(QUALITY_PRESETS["audio"].keys()),
                index=1,
                help="Select audio quality preset (Low: 128k, Medium: 192k, High: 256k, Maximum: 320k)"
            )
        
        with col2:
            sample_rate = st.selectbox(
                "🔊 Sample Rate (Hz)",
                ["44100", "48000", "22050", "16000"],
                index=0,
                help="Select sample rate in Hz (higher = better quality but larger file)"
            )
            
            channels = st.selectbox(
                "🎧 Audio Channels",
                ["2 (Stereo)", "1 (Mono)"],
                index=0,
                help="Select number of audio channels"
            )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.text_input(
                    "⏱️ Start Time (seconds)",
                    placeholder="0",
                    help="Start time for trimming (in seconds)"
                )
                
                end_time = st.text_input(
                    "⏱️ End Time (seconds)",
                    placeholder="0",
                    help="End time for trimming (in seconds)"
                )
            
            with col2:
                normalize = st.checkbox(
                    "📊 Normalize Audio",
                    value=True,
                    help="Normalize audio levels for consistent volume"
                )
                
                fade_in = st.number_input(
                    "🔊 Fade In (seconds)",
                    min_value=0.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.1,
                    help="Add fade in effect at the beginning"
                )
                
                fade_out = st.number_input(
                    "🔊 Fade Out (seconds)",
                    min_value=0.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.1,
                    help="Add fade out effect at the end"
                )
        
        # Show file info if uploaded
        if uploaded_file is not None:
            st.subheader("📋 File Information")
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / (1024*1024):.2f} MB",
                "File type": uploaded_file.type or "Unknown"
            }
            
            # Special handling for DAT files
            if uploaded_file.name.lower().endswith('.dat'):
                file_details["File type"] = "DAT (Digital Audio Tape)"
                st.info("📼 DAT file detected. This format will be processed as raw audio data.")
            
            st.json(file_details)
        
        # Submit button - always enabled, validation happens in processing
        submitted = st.form_submit_button("🔄 Convert Audio")
    
    # Process form submission
    if submitted:
        if uploaded_file is None:
            st.error("⚠️ Please upload an audio file first")
        else:
            try:
                with st.spinner("🔄 Converting audio..."):
                    # Create temporary file with proper extension handling for DAT files
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    if file_extension == 'dat':
                        # For DAT files, we'll let FFmpeg handle the format detection
                        temp_suffix = ".dat"
                    else:
                        temp_suffix = f".{file_extension}"
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=temp_suffix) as tmp_file:
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
                    
                    # Convert audio with special handling for DAT files
                    success = convert_audio(
                        input_path=input_path,
                        output_path=str(output_path),
                        output_format=output_format,
                        quality=QUALITY_PRESETS["audio"][quality],
                        sample_rate=int(sample_rate),
                        channels=1 if channels.startswith("1") else 2,
                        start_time=float(start_time) if start_time else None,
                        end_time=float(end_time) if end_time else None,
                        normalize=normalize,
                        fade_in=fade_in,
                        fade_out=fade_out,
                        input_format="dat" if file_extension == "dat" else None
                    )
                    
                    # Clean up input file
                    try:
                        os.unlink(input_path)
                    except:
                        pass
                    
                    if success and output_path.exists():
                        st.success("✅ Audio conversion completed successfully!")
                        
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
                            label="📥 Download Converted Audio",
                            data=file_data,
                            file_name=output_filename
                        )
                        
                        # Preview section
                        st.subheader("🎧 Audio Preview")
                        st.audio(file_data, format=f"audio/{output_format}")
                        
                    else:
                        st.error("❌ Audio conversion failed. Please check the file and try again.")
                        if file_extension == "dat":
                            st.warning("💡 DAT files may require specific handling. Ensure the file contains valid audio data.")
                        
            except Exception as e:
                st.error(f"❌ Error during conversion: {str(e)}")
                if uploaded_file.name.lower().endswith('.dat'):
                    st.warning("💡 DAT file conversion failed. This might be due to an unsupported DAT format variant or corrupted data.")
                st.exception(e)
    
    # Batch conversion section
    st.markdown("---")
    st.subheader("📦 Batch Conversion")
    
    with st.form("batch_form"):
        st.markdown("Convert multiple audio files at once")
        
        uploaded_files = st.file_uploader(
            "Choose multiple audio files",
            type=supported_input_formats,
            accept_multiple_files=True,
            help="Select multiple files for batch conversion (including DAT files)"
        )
        
        if uploaded_files:
            col1, col2 = st.columns(2)
            
            with col1:
                batch_output_format = st.selectbox(
                    "Output Format",
                    SUPPORTED_FORMATS["audio_output"],
                    index=0,
                    key="batch_format"
                )
                
                batch_quality = st.selectbox(
                    "Audio Quality",
                    list(QUALITY_PRESETS["audio"].keys()),
                    index=1,
                    key="batch_quality"
                )
            
            with col2:
                batch_sample_rate = st.selectbox(
                    "Sample Rate",
                    ["44100", "48000", "22050", "16000"],
                    index=0,
                    key="batch_sample_rate"
                )
                
                batch_normalize = st.checkbox(
                    "Normalize Audio",
                    value=True,
                    key="batch_normalize"
                )
            
            batch_submitted = st.form_submit_button("🔄 Convert All Files")
    
    # Process batch form submission
    if batch_submitted and uploaded_files:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            converted_files = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Converting {uploaded_file.name}...")
                
                try:
                    # Handle file extension for DAT files
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    temp_suffix = f".{file_extension}"
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=temp_suffix) as tmp_file:
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
                    
                    # Convert audio with DAT support
                    success = convert_audio(
                        input_path=input_path,
                        output_path=str(output_path),
                        output_format=batch_output_format,
                        quality=QUALITY_PRESETS["audio"][batch_quality],
                        sample_rate=int(batch_sample_rate),
                        channels=2,
                        normalize=batch_normalize,
                        input_format="dat" if file_extension == "dat" else None
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
                st.success(f"✅ Successfully converted {len(converted_files)} files!")
                
                # Create zip file for batch download
                import zipfile
                zip_path = output_dir / "converted_audio_files.zip"
                
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_path in converted_files:
                        zipf.write(file_path, os.path.basename(file_path))
                
                # Download zip button
                with open(zip_path, 'rb') as f:
                    zip_data = f.read()
                
                st.download_button(
                    label="📦 Download All Converted Files (ZIP)",
                    data=zip_data,
                    file_name="converted_audio_files.zip"
                )
                
                # Clean up zip file
                try:
                    os.unlink(zip_path)
                except:
                    pass
            else:
                st.error("❌ No files were successfully converted")
                
        except Exception as e:
            st.error(f"❌ Error during batch conversion: {str(e)}")
            st.exception(e)
    
    # Format comparison - Updated to include DAT
    with st.expander("📊 Format Comparison"):
        st.markdown("""
        | Format | Quality | File Size | Compatibility | Best For |
        |--------|---------|-----------|---------------|----------|
        | **MP3** | Good | Small | Universal | General use, streaming |
        | **WAV** | Excellent | Large | Universal | Professional audio, editing |
        | **FLAC** | Excellent | Medium | Good | High quality, archiving |
        | **AAC** | Very Good | Small | Good | Apple devices, streaming |
        | **OGG** | Very Good | Small | Limited | Open source, web |
        | **DAT** | Excellent | Large | Limited | Digital Audio Tape, archival |
        
        **💡 Recommendation:** MP3 is best for most uses due to universal compatibility and good quality-to-size ratio.
        
        **📼 DAT Files:** Digital Audio Tape files are high-quality audio format primarily used for professional recording and archival purposes.
        """)
    
    # Help section - Updated with DAT information
    with st.expander("❓ How to use"):
        st.markdown("""
        ### Steps to convert audio files:
        
        1. **Upload an audio file** using the file uploader above
        2. **Select output format** (MP3, WAV, FLAC, AAC, OGG)
        3. **Choose quality settings** based on your needs
        4. **Adjust advanced options** if needed
        5. **Click Convert** to start the process
        
        ### Supported input formats:
        - **Audio:** MP3, WAV, FLAC, M4A, AAC, OGG, WMA, **DAT**
        - **Video with audio:** MP4, MOV, AVI, MKV, WEBM
        
        ### Quality presets:
        - **Low (128k):** Small file size, basic quality
        - **Medium (192k):** Balanced size and quality
        - **High (256k):** Good quality, larger file
        - **Maximum (320k):** Best quality, largest file
        
        ### Tips:
        - Use batch conversion for multiple files
        - Normalize audio for consistent levels
        - Higher sample rates = better quality but larger files
        - **DAT files:** Ensure the DAT file contains valid audio data. Some DAT files may require specific handling.
        
        ### About DAT Files:
        - **DAT (Digital Audio Tape)** files are high-quality digital audio format
        - Originally used in professional recording and digital audio tape systems
        - May contain uncompressed digital audio data
        - Conversion success depends on the specific DAT format variant
        """)