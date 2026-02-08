"""
Audio capture module for Record & Transcribe.
Handles microphone and system audio (WASAPI Loopback) recording.
"""

import sounddevice as sd
import numpy as np
import wave
import threading
import queue
from datetime import datetime
from pathlib import Path


class AudioCapture:
    """Captures audio from microphone and/or system audio (WASAPI Loopback)."""

    SAMPLE_RATE = 44100
    OUTPUT_CHANNELS = 2  # Always output stereo
    DTYPE = np.int16

    def __init__(self):
        self.is_recording = False
        self.mic_stream = None
        self.loopback_stream = None
        self.mic_queue = queue.Queue()
        self.loopback_queue = queue.Queue()
        self.recording_thread = None
        self.output_file = None
        self.wave_file = None
        self.mic_channels = 1
        self.loopback_channels = 2
        # Separate levels for mic and loopback
        self.mic_level = 0
        self.loopback_level = 0
        # Track which sources are active
        self.mic_active = False
        self.loopback_active = False
        # Preview mode (level monitoring without recording)
        self.is_previewing = False

    @staticmethod
    def get_input_devices():
        """Get list of available input devices (microphones)."""
        devices = sd.query_devices()
        input_devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'is_loopback': 'loopback' in device['name'].lower()
                })
        return input_devices

    @staticmethod
    def get_loopback_devices():
        """Get WASAPI loopback devices for system audio capture."""
        devices = sd.query_devices()
        loopback_devices = []
        for i, device in enumerate(devices):
            name_lower = device['name'].lower()
            if 'loopback' in name_lower or 'stereo mix' in name_lower:
                loopback_devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels']
                })

        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0 and device['max_input_channels'] > 0:
                if not any(d['index'] == i for d in loopback_devices):
                    if 'speaker' in device['name'].lower() or 'headphone' in device['name'].lower():
                        loopback_devices.append({
                            'index': i,
                            'name': f"{device['name']} (Loopback)",
                            'channels': min(device['max_input_channels'], 2)
                        })

        return loopback_devices

    @staticmethod
    def _peak_to_level(peak):
        """Convert peak amplitude to a 0-100 meter level using dB scaling."""
        if peak < 1:
            return 0
        # Convert to dB (relative to int16 max)
        db = 20 * np.log10(peak / 32768)
        # Map -60dB..0dB to 0..100
        level = max(0, min(100, int((db + 60) / 60 * 100)))
        return level

    def _mic_callback(self, indata, frames, time, status):
        """Callback for microphone stream."""
        if status:
            print(f"Mic callback status: {status}")

        peak = np.max(np.abs(indata))
        self.mic_level = self._peak_to_level(peak)

        if self.is_recording:
            if self.mic_channels == 1 and indata.shape[1] == 1:
                stereo_data = np.column_stack((indata, indata))
                self.mic_queue.put(stereo_data.copy())
            else:
                self.mic_queue.put(indata.copy())

    def _loopback_callback(self, indata, frames, time, status):
        """Callback for loopback/system audio stream."""
        if status:
            print(f"Loopback callback status: {status}")

        peak = np.max(np.abs(indata))
        self.loopback_level = self._peak_to_level(peak)

        if self.is_recording:
            if self.loopback_channels == 1 and indata.shape[1] == 1:
                stereo_data = np.column_stack((indata, indata))
                self.loopback_queue.put(stereo_data.copy())
            else:
                self.loopback_queue.put(indata.copy())

    def _recording_loop(self):
        """Main recording loop - mixes and writes audio data to file."""
        while self.is_recording or not self.mic_queue.empty() or not self.loopback_queue.empty():
            mic_data = None
            loopback_data = None

            if self.mic_active:
                try:
                    mic_data = self.mic_queue.get(timeout=0.1)
                except queue.Empty:
                    pass

            if self.loopback_active:
                try:
                    loopback_data = self.loopback_queue.get(timeout=0.1)
                except queue.Empty:
                    pass

            if mic_data is not None and loopback_data is not None:
                mic_float = mic_data.astype(np.float32)
                loopback_float = loopback_data.astype(np.float32)
                len_mic = mic_float.shape[0]
                len_loop = loopback_float.shape[0]
                if len_mic < len_loop:
                    mic_float = np.pad(mic_float, ((0, len_loop - len_mic), (0, 0)))
                elif len_loop < len_mic:
                    loopback_float = np.pad(loopback_float, ((0, len_mic - len_loop), (0, 0)))
                mixed = (mic_float + loopback_float) / 2
                mixed = np.clip(mixed, -32768, 32767).astype(np.int16)
                if self.wave_file:
                    self.wave_file.writeframes(mixed.tobytes())
            elif mic_data is not None:
                if self.wave_file:
                    self.wave_file.writeframes(mic_data.tobytes())
            elif loopback_data is not None:
                if self.wave_file:
                    self.wave_file.writeframes(loopback_data.tobytes())

    def start_recording(self, mic_device_index=None, loopback_device_index=None, output_dir=None):
        """
        Start recording audio from mic and/or system audio.

        Args:
            mic_device_index: Index of microphone device (optional)
            loopback_device_index: Index of loopback device for system audio (optional)
            output_dir: Directory to save recordings

        Returns:
            Path to the output WAV file
        """
        if self.is_recording:
            raise RuntimeError("Already recording")

        if output_dir is None:
            output_dir = Path.home() / "Documents" / "Record & Transcribe"
        else:
            output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.output_file = output_dir / f"{timestamp}.wav"

        self.mic_active = False
        self.loopback_active = False
        self.mic_level = 0
        self.loopback_level = 0

        self.wave_file = wave.open(str(self.output_file), 'wb')
        self.wave_file.setnchannels(self.OUTPUT_CHANNELS)
        self.wave_file.setsampwidth(2)
        self.wave_file.setframerate(self.SAMPLE_RATE)

        self.is_recording = True

        if mic_device_index is not None:
            try:
                device_info = sd.query_devices(mic_device_index)
                self.mic_channels = min(device_info['max_input_channels'], 2)
                self.mic_stream = sd.InputStream(
                    device=mic_device_index,
                    samplerate=self.SAMPLE_RATE,
                    channels=self.mic_channels,
                    dtype=self.DTYPE,
                    callback=self._mic_callback
                )
                self.mic_stream.start()
                self.mic_active = True
            except Exception as e:
                self.is_recording = False
                self.wave_file.close()
                raise RuntimeError(f"Failed to start microphone stream: {e}")

        if loopback_device_index is not None:
            try:
                device_info = sd.query_devices(loopback_device_index)
                self.loopback_channels = min(device_info['max_input_channels'], 2)
                self.loopback_stream = sd.InputStream(
                    device=loopback_device_index,
                    samplerate=self.SAMPLE_RATE,
                    channels=self.loopback_channels,
                    dtype=self.DTYPE,
                    callback=self._loopback_callback
                )
                self.loopback_stream.start()
                self.loopback_active = True
            except Exception as e:
                if self.mic_stream:
                    self.mic_stream.stop()
                    self.mic_stream.close()
                    self.mic_stream = None
                self.is_recording = False
                self.wave_file.close()
                raise RuntimeError(f"Failed to start loopback stream: {e}")

        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.start()

        return self.output_file

    def stop_recording(self):
        """
        Stop recording and return the path to the recorded file.

        Returns:
            Path to the recorded WAV file
        """
        if not self.is_recording:
            return None

        self.is_recording = False

        if self.mic_stream:
            self.mic_stream.stop()
            self.mic_stream.close()
            self.mic_stream = None

        if self.loopback_stream:
            self.loopback_stream.stop()
            self.loopback_stream.close()
            self.loopback_stream = None

        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
            self.recording_thread = None

        if self.wave_file:
            self.wave_file.close()
            self.wave_file = None

        return self.output_file

    def get_recording_duration(self):
        """Get current recording duration in seconds."""
        if self.wave_file and self.is_recording:
            frames = self.wave_file.getnframes() if hasattr(self.wave_file, 'getnframes') else 0
            return frames / self.SAMPLE_RATE
        return 0

    def get_current_level(self):
        """Get current audio levels (0-100) for visualization.

        Returns:
            tuple: (mic_level, loopback_level)
        """
        return self.mic_level, self.loopback_level

    def start_preview(self, mic_device_index=None, loopback_device_index=None):
        """
        Start preview mode - streams audio for level monitoring without recording.

        Args:
            mic_device_index: Index of microphone device (optional)
            loopback_device_index: Index of loopback device (optional)
        """
        self.stop_preview()

        self.is_previewing = True
        self.mic_level = 0
        self.loopback_level = 0

        if mic_device_index is not None:
            try:
                device_info = sd.query_devices(mic_device_index)
                self.mic_channels = min(device_info['max_input_channels'], 2)
                self.mic_stream = sd.InputStream(
                    device=mic_device_index,
                    samplerate=self.SAMPLE_RATE,
                    channels=self.mic_channels,
                    dtype=self.DTYPE,
                    callback=self._mic_callback
                )
                self.mic_stream.start()
                self.mic_active = True
            except Exception as e:
                print(f"Failed to start mic preview: {e}")

        if loopback_device_index is not None:
            try:
                device_info = sd.query_devices(loopback_device_index)
                self.loopback_channels = min(device_info['max_input_channels'], 2)
                self.loopback_stream = sd.InputStream(
                    device=loopback_device_index,
                    samplerate=self.SAMPLE_RATE,
                    channels=self.loopback_channels,
                    dtype=self.DTYPE,
                    callback=self._loopback_callback
                )
                self.loopback_stream.start()
                self.loopback_active = True
            except Exception as e:
                print(f"Failed to start loopback preview: {e}")

    def stop_preview(self):
        """Stop preview mode and close streams."""
        if not self.is_previewing:
            return

        self.is_previewing = False

        if self.mic_stream:
            try:
                self.mic_stream.stop()
                self.mic_stream.close()
            except Exception:
                pass
            self.mic_stream = None

        if self.loopback_stream:
            try:
                self.loopback_stream.stop()
                self.loopback_stream.close()
            except Exception:
                pass
            self.loopback_stream = None

        self.mic_active = False
        self.loopback_active = False
        self.mic_level = 0
        self.loopback_level = 0


def convert_to_mp3(wav_path, delete_wav=True):
    """
    Convert WAV file to MP3.

    Args:
        wav_path: Path to WAV file
        delete_wav: Whether to delete the WAV file after conversion

    Returns:
        Path to the MP3 file
    """
    from pydub import AudioSegment

    wav_path = Path(wav_path)
    mp3_path = wav_path.with_suffix('.mp3')

    audio = AudioSegment.from_wav(str(wav_path))
    audio.export(str(mp3_path), format='mp3', bitrate='128k')

    if delete_wav:
        wav_path.unlink()

    return mp3_path


if __name__ == "__main__":
    print("=== Input Devices (Microphones) ===")
    for device in AudioCapture.get_input_devices():
        print(f"  [{device['index']}] {device['name']} ({device['channels']} ch)")

    print("\n=== Loopback Devices (System Audio) ===")
    for device in AudioCapture.get_loopback_devices():
        print(f"  [{device['index']}] {device['name']} ({device['channels']} ch)")
