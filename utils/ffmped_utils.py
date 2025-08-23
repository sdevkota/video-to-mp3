import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json

def run_ffmpeg_command(cmd: list, timeout: int = 300) -> Tuple[bool, str, str]:
    """
    Run FFmpeg command and return success status and output
    
    Args:
        cmd: FFmpeg command as list
        timeout: Command timeout in seconds
    
    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def convert_audio(
    input_path: str,
    output_path: str,
    output_format: str,
    quality: str = "192k",
    sample_rate: int = 44100,
    channels: int = 2,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    normalize: bool = False,
    fade_in: float = 0.0,
    fade_out: float = 0.0
) -> bool:
    """
    Convert audio file using FFmpeg
    
    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        output_format: Output format (mp3, wav, flac, etc.)
        quality: Audio quality/bitrate
        sample_rate: Sample rate in Hz
        channels: Number of audio channels
        start_time: Start time in seconds
        end_time: End time in seconds
        normalize: Whether to normalize audio
        fade_in: Fade in duration in seconds
        fade_out: Fade out duration in seconds
    
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        # Base FFmpeg command
        cmd = ["ffmpeg", "-i", input_path, "-y"]
        
        # Add input options
        if start_time is not None:
            cmd.extend(["-ss", str(start_time)])
        if end_time is not None:
            cmd.extend(["-to", str(end_time)])
        
        # Add audio processing filters
        filters = []
        
        if normalize:
            filters.append("loudnorm")
        
        if fade_in > 0:
            filters.append(f"afade=t=in:st=0:d={fade_in}")
        
        if fade_out > 0:
            # Calculate fade out start time
            duration = end_time - start_time if start_time and end_time else None
            if duration:
                fade_start = duration - fade_out
                filters.append(f"afade=t=out:st={fade_start}:d={fade_out}")
        
        # Apply filters if any
        if filters:
            cmd.extend(["-af", ",".join(filters)])
        
        # Add output options based on format
        if output_format == "mp3":
            cmd.extend(["-vn", "-acodec", "libmp3lame", "-ab", quality, "-ar", str(sample_rate), "-ac", str(channels)])
        elif output_format == "wav":
            cmd.extend(["-vn", "-acodec", "pcm_s16le", "-ar", str(sample_rate), "-ac", str(channels)])
        elif output_format == "flac":
            cmd.extend(["-vn", "-acodec", "flac", "-ar", str(sample_rate), "-ac", str(channels)])
        elif output_format == "aac":
            cmd.extend(["-vn", "-acodec", "aac", "-b:a", quality, "-ar", str(sample_rate), "-ac", str(channels)])
        elif output_format == "ogg":
            cmd.extend(["-vn", "-acodec", "libvorbis", "-ar", str(sample_rate), "-ac", str(channels)])
        else:
            # Default to copy codec
            cmd.extend(["-vn", "-acodec", "copy"])
        
        # Add output path
        cmd.append(output_path)
        
        # Run conversion
        success, stdout, stderr = run_ffmpeg_command(cmd)
        
        if not success:
            print(f"FFmpeg error: {stderr}")
        
        return success
        
    except Exception as e:
        print(f"Error in convert_audio: {e}")
        return False

def convert_video(
    input_path: str,
    output_path: str,
    output_format: str,
    quality_preset: str = "medium",
    resolution: Optional[Tuple[int, int]] = None,
    fps: Optional[int] = None,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    crop_width: Optional[int] = None,
    crop_height: Optional[int] = None,
    audio_codec: str = "aac",
    video_codec: str = "libx264",
    two_pass: bool = False,
    deinterlace: bool = False
) -> bool:
    """
    Convert video file using FFmpeg
    
    Args:
        input_path: Input video file path
        output_path: Output video file path
        output_format: Output format (mp4, avi, mkv, etc.)
        quality_preset: Quality preset (ultrafast, fast, medium, slow, high)
        resolution: Target resolution (width, height)
        fps: Target frame rate
        start_time: Start time in seconds
        end_time: End time in seconds
        crop_width: Crop width in pixels
        crop_height: Crop height in pixels
        audio_codec: Audio codec to use
        video_codec: Video codec to use
        two_pass: Whether to use two-pass encoding
        deinterlace: Whether to deinterlace video
    
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        # Base FFmpeg command
        cmd = ["ffmpeg", "-i", input_path, "-y"]
        
        # Add input options
        if start_time is not None:
            cmd.extend(["-ss", str(start_time)])
        if end_time is not None:
            cmd.extend(["-to", str(end_time)])
        
        # Add video processing filters
        filters = []
        
        if deinterlace:
            filters.append("yadif")
        
        if crop_width and crop_height:
            filters.append(f"crop={crop_width}:{crop_height}")
        
        if resolution:
            filters.append(f"scale={resolution[0]}:{resolution[1]}")
        
        if fps:
            filters.append(f"fps={fps}")
        
        # Apply filters if any
        if filters:
            cmd.extend(["-vf", ",".join(filters)])
        
        # Add video codec options
        if video_codec == "libx264":
            quality_settings = {
                "ultrafast": {"crf": "28", "preset": "ultrafast"},
                "fast": {"crf": "26", "preset": "fast"},
                "medium": {"crf": "23", "preset": "medium"},
                "slow": {"crf": "20", "preset": "slow"},
                "high": {"crf": "18", "preset": "slow"}
            }
            
            if quality_preset in quality_settings:
                settings = quality_settings[quality_preset]
                cmd.extend(["-c:v", video_codec, "-crf", settings["crf"], "-preset", settings["preset"]])
            else:
                cmd.extend(["-c:v", video_codec, "-crf", "23", "-preset", "medium"])
        
        elif video_codec == "libx265":
            cmd.extend(["-c:v", video_codec, "-crf", "28", "-preset", "medium"])
        
        elif video_codec == "libvpx-vp9":
            cmd.extend(["-c:v", video_codec, "-crf", "30", "-b:v", "0"])
        
        else:
            cmd.extend(["-c:v", video_codec])
        
        # Add audio codec options
        if audio_codec == "copy":
            cmd.extend(["-c:a", "copy"])
        elif audio_codec == "none":
            cmd.extend(["-an"])
        else:
            cmd.extend(["-c:a", audio_codec])
        
        # Add output path
        cmd.append(output_path)
        
        # Run conversion
        success, stdout, stderr = run_ffmpeg_command(cmd)
        
        if not success:
            print(f"FFmpeg error: {stderr}")
        
        return success
        
    except Exception as e:
        print(f"Error in convert_video: {e}")
        return False

def extract_audio_from_video(
    input_path: str,
    output_path: str,
    audio_format: str = "mp3",
    quality: str = "192k",
    sample_rate: int = 44100,
    channels: int = 2
) -> bool:
    """
    Extract audio from video file
    
    Args:
        input_path: Input video file path
        output_path: Output audio file path
        audio_format: Output audio format
        quality: Audio quality/bitrate
        sample_rate: Sample rate in Hz
        channels: Number of audio channels
    
    Returns:
        True if extraction successful, False otherwise
    """
    return convert_audio(
        input_path=input_path,
        output_path=output_path,
        output_format=audio_format,
        quality=quality,
        sample_rate=sample_rate,
        channels=channels
    )

def compress_video(
    input_path: str,
    output_path: str,
    output_format: str = "mp4",
    crf: str = "25",
    preset: str = "medium",
    target_size_mb: Optional[int] = None,
    maintain_quality: bool = False
) -> bool:
    """
    Compress video file to reduce size
    
    Args:
        input_path: Input video file path
        output_path: Output video file path
        output_format: Output format
        crf: Constant Rate Factor (lower = better quality, higher = smaller file)
        preset: Encoding preset (ultrafast, fast, medium, slow, slower)
        target_size_mb: Target file size in MB
        maintain_quality: Whether to prioritize quality over size
    
    Returns:
        True if compression successful, False otherwise
    """
    try:
        # Base FFmpeg command
        cmd = ["ffmpeg", "-i", input_path, "-y"]
        
        # Adjust CRF based on quality preference
        if maintain_quality:
            crf = str(max(18, int(crf) - 5))  # Better quality
        else:
            crf = str(min(35, int(crf) + 5))   # Smaller file
        
        # Add video codec options
        cmd.extend(["-c:v", "libx264", "-crf", crf, "-preset", preset])
        
        # Add audio codec
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])
        
        # Add output path
        cmd.append(output_path)
        
        # Run compression
        success, stdout, stderr = run_ffmpeg_command(cmd)
        
        if not success:
            print(f"FFmpeg error: {stderr}")
        
        return success
        
    except Exception as e:
        print(f"Error in compress_video: {e}")
        return False

def analyze_media(input_path: str, analysis_type: str = "basic") -> Optional[Dict[str, Any]]:
    """
    Analyze media file using FFprobe
    
    Args:
        input_path: Input media file path
        analysis_type: Type of analysis (basic, detailed, codec, stream)
    
    Returns:
        Dictionary containing analysis results or None if error
    """
    try:
        # Base FFprobe command
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", input_path
        ]
        
        # Run analysis
        success, stdout, stderr = run_ffmpeg_command(cmd, timeout=60)
        
        if not success:
            print(f"FFprobe error: {stderr}")
            return None
        
        # Parse JSON output
        info = json.loads(stdout)
        
        # Process based on analysis type
        if analysis_type == "basic":
            return process_basic_analysis(info)
        elif analysis_type == "detailed":
            return process_detailed_analysis(info)
        elif analysis_type == "codec":
            return process_codec_analysis(info)
        elif analysis_type == "stream":
            return process_stream_analysis(info)
        else:
            return info
            
    except Exception as e:
        print(f"Error in analyze_media: {e}")
        return None

def process_basic_analysis(info: Dict[str, Any]) -> Dict[str, Any]:
    """Process basic media analysis"""
    format_info = info.get('format', {})
    streams = info.get('streams', [])
    
    # Count stream types
    video_streams = [s for s in streams if s.get('codec_type') == 'video']
    audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
    
    return {
        'format_name': format_info.get('format_name', 'unknown'),
        'duration_min': float(format_info.get('duration', 0)) / 60,
        'file_size_mb': int(format_info.get('size', 0)) / (1024 * 1024),
        'bitrate_kbps': int(format_info.get('bit_rate', 0)) / 1000,
        'has_video': len(video_streams) > 0,
        'has_audio': len(audio_streams) > 0,
        'video_streams_count': len(video_streams),
        'audio_streams_count': len(audio_streams)
    }

def process_detailed_analysis(info: Dict[str, Any]) -> Dict[str, Any]:
    """Process detailed media analysis"""
    basic_info = process_basic_analysis(info)
    streams = info.get('streams', [])
    
    # Get video info
    video_streams = [s for s in streams if s.get('codec_type') == 'video']
    audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
    
    video_info = {}
    if video_streams:
        video_stream = video_streams[0]
        video_info = {
            'width': video_stream.get('width'),
            'height': video_stream.get('height'),
            'codec_name': video_stream.get('codec_name'),
            'fps': eval(video_stream.get('r_frame_rate', '0/1')) if '/' in video_stream.get('r_frame_rate', '0/1') else 0,
            'bitrate_kbps': int(video_stream.get('bit_rate', 0)) / 1000 if video_stream.get('bit_rate') else 0,
            'color_space': video_stream.get('color_space'),
            'aspect_ratio': video_stream.get('display_aspect_ratio')
        }
    
    audio_info = {}
    if audio_streams:
        audio_stream = audio_streams[0]
        audio_info = {
            'codec_name': audio_stream.get('codec_name'),
            'sample_rate': audio_stream.get('sample_rate'),
            'channels': audio_stream.get('channels'),
            'bitrate_kbps': int(audio_stream.get('bit_rate', 0)) / 1000 if audio_stream.get('bit_rate') else 0,
            'language': audio_stream.get('language'),
            'duration_sec': float(audio_stream.get('duration', 0))
        }
    
    basic_info.update({
        'video_info': video_info,
        'audio_info': audio_info,
        'streams': streams
    })
    
    return basic_info

def process_codec_analysis(info: Dict[str, Any]) -> Dict[str, Any]:
    """Process codec analysis"""
    return {
        'video_streams': [s for s in info.get('streams', []) if s.get('codec_type') == 'video'],
        'audio_streams': [s for s in info.get('streams', []) if s.get('codec_type') == 'audio'],
        'format_info': info.get('format', {})
    }

def process_stream_analysis(info: Dict[str, Any]) -> Dict[str, Any]:
    """Process stream analysis"""
    return {
        'streams': info.get('streams', []),
        'format_info': info.get('format', {}),
        'total_streams': len(info.get('streams', []))
    }