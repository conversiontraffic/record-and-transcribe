@echo off
echo ============================================
echo  Record ^& Transcribe - Build Script
echo ============================================
echo.

:: Check for FFmpeg in bundled_ffmpeg/
if not exist "bundled_ffmpeg\ffmpeg.exe" (
    echo [WARNING] bundled_ffmpeg\ffmpeg.exe not found!
    echo           The .exe will work but MP3 conversion requires FFmpeg.
    echo           Download from: https://github.com/BtbN/FFmpeg-Builds/releases
    echo           Place ffmpeg.exe in the bundled_ffmpeg\ folder.
    echo.
)

:: Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements-dev.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo.

:: Build with PyInstaller
echo [2/3] Building executable...
pyinstaller record-and-transcribe.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)
echo.

:: Done
echo [3/3] Build complete!
echo.
if exist "dist\RecordAndTranscribe.exe" (
    echo   Output: dist\RecordAndTranscribe.exe
    echo   Size:
    for %%A in (dist\RecordAndTranscribe.exe) do echo     %%~zA bytes
) else (
    echo [WARNING] Expected output not found at dist\RecordAndTranscribe.exe
)
echo.
pause
