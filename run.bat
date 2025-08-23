@echo off
REM Complete Media Converter Suite - Run Script for Windows
REM Built by Nepal Media Group

echo 🎵 Complete Media Converter Suite
echo =================================
echo.

REM Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    echo    Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python found
python --version

echo.

REM Check if pip is available
echo 🔍 Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip not found. Please install pip.
    pause
    exit /b 1
)
echo ✅ pip found

echo.

REM Check and install dependencies
echo 📦 Checking and installing dependencies...

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Upgrade pip
echo 📥 Upgrading pip...
python -m pip install --upgrade pip

REM Install all dependencies from requirements.txt
echo 📥 Installing all dependencies from requirements.txt...
pip install -r requirements.txt

REM Verify key dependencies
echo 🔍 Verifying key dependencies...

REM Check if yt-dlp is installed
python -c "import yt_dlp" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ yt-dlp installation failed
    pause
    exit /b 1
)
echo ✅ yt-dlp is installed

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ streamlit installation failed
    pause
    exit /b 1
)
echo ✅ streamlit is installed

REM Check if googletrans is installed
python -c "import googletrans" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ googletrans installation failed
    pause
    exit /b 1
)
echo ✅ googletrans is installed

REM Check if ffmpeg is available
echo 🔍 Checking ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  ffmpeg not found - media conversion will not work properly
    echo    Download from: https://ffmpeg.org/download.html
    echo    Extract and add bin folder to PATH
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        pause
        exit /b 1
    )
) else (
    echo ✅ ffmpeg found
)

echo.

REM Test if the app can be imported
echo 🧪 Testing application imports...
python -c "from main import main; print('✅ All modules imported successfully')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Application import failed. Please check the error above.
    pause
    exit /b 1
)
echo ✅ Application ready to run

echo.

REM Run the app
echo 🚀 Starting Complete Media Converter Suite...
echo 📱 Your browser will open automatically
echo 🌐 If not, visit: http://localhost:8501
echo.
echo 🎯 Available Tools:
echo    - 🎥 YouTube Converter
echo    - 🎵 Audio Converter
echo    - 🎬 Video Converter
echo    - 🛠️ Media Tools

echo.
echo Press Ctrl+C to stop the application
echo.

REM Run streamlit
python -m streamlit run main.py

echo.
echo 👋 Thank you for using Complete Media Converter Suite!
pause
