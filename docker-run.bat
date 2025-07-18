@echo off
title NMG Video to MP3 Converter - Docker Edition

echo.
echo 🐳 NMG Video to MP3 Converter - Docker Edition
echo ===============================================
echo.

REM Check if Docker is installed
echo 🔍 Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker found
    docker --version
) else (
    echo ❌ Docker not found. Please install Docker Desktop.
    echo    Visit: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo.

REM Check if Docker Compose is available
echo 🔍 Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    set COMPOSE_CMD=docker-compose
    echo ✅ docker-compose found
) else (
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=docker compose
        echo ✅ docker compose (plugin) found
    ) else (
        echo ❌ Docker Compose not found. Please install Docker Compose.
        pause
        exit /b 1
    )
)

echo.

REM Create downloads directory
echo 📁 Creating downloads directory...
if not exist downloads mkdir downloads
echo ✅ Downloads directory ready: .\downloads

echo.

REM Check if container is already running
echo 🔍 Checking for existing container...
docker ps | findstr "nmg-video-converter" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Container is already running!
    echo 🌐 Access the app at: http://localhost:8501
    echo.
    set /p choice="   Stop and restart? (y/n): "
    if /i "%choice%"=="y" (
        echo 🛑 Stopping existing container...
        %COMPOSE_CMD% down
    ) else (
        echo ✅ Keeping existing container running
        echo 🌐 Visit: http://localhost:8501
        pause
        exit /b 0
    )
)

echo.

REM Build and run the container
echo 🏗️  Building and starting the application...
echo 📦 This may take a few minutes on first run...
echo.

%COMPOSE_CMD% up --build -d

REM Check if container started successfully
echo.
echo 🔍 Checking container status...
timeout /t 5 /nobreak >nul

docker ps | findstr "nmg-video-converter" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Container started successfully!
    echo.
    echo 🎉 NMG Video to MP3 Converter is now running!
    echo 🌐 Open your browser and visit: http://localhost:8501
    echo 📁 Downloads will be saved to: .\downloads
    echo.
    echo 📋 Useful commands:
    echo    View logs:        %COMPOSE_CMD% logs -f
    echo    Stop container:   %COMPOSE_CMD% down
    echo    Restart:          %COMPOSE_CMD% restart
    echo.
) else (
    echo ❌ Container failed to start. Checking logs...
    %COMPOSE_CMD% logs
    pause
    exit /b 1
)

pause
