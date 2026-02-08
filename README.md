# Record & Transcribe

**Simple audio recorder with built-in transcription.** Record meetings, interviews, or any audio from your microphone and/or system audio, then transcribe it locally using OpenAI Whisper.

*by [conversion-traffic.de](https://www.conversion-traffic.de)*

[Deutsche Version / German Version](README_DE.md)

---

## Features

- Record **microphone** and/or **system audio** (WASAPI Loopback / BlackHole)
- **Live audio level meters** for both sources
- Automatic **MP3 conversion** after recording
- Built-in **transcription** using OpenAI Whisper (runs locally, no API key needed)
- **Transcribe existing files** (MP3, WAV, MP4, MKV, AVI, M4A, WebM)
- **Bilingual UI** - English and German
- **Cross-platform** - Windows (.exe) and macOS (from source)
- All processing happens **locally** - no data leaves your machine

## Download

Go to [Releases](../../releases) and download the latest `record-and-transcribe-vX.Y.Z-windows.exe`.

## System Requirements

- **OS:** Windows 10/11 or macOS 12+
- **Python:** 3.10+ (only for running from source)
- **FFmpeg:** Bundled in the .exe release, or install separately for development / macOS

### System Audio Recording

**Windows:**
- **Stereo Mix** - Enable in Windows Sound Settings > Recording Devices
- **VB-Audio Virtual Cable** (free) - [Download here](https://vb-audio.com/Cable/)
- **WASAPI Loopback device** - Some audio drivers expose this automatically

**macOS:**
- **BlackHole** (free, recommended) - `brew install blackhole-2ch`
- **Soundflower** (free) - [Download here](https://github.com/mattingalls/Soundflower)
- **Loopback** (paid) by Rogue Amoeba

## Quick Start

### Option 1: Installer (Recommended)

1. Download `record-and-transcribe-setup-vX.Y.Z-windows.exe` from [Releases](../../releases)
2. Run the installer (Start Menu shortcut + optional Desktop shortcut)
3. Select your audio sources
4. Click "Start Recording"

### Option 2: Portable .exe

1. Download `record-and-transcribe-vX.Y.Z-windows.exe` from [Releases](../../releases)
2. Run from any folder - no installation needed
3. Settings are saved next to the .exe

> **Windows SmartScreen:** On first launch, Windows may show "Windows protected your PC". Click **"More info"** then **"Run anyway"**. This happens because the app is not code-signed (it's open source and free).

### Option 3: macOS

```bash
git clone https://github.com/conversiontraffic/record-and-transcribe.git
cd record-and-transcribe

# One-command setup & launch (creates venv, installs deps)
chmod +x start-mac.sh
./start-mac.sh
```

Prerequisites: Python 3.10+ and FFmpeg (`brew install python ffmpeg`).
Optional for system audio: `brew install blackhole-2ch`

### Option 4: Run from Source (any OS)

```bash
git clone https://github.com/conversiontraffic/record-and-transcribe.git
cd record-and-transcribe

# Install dependencies
pip install -r requirements.txt

# Optional: Install Whisper for transcription
pip install openai-whisper

# Run
python src/recorder.py
```

## Transcription

Transcription uses [OpenAI Whisper](https://github.com/openai/whisper) running locally on your machine.

- **Model:** `small` (good balance of speed and accuracy)
- **Languages:** Auto-detect, German, English, French, Spanish, Italian
- **Note:** First transcription downloads the model (~460 MB)

Whisper is **optional** - the recorder works without it. Install with:

```bash
pip install openai-whisper
```

## Building from Source

### Prerequisites

- Python 3.9+
- FFmpeg (place `ffmpeg.exe` in `bundled_ffmpeg/` for bundling)

### Build the .exe

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Build (Windows)
build.bat

# Or manually:
pyinstaller record-and-transcribe.spec --noconfirm
```

Output: `dist/RecordAndTranscribe.exe`

## Configuration

Settings are saved in `config.json`. Location: `%APPDATA%\Record & Transcribe\` (Installer) or next to the .exe (Portable).

- **Output folder** - Where recordings are saved (default: `~/Documents/Record & Transcribe`)
- **Auto-transcribe** - Automatically transcribe after recording
- **Language** - Transcription language
- **UI Language** - Interface language (English/German, requires restart)

## License

GPL-3.0 License - see [LICENSE](LICENSE)

## Author

Benjamin Haentzschel - [conversion-traffic.de](https://www.conversion-traffic.de)
