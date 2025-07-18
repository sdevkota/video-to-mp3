import yt_dlp
import os
import tempfile
import re
import time

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    # Remove invalid characters for filenames
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Remove leading/trailing spaces
    filename = filename.strip()
    return filename

def download_video_as_mp3(video_url, temp_dir=None):
    """Download video (YouTube or MP4) as MP3 and return file path"""
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()
    
    try:
        # First get video info
        ydl_opts_info = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # If title is still "Unknown" or just the URL, try to extract from URL
            if title == 'Unknown' or title == video_url:
                # Extract filename from URL for MP4 files
                if video_url.endswith('.mp4'):
                    title = os.path.basename(video_url).replace('.mp4', '')
                else:
                    title = f"audio_{int(time.time())}"
        
        # Sanitize title for filename
        safe_title = sanitize_filename(title)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': f'{temp_dir}/{safe_title}.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            # YouTube bot detection bypass
            'cookiesfrombrowser': ('chrome',),  # Try to use Chrome cookies
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['js'],
                }
            },
            # Additional headers to avoid bot detection
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        # Find the downloaded MP3 file
        mp3_file = None
        for file in os.listdir(temp_dir):
            if file.endswith('.mp3'):
                mp3_file = os.path.join(temp_dir, file)
                break
        
        if mp3_file and os.path.exists(mp3_file):
            return {
                'success': True,
                'title': title,
                'duration': duration,
                'file_path': mp3_file,
                'filename': os.path.basename(mp3_file),
                'message': f"Successfully converted: {title}"
            }
        else:
            return {
                'success': False,
                'error': "MP3 file not found after conversion",
                'message': "Conversion completed but file not found"
            }
            
    except yt_dlp.utils.DownloadError as e:
        return {
            'success': False,
            'error': str(e),
            'message': "Download failed. Try updating yt-dlp or use a different video URL."
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"An error occurred: {str(e)}"
        }

# Backward compatibility
def download_youtube_as_mp3(youtube_url, temp_dir=None):
    """Backward compatibility wrapper"""
    return download_video_as_mp3(youtube_url, temp_dir)

def get_video_info(video_url):
    """Get video information without downloading"""
    try:
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True,
            # YouTube bot detection bypass
            'cookiesfrombrowser': ('chrome',),
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['js'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            title = info.get('title', 'Unknown')
            # Handle direct MP4 URLs
            if title == 'Unknown' or title == video_url:
                if video_url.endswith('.mp4'):
                    title = os.path.basename(video_url).replace('.mp4', '')
                else:
                    title = f"audio_{int(time.time())}"
            
            return {
                'success': True,
                'title': title,
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', '')
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# CLI usage
if __name__ == '__main__':
    url = input("Enter YouTube URL: ")
    
    # For CLI, save to downloads folder
    downloads_folder = "downloads"
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    
    result = download_video_as_mp3(url, downloads_folder)
    print(result['message'])
    
    if result['success']:
        print(f"File saved: {result['file_path']}")
