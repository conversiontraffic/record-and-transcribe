"""
Transcriber module for Record & Transcribe.
Uses Whisper Python API with tqdm wrapper for real progress tracking.
"""

import os
import sys
import threading
import logging
from pathlib import Path
from typing import Callable, Optional
import subprocess

# Import tqdm module for patching
import tqdm as tqdm_module


class ProgressTqdm(tqdm_module.tqdm):
    """
    tqdm wrapper that calls a progress callback on each update.
    Whisper uses tqdm internally for its progress bar - we intercept that.
    Also polls progress periodically in case update() isn't called often.
    """
    _callback: Optional[Callable[[int], None]] = None
    _last_percent: int = -1
    _instance: Optional['ProgressTqdm'] = None
    _poll_thread: Optional[threading.Thread] = None
    _stop_polling: bool = False
    _devnull: Optional[object] = None

    def __init__(self, *args, **kwargs):
        # pythonw.exe has sys.stderr=None, which crashes tqdm.
        # Redirect output to devnull since we use callbacks instead.
        if sys.stderr is None:
            if ProgressTqdm._devnull is None:
                ProgressTqdm._devnull = open(os.devnull, 'w')
            kwargs.setdefault('file', ProgressTqdm._devnull)
        super().__init__(*args, **kwargs)
        ProgressTqdm._instance = self
        ProgressTqdm._stop_polling = False
        ProgressTqdm._poll_thread = threading.Thread(target=self._poll_progress, daemon=True)
        ProgressTqdm._poll_thread.start()

    def _poll_progress(self):
        """Poll progress every 2 seconds and report it."""
        import time
        while not ProgressTqdm._stop_polling:
            time.sleep(2)
            if ProgressTqdm._instance and ProgressTqdm._callback:
                inst = ProgressTqdm._instance
                if inst.total and inst.total > 0:
                    percent = int((inst.n / inst.total) * 100)
                    if percent != ProgressTqdm._last_percent:
                        ProgressTqdm._last_percent = percent
                        ProgressTqdm._callback(percent)

    def update(self, n=1):
        super().update(n)
        self._report_progress()

    def _report_progress(self):
        """Report current progress to callback."""
        if ProgressTqdm._callback and self.total:
            percent = int((self.n / self.total) * 100)
            if percent != ProgressTqdm._last_percent:
                ProgressTqdm._last_percent = percent
                ProgressTqdm._callback(percent)

    def close(self):
        ProgressTqdm._stop_polling = True
        ProgressTqdm._instance = None
        super().close()


logger = logging.getLogger(__name__)

# Cache for system whisper GPU check result
_system_whisper_gpu_cache: tuple[bool, str | None] | None = None


def check_system_whisper_gpu() -> tuple[bool, str | None]:
    """
    Check if system Python has whisper + CUDA GPU available.
    Only checks when running as .exe (PyInstaller bundle).
    Results are cached for the lifetime of the process.

    Returns:
        (available, python_path) - whether system whisper+GPU is available and the python path
    """
    global _system_whisper_gpu_cache

    if _system_whisper_gpu_cache is not None:
        return _system_whisper_gpu_cache

    # Only relevant in .exe mode
    if not hasattr(sys, '_MEIPASS'):
        _system_whisper_gpu_cache = (False, None)
        return _system_whisper_gpu_cache

    for python_cmd in ['python', 'python3']:
        try:
            result = subprocess.run(
                [python_cmd, '-c',
                 'import whisper, torch; print(torch.cuda.is_available())'],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            if result.returncode == 0 and 'True' in result.stdout:
                logger.info(f"System whisper+GPU detected via '{python_cmd}'")
                _system_whisper_gpu_cache = (True, python_cmd)
                return _system_whisper_gpu_cache
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue

    logger.info("No system whisper+GPU found")
    _system_whisper_gpu_cache = (False, None)
    return _system_whisper_gpu_cache


class Transcriber:
    """Handles audio transcription using Whisper Python API."""

    # Language map: whisper language code -> whisper language name
    # The keys displayed in UI come from i18n, this maps to Whisper's expected values
    SUPPORTED_LANGUAGES = {
        None: None,       # Auto-detect
        'German': 'German',
        'English': 'English',
        'French': 'French',
        'Spanish': 'Spanish',
        'Italian': 'Italian',
    }

    AVAILABLE_MODELS = ['tiny', 'base', 'small', 'medium', 'large']

    def __init__(self, model: str = 'small'):
        """
        Initialize transcriber.

        Args:
            model: Whisper model to use (tiny, base, small, medium, large)
        """
        self.model_name = model
        self.model = None  # Lazy loading
        self.is_transcribing = False
        self._cancelled = False
        self._process: subprocess.Popen | None = None

    def _transcribe_via_system(
        self,
        audio_path: Path,
        language: str | None,
        output_format: str,
        output_dir: Path | None,
        callback: Optional[Callable[[str], None]],
        on_progress: Optional[Callable[[int], None]],
        on_status: Optional[Callable[[str], None]]
    ) -> Path:
        """
        Transcribe using system-installed whisper CLI with GPU support.
        Called when running as .exe and system Python has whisper+CUDA.
        """
        _, python_path = check_system_whisper_gpu()

        if output_dir is None:
            output_dir = audio_path.parent
        else:
            output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if on_status:
            on_status('transcribing_gpu')

        cmd = [
            python_path, '-m', 'whisper',
            str(audio_path),
            '--model', self.model_name,
            '--output_format', output_format,
            '--output_dir', str(output_dir),
            '--verbose', 'False'
        ]
        if language:
            cmd.extend(['--language', language])

        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            # Wait for completion, checking for cancellation
            while self._process.poll() is None:
                if self._cancelled:
                    self._process.terminate()
                    try:
                        self._process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self._process.kill()
                    raise RuntimeError("Transcription cancelled")
                # Brief sleep to avoid busy-waiting
                import time
                time.sleep(0.5)

            if self._process.returncode != 0:
                stderr = self._process.stderr.read() if self._process.stderr else ''
                raise RuntimeError(f"System whisper failed (exit {self._process.returncode}): {stderr[-500:]}")

            if on_progress:
                on_progress(100)

            output_path = output_dir / f"{audio_path.stem}.{output_format}"
            if not output_path.exists():
                raise RuntimeError(f"Expected output file not found: {output_path}")

            if callback:
                callback(str(output_path))

            return output_path

        finally:
            self._process = None
            self.is_transcribing = False

    def transcribe(
        self,
        audio_path: str | Path,
        language: str = 'German',
        output_format: str = 'txt',
        output_dir: str | Path = None,
        callback: Optional[Callable[[str], None]] = None,
        on_progress: Optional[Callable[[int], None]] = None,
        on_status: Optional[Callable[[str], None]] = None
    ) -> Path:
        """
        Transcribe audio file using Whisper Python API.

        Args:
            audio_path: Path to audio file (MP3 or WAV)
            language: Language of the audio (English, German, etc.) or None for auto
            output_format: Output format (txt only for now)
            output_dir: Directory to save output (default: same as audio file)
            callback: Optional callback function called when done with output path
            on_progress: Optional callback for progress updates (receives percent 0-100)
            on_status: Optional callback for status updates (receives status key string)

        Returns:
            Path to the transcription file
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self.is_transcribing = True
        self._cancelled = False

        # In .exe mode, delegate to system whisper if GPU is available
        if hasattr(sys, '_MEIPASS'):
            gpu_available, _ = check_system_whisper_gpu()
            if gpu_available:
                return self._transcribe_via_system(
                    audio_path, language, output_format,
                    output_dir, callback, on_progress, on_status
                )

        import whisper

        # Install tqdm wrapper BEFORE model loading so download progress is captured
        original_tqdm = tqdm_module.tqdm
        ProgressTqdm._callback = on_progress
        ProgressTqdm._last_percent = -1
        tqdm_module.tqdm = ProgressTqdm

        whisper_transcribe_mod = sys.modules.get('whisper.transcribe')
        original_whisper_tqdm = None
        if whisper_transcribe_mod and hasattr(whisper_transcribe_mod, 'tqdm'):
            original_whisper_tqdm = whisper_transcribe_mod.tqdm.tqdm
            whisper_transcribe_mod.tqdm.tqdm = ProgressTqdm

        # Lazy load model (with tqdm wrapper active for download progress)
        if self.model is None:
            model_cached = check_whisper_model_cached(self.model_name)
            if not model_cached and on_status:
                on_status('downloading_model')
            elif on_status:
                on_status('loading_model')
            try:
                import torch
                if torch.cuda.is_available():
                    device = "cuda"
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    device = "mps"
                else:
                    device = "cpu"
                self.model = whisper.load_model(self.model_name, device=device)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load Whisper model '{self.model_name}': {e}"
                )
            if on_status:
                on_status('model_ready')
            ProgressTqdm._last_percent = -1

        try:
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                verbose=False
            )

            if self._cancelled:
                raise RuntimeError("Transcription cancelled")

            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{audio_path.stem}.{output_format}"
            else:
                output_path = audio_path.with_suffix(f'.{output_format}')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['text'].strip())

            if on_progress:
                on_progress(100)

            if callback:
                callback(str(output_path))

            return output_path

        finally:
            tqdm_module.tqdm = original_tqdm
            ProgressTqdm._callback = None

            if original_whisper_tqdm is not None:
                whisper_transcribe_mod.tqdm.tqdm = original_whisper_tqdm

            self.is_transcribing = False

    def transcribe_async(
        self,
        audio_path: str | Path,
        language: str = 'German',
        output_format: str = 'txt',
        on_complete: Optional[Callable[[Path], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> threading.Thread:
        """
        Transcribe audio file asynchronously.

        Args:
            audio_path: Path to audio file
            language: Language of the audio
            output_format: Output format
            on_complete: Callback when transcription is done
            on_error: Callback when error occurs

        Returns:
            Thread object handling the transcription
        """
        def run():
            try:
                result = self.transcribe(audio_path, language, output_format)
                if on_complete:
                    on_complete(result)
            except Exception as e:
                if on_error:
                    on_error(str(e))

        thread = threading.Thread(target=run)
        thread.start()
        return thread

    def cancel(self):
        """Cancel ongoing transcription."""
        self._cancelled = True
        self.is_transcribing = False
        # Terminate system whisper subprocess if running
        if self._process is not None:
            try:
                self._process.terminate()
            except OSError:
                pass


def extract_audio_from_video(video_path: str | Path, output_format: str = 'mp3') -> Path:
    """
    Extract audio from video file using ffmpeg.

    Args:
        video_path: Path to video file (mp4, mkv, avi, etc.)
        output_format: Output audio format (mp3, wav)

    Returns:
        Path to extracted audio file
    """
    video_path = Path(video_path)
    audio_path = video_path.with_suffix(f'.{output_format}')

    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-vn',
        '-acodec', 'libmp3lame' if output_format == 'mp3' else 'pcm_s16le',
        '-q:a', '4',
        '-y',
        str(audio_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return audio_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio extraction failed: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg or place ffmpeg.exe in bundled_ffmpeg/.")


def check_whisper_installed() -> bool:
    """Check if Whisper is installed and available."""
    try:
        import whisper
        return True
    except ImportError:
        return False


def check_whisper_model_cached(model_name: str = 'small') -> bool:
    """Check if the Whisper model is already downloaded and complete."""
    # Minimum expected file sizes in bytes (approximate)
    MODEL_MIN_SIZES = {
        'tiny': 70_000_000,
        'base': 130_000_000,
        'small': 450_000_000,
        'medium': 1_400_000_000,
        'large': 2_800_000_000,
    }
    try:
        import whisper
        import os
        url = whisper._MODELS.get(model_name)
        if url is None:
            return False
        # Check default cache location
        default_cache = os.path.join(os.path.expanduser("~"), ".cache")
        download_root = os.path.join(os.getenv("XDG_CACHE_HOME", default_cache), "whisper")
        expected = os.path.join(download_root, os.path.basename(url))
        if not os.path.exists(expected):
            return False
        # Verify file is not incomplete (partial download)
        file_size = os.path.getsize(expected)
        min_size = MODEL_MIN_SIZES.get(model_name, 50_000_000)
        return file_size >= min_size
    except Exception:
        return False


if __name__ == "__main__":
    if check_whisper_installed():
        print("Whisper is installed")
    else:
        print("Whisper is not installed")
        print("  Install with: pip install -U openai-whisper")
