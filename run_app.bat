@echo off
echo 🎵 Starting Video to MP3 Converter...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if FFmpeg is installed
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  FFmpeg not found! Please install FFmpeg first:
    echo    Download from: https://ffmpeg.org/download.html
    echo    Or use: winget install ffmpeg
    pause
    exit /b 1
)

REM Create downloads directory
if not exist "downloads" mkdir downloads

REM Start the Streamlit app
echo 🚀 Starting web interface...
echo 📱 Open http://localhost:8501 in your browser
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
pause
