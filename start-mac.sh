#!/bin/bash
# Record & Transcribe - macOS Launcher
# Usage: chmod +x start-mac.sh && ./start-mac.sh

cd "$(dirname "$0")"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required."
    echo "Install with: brew install python"
    exit 1
fi

# Create virtual environment on first run
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install openai-whisper
    echo ""
    echo "Setup complete!"
    echo ""
else
    source venv/bin/activate
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: FFmpeg not found. MP3 conversion and video transcription won't work."
    echo "Install with: brew install ffmpeg"
    echo ""
fi

python src/recorder.py
