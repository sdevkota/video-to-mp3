@echo off
title NMG Video to MP3 Converter

echo.
echo 🎵 NMG Video to MP3 Converter
echo ==============================
echo.

REM Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo ✅ Python found
    python --version
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
        echo ✅ Python3 found
        python3 --version
    ) else (
        echo ❌ Python not found. Please install Python 3.7 or higher.
        echo    Visit: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo.

REM Check if pip is available
echo 🔍 Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    set PIP_CMD=pip
    echo ✅ pip found
) else (
    echo ❌ pip not found. Please install pip.
    pause
    exit /b 1
)

echo.

REM Check and install dependencies
echo 📦 Checking dependencies...

REM Check if yt-dlp is installed
%PYTHON_CMD% -c "import yt_dlp" 2>nul
if %errorlevel% equ 0 (
    echo ✅ yt-dlp is installed
) else (
    echo 📥 Installing yt-dlp...
    %PIP_CMD% install yt-dlp
)

REM Check if streamlit is installed
%PYTHON_CMD% -c "import streamlit" 2>nul
if %errorlevel% equ 0 (
    echo ✅ streamlit is installed
) else (
    echo 📥 Installing streamlit...
    %PIP_CMD% install streamlit
)

echo.

REM Check if ffmpeg is available
echo 🔍 Checking ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ ffmpeg found
) else (
    echo ⚠️  ffmpeg not found - audio conversion may not work properly
    echo    Download from: https://ffmpeg.org/download.html
    echo    Add ffmpeg to your system PATH
    echo.
    set /p choice="   Continue anyway? (y/n): "
    if /i not "%choice%"=="y" exit /b 1
)

echo.

REM Run the app
echo 🚀 Starting NMG Video to MP3 Converter...
echo 📱 Your browser will open automatically
echo 🌐 If not, visit: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

REM Run streamlit
%PYTHON_CMD% -m streamlit run app.py

echo.
echo 👋 Thank you for using NMG Video to MP3 Converter!
pause
