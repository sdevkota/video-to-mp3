import os
import re
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Remove invalid characters from filename and limit length
    
    Args:
        filename: Original filename
        max_length: Maximum length for filename
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Strip whitespace
    filename = filename.strip()
    
    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        # Account for extension length and ellipsis
        max_name_length = max_length - len(ext) - 3
        filename = name[:max_name_length] + "..." + ext
    
    return filename

def check_ffmpeg() -> bool:
    """
    Check if FFmpeg is available in system PATH
    
    Returns:
        True if FFmpeg is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'], 
            capture_output=True, 
            check=True,
            timeout=10
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive file information using FFprobe
    
    Args:
        file_path: Path to the media file
    
    Returns:
        Dictionary containing file information or None if error
    """
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True,
            timeout=30
        )
        
        info = json.loads(result.stdout)
        
        # Extract basic information
        format_info = info.get('format', {})
        streams = info.get('streams', [])
        
        # Parse duration
        duration = float(format_info.get('duration', 0))
        format_name = format_info.get('format_name', 'unknown')
        file_size = int(format_info.get('size', 0))
        
        # Analyze streams
        video_streams = [s for s in streams if s.get('codec_type') == 'video']
        audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
        
        has_video = len(video_streams) > 0
        has_audio = len(audio_streams) > 0
        
        # Get video info
        video_info = {}
        if video_streams:
            video_stream = video_streams[0]
            video_info = {
                'codec': video_stream.get('codec_name', 'unknown'),
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'fps': video_stream.get('r_frame_rate', '0/0'),
                'bit_rate': video_stream.get('bit_rate', '0'),
                'pixel_format': video_stream.get('pix_fmt', 'unknown')
            }
        
        # Get audio info
        audio_info = {}
        if audio_streams:
            audio_stream = audio_streams[0]
            audio_info = {
                'codec': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': audio_stream.get('sample_rate', 0),
                'channels': audio_stream.get('channels', 0),
                'bit_rate': audio_stream.get('bit_rate', '0'),
                'channel_layout': audio_stream.get('channel_layout', 'unknown')
            }
        
        return {
            'duration': duration,
            'format': format_name,
            'file_size': file_size,
            'has_video': has_video,
            'has_audio': has_audio,
            'video_info': video_info,
            'audio_info': audio_info,
            'streams_count': {
                'video': len(video_streams),
                'audio': len(audio_streams),
                'total': len(streams)
            }
        }
        
    except (subprocess.CalledProcessError, json.JSONDecodeError, 
            subprocess.TimeoutExpired, Exception) as e:
        print(f"Error getting file info: {e}")
        return None

def format_duration(seconds: float) -> str:
    """
    Format duration from seconds to readable format
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string (HH:MM:SS or MM:SS)
    """
    if not seconds or seconds < 0:
        return "Unknown"
    
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    seconds = int(seconds) % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in appropriate units
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted file size string
    """
    if size_bytes >= 1024**3:  # >= 1GB
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes >= 1024**2:  # >= 1MB
        return f"{size_bytes / (1024**2):.2f} MB"
    elif size_bytes >= 1024:  # >= 1KB
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes} bytes"

def create_temp_dir(prefix: str = "media_converter_") -> str:
    """
    Create a temporary directory for processing
    
    Args:
        prefix: Prefix for temporary directory name
    
    Returns:
        Path to created temporary directory
    """
    return tempfile.mkdtemp(prefix=prefix)

def cleanup_temp_dir(temp_dir: str) -> bool:
    """
    Clean up temporary directory and all contents
    
    Args:
        temp_dir: Path to temporary directory
    
    Returns:
        True if cleanup successful, False otherwise
    """
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"Error cleaning up temp directory {temp_dir}: {e}")
        return False

def validate_file_format(filename: str, allowed_formats: list) -> bool:
    """
    Validate if file has an allowed format
    
    Args:
        filename: Name of the file
        allowed_formats: List of allowed file extensions (without dots)
    
    Returns:
        True if format is allowed, False otherwise
    """
    file_extension = Path(filename).suffix.lower().lstrip('.')
    return file_extension in [fmt.lower() for fmt in allowed_formats]

def get_output_filename(input_filename: str, output_format: str) -> str:
    """
    Generate output filename by changing extension
    
    Args:
        input_filename: Original filename
        output_format: Desired output format (extension without dot)
    
    Returns:
        Output filename with new extension
    """
    base_name = Path(input_filename).stem
    safe_name = sanitize_filename(base_name)
    return f"{safe_name}.{output_format.lower()}"

def estimate_conversion_time(file_size_bytes: int, conversion_type: str = "audio") -> str:
    """
    Estimate conversion time based on file size
    
    Args:
        file_size_bytes: Size of input file in bytes
        conversion_type: Type of conversion ("audio", "video", "compress")
    
    Returns:
        Estimated time string
    """
    # Rough estimates based on typical conversion speeds
    size_mb = file_size_bytes / (1024**2)
    
    if conversion_type == "audio":
        # Audio conversion is typically fast
        if size_mb < 50:
            return "< 1 minute"
        elif size_mb < 200:
            return "1-3 minutes"
        else:
            return f"{int(size_mb / 100)} - {int(size_mb / 50)} minutes"
    
    elif conversion_type == "video":
        # Video conversion is slower
        if size_mb < 100:
            return "2-5 minutes"
        elif size_mb < 500:
            return "5-15 minutes"
        elif size_mb < 1000:
            return "15-30 minutes"
        else:
            return f"{int(size_mb / 50)} - {int(size_mb / 25)} minutes"
    
    elif conversion_type == "compress":
        # Compression time varies
        if size_mb < 200:
            return "2-5 minutes"
        elif size_mb < 1000:
            return "5-20 minutes"
        else:
            return f"{int(size_mb / 100)} - {int(size_mb / 50)} minutes"
    
    return "Processing time varies"

def safe_file_read(file_path: str, chunk_size: int = 8192) -> bytes:
    """
    Safely read large files in chunks
    
    Args:
        file_path: Path to file to read
        chunk_size: Size of each chunk to read
    
    Returns:
        File contents as bytes
    """
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return b""