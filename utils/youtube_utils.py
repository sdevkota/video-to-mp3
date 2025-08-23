import os
import tempfile
import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess

from config import YT_DLP_OPTIONS, QUALITY_PRESETS

def download_youtube_audio(
    url: str,
    output_format: str = "mp3",
    quality: str = "192k",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Optional[str]:
    """
    Download YouTube video and convert to audio format
    
    Args:
        url: YouTube video URL
        output_format: Output audio format
        quality: Audio quality/bitrate
        start_time: Start time for trimming (HH:MM:SS)
        end_time: End time for trimming (HH:MM:SS)
    
    Returns:
        Path to downloaded audio file or None if failed
    """
    try:
        # Create output directory
        output_dir = Path("downloads")
        output_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = YT_DLP_OPTIONS["base"].copy()
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': quality.replace('k', ''),
            }],
            'quiet': True,
            'no_warnings': True
        })
        
        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown')
            
            # Find the downloaded file
            downloaded_file = None
            for file in output_dir.iterdir():
                if file.suffix == f'.{output_format}' and video_title.lower() in file.name.lower():
                    downloaded_file = file
                    break
            
            if not downloaded_file:
                # Try to find any file with the correct extension
                for file in output_dir.iterdir():
                    if file.suffix == f'.{output_format}':
                        downloaded_file = file
                        break
            
            if downloaded_file:
                # Apply trimming if specified
                if start_time or end_time:
                    trimmed_file = apply_audio_trimming(
                        str(downloaded_file),
                        output_format,
                        start_time,
                        end_time
                    )
                    if trimmed_file:
                        # Remove original file
                        try:
                            os.remove(downloaded_file)
                        except:
                            pass
                        return trimmed_file
                
                return str(downloaded_file)
            
            return None
            
    except Exception as e:
        print(f"Error downloading YouTube audio: {e}")
        return None

def download_youtube_video(
    url: str,
    output_format: str = "mp4",
    quality_preset: str = "medium",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Optional[str]:
    """
    Download YouTube video in specified format
    
    Args:
        url: YouTube video URL
        output_format: Output video format
        quality_preset: Video quality preset
        start_time: Start time for trimming (HH:MM:SS)
        end_time: End time for trimming (HH:MM:SS)
    
    Returns:
        Path to downloaded video file or None if failed
    """
    try:
        # Create output directory
        output_dir = Path("downloads")
        output_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = YT_DLP_OPTIONS["base"].copy()
        ydl_opts.update({
            'format': 'best[height<=720]/best',  # Limit to 720p for reasonable file size
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True
        })
        
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown')
            
            # Find the downloaded file
            downloaded_file = None
            for file in output_dir.iterdir():
                if file.suffix in ['.mp4', '.webm', '.mkv'] and video_title.lower() in file.name.lower():
                    downloaded_file = file
                    break
            
            if not downloaded_file:
                # Try to find any video file
                for file in output_dir.iterdir():
                    if file.suffix in ['.mp4', '.webm', '.mkv']:
                        downloaded_file = file
                        break
            
            if downloaded_file:
                # Convert to desired format if needed
                if downloaded_file.suffix != f'.{output_format}':
                    converted_file = convert_video_format(
                        str(downloaded_file),
                        output_format,
                        quality_preset
                    )
                    if converted_file:
                        # Remove original file
                        try:
                            os.remove(downloaded_file)
                        except:
                            pass
                        return converted_file
                
                # Apply trimming if specified
                if start_time or end_time:
                    trimmed_file = apply_video_trimming(
                        str(downloaded_file),
                        output_format,
                        start_time,
                        end_time
                    )
                    if trimmed_file:
                        # Remove original file
                        try:
                            os.remove(downloaded_file)
                        except:
                            pass
                        return trimmed_file
                
                return str(downloaded_file)
            
            return None
            
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        return None

def apply_audio_trimming(
    input_path: str,
    output_format: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Optional[str]:
    """
    Apply trimming to audio file using FFmpeg
    
    Args:
        input_path: Input audio file path
        output_format: Output audio format
        start_time: Start time (HH:MM:SS)
        end_time: End time (HH:MM:SS)
    
    Returns:
        Path to trimmed audio file or None if failed
    """
    try:
        # Create output filename
        input_file = Path(input_path)
        output_filename = f"{input_file.stem}_trimmed.{output_format}"
        output_path = input_file.parent / output_filename
        
        # Build FFmpeg command
        cmd = ["ffmpeg", "-i", input_path, "-y"]
        
        if start_time:
            cmd.extend(["-ss", start_time])
        if end_time:
            cmd.extend(["-to", end_time])
        
        # Add output options
        if output_format == "mp3":
            cmd.extend(["-vn", "-acodec", "libmp3lame", "-ab", "192k"])
        elif output_format == "wav":
            cmd.extend(["-vn", "-acodec", "pcm_s16le"])
        elif output_format == "flac":
            cmd.extend(["-vn", "-acodec", "flac"])
        else:
            cmd.extend(["-vn", "-acodec", "copy"])
        
        cmd.append(str(output_path))
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and output_path.exists():
            return str(output_path)
        else:
            print(f"FFmpeg error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error applying audio trimming: {e}")
        return None

def apply_video_trimming(
    input_path: str,
    output_format: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Optional[str]:
    """
    Apply trimming to video file using FFmpeg
    
    Args:
        input_path: Input video file path
        output_format: Output video format
        start_time: Start time (HH:MM:SS)
        end_time: End time (HH:MM:SS)
    
    Returns:
        Path to trimmed video file or None if failed
    """
    try:
        # Create output filename
        input_file = Path(input_path)
        output_filename = f"{input_file.stem}_trimmed.{output_format}"
        output_path = input_file.parent / output_filename
        
        # Build FFmpeg command
        cmd = ["ffmpeg", "-i", input_path, "-y"]
        
        if start_time:
            cmd.extend(["-ss", start_time])
        if end_time:
            cmd.extend(["-to", end_time])
        
        # Add output options
        if output_format == "mp4":
            cmd.extend(["-c:v", "libx264", "-c:a", "aac"])
        elif output_format == "avi":
            cmd.extend(["-c:v", "libx264", "-c:a", "mp3"])
        elif output_format == "mkv":
            cmd.extend(["-c:v", "libx264", "-c:a", "aac"])
        else:
            cmd.extend(["-c:v", "copy", "-c:a", "copy"])
        
        cmd.append(str(output_path))
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and output_path.exists():
            return str(output_path)
        else:
            print(f"FFmpeg error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error applying video trimming: {e}")
        return None

def convert_video_format(
    input_path: str,
    output_format: str,
    quality_preset: str = "medium"
) -> Optional[str]:
    """
    Convert video to different format using FFmpeg
    
    Args:
        input_path: Input video file path
        output_format: Output video format
        quality_preset: Quality preset
    
    Returns:
        Path to converted video file or None if failed
    """
    try:
        # Create output filename
        input_file = Path(input_path)
        output_filename = f"{input_file.stem}.{output_format}"
        output_path = input_file.parent / output_filename
        
        # Get quality settings
        quality_settings = QUALITY_PRESETS["video"].get(quality_preset, {"crf": "23", "preset": "medium"})
        
        # Build FFmpeg command
        cmd = ["ffmpeg", "-i", input_path, "-y"]
        
        # Add video codec options
        if output_format == "mp4":
            cmd.extend(["-c:v", "libx264", "-crf", quality_settings["crf"], "-preset", quality_settings["preset"]])
        elif output_format == "avi":
            cmd.extend(["-c:v", "libx264", "-crf", quality_settings["crf"], "-preset", quality_settings["preset"]])
        elif output_format == "mkv":
            cmd.extend(["-c:v", "libx264", "-crf", quality_settings["crf"], "-preset", quality_settings["preset"]])
        else:
            cmd.extend(["-c:v", "copy"])
        
        # Add audio codec
        cmd.extend(["-c:a", "aac"])
        
        cmd.append(str(output_path))
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and output_path.exists():
            return str(output_path)
        else:
            print(f"FFmpeg error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error converting video format: {e}")
        return None

def get_youtube_info(url: str) -> Optional[Dict[str, Any]]:
    """
    Get YouTube video information without downloading
    
    Args:
        url: YouTube video URL
    
    Returns:
        Dictionary containing video information or None if failed
    """
    try:
        ydl_opts = YT_DLP_OPTIONS["base"].copy()
        ydl_opts.update({
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'upload_date': info.get('upload_date'),
                'description': info.get('description'),
                'thumbnail': info.get('thumbnail'),
                'formats': info.get('formats', [])
            }
            
    except Exception as e:
        print(f"Error getting YouTube info: {e}")
        return None