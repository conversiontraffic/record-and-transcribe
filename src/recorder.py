"""
Record & Transcribe - Simple GUI for recording and transcribing audio.
Records microphone and/or system audio, with optional automatic transcription.
"""

import sys
import os
import subprocess
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.style import ThemeDefinition, Colors
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time
import json
from pathlib import Path

from i18n import t, set_language, get_language
from audio_capture import AudioCapture, convert_to_mp3
from transcriber import Transcriber, check_whisper_installed, check_whisper_model_cached, extract_audio_from_video
from widgets import RoundedButton
from update_checker import check_for_updates, download_update


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent.parent / relative_path


def get_config_dir():
    """Get config directory. Uses AppData when installed in Program Files, otherwise next to exe."""
    if hasattr(sys, '_MEIPASS'):
        exe_dir = Path(sys.executable).parent
        # If installed in a protected directory, use AppData for config
        protected_prefixes = [
            os.environ.get('ProgramFiles', ''),
            os.environ.get('ProgramFiles(x86)', ''),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
        ]
        exe_str = str(exe_dir).lower()
        for prefix in protected_prefixes:
            if prefix and exe_str.startswith(prefix.lower()):
                appdata_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / 'Record & Transcribe'
                appdata_dir.mkdir(parents=True, exist_ok=True)
                return appdata_dir
        return exe_dir
    return Path(__file__).parent.parent


def setup_ffmpeg():
    """Add bundled FFmpeg to PATH if available."""
    ffmpeg_dir = get_resource_path('bundled_ffmpeg')
    if ffmpeg_dir.exists():
        os.environ['PATH'] = str(ffmpeg_dir) + os.pathsep + os.environ.get('PATH', '')


# Setup FFmpeg before anything else
setup_ffmpeg()

# Paths
CONFIG_FILE = get_config_dir() / 'config.json'
DEFAULT_OUTPUT_DIR = Path.home() / 'Documents' / 'Record & Transcribe'
LOGO_PATH = get_resource_path('assets' / Path('logo.png'))

# Branding
APP_NAME = "Record & Transcribe"
APP_VERSION = "0.1.0"
APP_SUBTITLE = "by conversion-traffic.de"

# Brand colors
BRAND_DARK_BLUE = '#012b45'
BRAND_GOLD = '#FFD700'
BRAND_AMBER = '#FFB300'

# Valid themes (only our custom themes are allowed)
VALID_THEMES = {'ct-dark', 'ct-light'}


def register_brand_themes(style):
    """Register custom dark and light themes with brand colors."""
    style.register_theme(ThemeDefinition(
        name='ct-dark',
        themetype='dark',
        colors=Colors(
            primary='#1a5276',
            secondary='#1a4a6e',
            success='#28a745',
            info='#2196F3',
            warning='#FFB300',
            danger='#e74c3c',
            light='#ecf0f1',
            dark='#012b45',
            bg='#0d1b2a',
            fg='#e0e0e0',
            selectbg='#1a5276',
            selectfg='#ffffff',
            border='#1a3a5c',
            inputbg='#132d46',
            inputfg='#e0e0e0',
            active='#1a5276'
        )
    ))
    style.register_theme(ThemeDefinition(
        name='ct-light',
        themetype='light',
        colors=Colors(
            primary='#012b45',
            secondary='#6c757d',
            success='#28a745',
            info='#2196F3',
            warning='#FFB300',
            danger='#dc3545',
            light='#f8f9fa',
            dark='#012b45',
            bg='#ffffff',
            fg='#012b45',
            selectbg='#012b45',
            selectfg='#ffffff',
            border='#ced4da',
            inputbg='#ffffff',
            inputfg='#012b45',
            active='#e9ecef'
        )
    ))


class RecordAndTranscribeApp:
    """Main application window."""

    # Map UI language display names to i18n codes
    UI_LANGUAGES = {
        'English': 'en',
        'Deutsch': 'de'
    }

    # Brand theme names
    THEME_DARK = 'ct-dark'
    THEME_LIGHT = 'ct-light'

    def __init__(self, root):
        self.root = root

        # Load config (need language before building UI)
        self.config = self._load_config()

        # Apply saved UI language
        ui_lang = self.config.get('ui_language', 'en')
        set_language(ui_lang)

        # Initialize components
        self.audio_capture = AudioCapture()
        self.transcriber = Transcriber(model='small')

        # State
        self.is_recording = False
        self.is_transcribing = False
        self.recording_start_time = None
        self.timer_thread = None
        self.current_wav_file = None
        self.level_update_id = None

        # Device lists
        self.mic_devices = []
        self.loopback_devices = []

        self._create_menu()
        self._create_widgets()
        self._refresh_devices()

        # Start preview for live levels
        self._start_preview()
        self._update_audio_level_preview()

        # Cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Check for updates (non-blocking)
        self._check_for_updates()

    def _on_close(self):
        """Clean up all resources when window is closed."""
        # Stop audio preview
        self._stop_preview()
        # Stop recording if active
        if self.is_recording:
            self.is_recording = False
            try:
                self.audio_capture.stop_recording()
            except Exception:
                pass
        # Cancel transcription if active
        if self.is_transcribing:
            self.transcriber.cancel()
        self.root.destroy()
        # Force exit to kill any remaining threads
        os._exit(0)

    @staticmethod
    def _open_in_explorer(file_path):
        """Open the containing folder in Explorer and select the file."""
        try:
            subprocess.Popen(['explorer', '/select,', str(Path(file_path))])
        except Exception:
            pass

    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('menu.file'), menu=file_menu)
        file_menu.add_command(label=t('menu.transcribe_file'), command=self._transcribe_file)
        file_menu.add_separator()
        file_menu.add_command(label=t('menu.exit'), command=self._on_close)

        # Settings menu with language selection
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('settings.frame_title'), menu=settings_menu)

        lang_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=t('settings.ui_language'), menu=lang_menu)

        for display_name, code in self.UI_LANGUAGES.items():
            lang_menu.add_command(
                label=display_name,
                command=lambda c=code: self._set_ui_language(c)
            )

        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=t('settings.theme'), menu=theme_menu)
        theme_menu.add_command(
            label=t('settings.theme_light'),
            command=lambda: self._set_theme(self.THEME_LIGHT)
        )
        theme_menu.add_command(
            label=t('settings.theme_dark'),
            command=lambda: self._set_theme(self.THEME_DARK)
        )

        # Help menu with system check
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t('menu.help'), menu=help_menu)
        help_menu.add_command(label=t('menu.system_check'), command=self._show_system_check)
        help_menu.add_command(label=t('menu.install_gpu'), command=self._install_gpu_support)
        help_menu.add_separator()
        help_menu.add_command(label=t('menu.check_updates'), command=self._manual_update_check)
        help_menu.add_command(label=t('menu.about'), command=self._show_about)

    def _check_cuda_available(self):
        """Check if CUDA GPU is available via PyTorch."""
        try:
            import torch
            return torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        except Exception:
            return False, None

    def _show_system_check(self):
        """Show a dialog with system status checks."""
        import shutil

        checks = []

        # FFmpeg
        ffmpeg_ok = shutil.which('ffmpeg') is not None
        checks.append((t('syscheck.ffmpeg'), ffmpeg_ok, t('syscheck.ffmpeg_desc')))

        # Whisper
        whisper_ok = check_whisper_installed()
        checks.append((t('syscheck.whisper'), whisper_ok, t('syscheck.whisper_desc')))

        # Whisper Model
        model_ok = check_whisper_model_cached(self.transcriber.model_name)
        model_desc = t('syscheck.model_desc', model=self.transcriber.model_name)
        checks.append((t('syscheck.model'), model_ok, model_desc))

        # System Audio (Loopback)
        loopback_ok = len(AudioCapture.get_loopback_devices()) > 0
        checks.append((t('syscheck.loopback'), loopback_ok, t('syscheck.loopback_desc')))

        # GPU/CUDA
        cuda_ok, gpu_name = self._check_cuda_available()
        if cuda_ok and gpu_name:
            checks.append((f'{t("syscheck.gpu")} ({gpu_name})', True, ''))
        elif hasattr(sys, '_MEIPASS'):
            checks.append((t('syscheck.gpu'), False, t('syscheck.gpu_exe_desc')))
        else:
            checks.append((t('syscheck.gpu'), False, t('syscheck.gpu_desc')))

        # Build message
        lines = [t('syscheck.title'), '']
        for name, ok, desc in checks:
            icon = '\u2705' if ok else '\u274C'
            lines.append(f'{icon}  {name}')
            if not ok and desc:
                lines.append(f'      {desc}')
        lines.append('')
        lines.append(t('syscheck.output_dir', path=self.output_dir_var.get()))

        messagebox.showinfo(t('menu.system_check'), '\n'.join(lines))

    def _install_gpu_support(self):
        """Install CUDA PyTorch for GPU-accelerated transcription."""
        # Check if already available
        cuda_ok, gpu_name = self._check_cuda_available()
        if cuda_ok:
            messagebox.showinfo(
                t('menu.install_gpu'),
                t('gpu.already_installed', gpu=gpu_name)
            )
            return

        # Check if running from .exe (can't pip install)
        if hasattr(sys, '_MEIPASS'):
            messagebox.showinfo(
                t('menu.install_gpu'),
                t('gpu.exe_not_supported')
            )
            return

        # Confirm installation
        if not messagebox.askyesno(
            t('menu.install_gpu'),
            t('gpu.confirm_install')
        ):
            return

        self.status_var.set(t('gpu.installing'))
        self.root.update()

        def install():
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install',
                     'torch', 'torchvision', 'torchaudio',
                     '--index-url', 'https://download.pytorch.org/whl/cu121'],
                    capture_output=True, text=True, timeout=600
                )
                if result.returncode == 0:
                    self.root.after(0, lambda: (
                        self.status_var.set(t('status.ready')),
                        messagebox.showinfo(
                            t('menu.install_gpu'),
                            t('gpu.install_success')
                        )
                    ))
                else:
                    self.root.after(0, lambda: (
                        self.status_var.set(t('status.ready')),
                        messagebox.showerror(
                            t('dialog.error'),
                            t('gpu.install_failed', error=result.stderr[-500:] if result.stderr else 'Unknown error')
                        )
                    ))
            except Exception as e:
                self.root.after(0, lambda: (
                    self.status_var.set(t('status.ready')),
                    messagebox.showerror(t('dialog.error'), str(e))
                ))

        threading.Thread(target=install, daemon=True).start()

    def _show_about(self):
        """Show About dialog with version, description, and license."""
        lines = [
            f"{APP_NAME} v{APP_VERSION}",
            f"{t('about.author')}",
            "",
            t('about.description'),
            "",
            t('about.license'),
        ]
        messagebox.showinfo(t('menu.about'), '\n'.join(lines))

    def _check_for_updates(self, manual=False):
        """Check for updates in background thread."""
        def on_result(version, url, filename):
            if version and url and filename:
                # Download the installer in background
                self.root.after(0, lambda: self.status_var.set(t('update.downloading')))
                download_update(
                    url, filename,
                    on_complete=lambda path: self.root.after(
                        0, lambda: self._show_update_dialog(version, path)
                    ),
                    on_error=lambda err: self.root.after(
                        0, lambda: self.status_var.set(t('status.ready'))
                    )
                )
            elif manual:
                self.root.after(0, lambda: messagebox.showinfo(
                    t('update.title'),
                    t('update.up_to_date', version=APP_VERSION)
                ))

        check_for_updates(APP_VERSION, on_result)

    def _manual_update_check(self):
        """Manually trigger update check from menu."""
        self._check_for_updates(manual=True)

    def _show_update_dialog(self, version, installer_path):
        """Show dialog offering to install downloaded update."""
        self.status_var.set(t('status.ready'))
        result = messagebox.askyesno(
            t('update.title'),
            t('update.ready', version=version)
        )
        if result:
            try:
                subprocess.Popen([installer_path])
                self._on_close()
            except Exception:
                pass

    def _load_config(self):
        """Load configuration from file."""
        default_config = {
            'output_dir': str(DEFAULT_OUTPUT_DIR),
            'auto_transcribe': True,
            'language': 'Auto',
            'ui_language': 'en',
            'theme': 'ct-dark'
        }
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    default_config.update(saved)
            except Exception:
                pass
        # Validate theme - fall back to ct-dark if invalid
        if default_config.get('theme') not in VALID_THEMES:
            default_config['theme'] = 'ct-dark'
        return default_config

    def _save_config(self):
        """Save configuration to file."""
        self.config['output_dir'] = self.output_dir_var.get()
        self.config['auto_transcribe'] = self.auto_transcribe_var.get()
        self.config['language'] = self.lang_var.get()
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _browse_output_dir(self):
        """Open folder browser dialog."""
        current = self.output_dir_var.get()
        if not Path(current).exists():
            current = str(DEFAULT_OUTPUT_DIR)

        folder = filedialog.askdirectory(
            initialdir=current,
            title=t('output.browse_title')
        )
        if folder:
            self.output_dir_var.set(folder)
            self._save_config()

    def _get_language_labels(self):
        """Get transcription language labels based on current UI language."""
        return {
            t('lang.auto'): None,
            t('lang.german'): 'German',
            t('lang.english'): 'English',
            t('lang.french'): 'French',
            t('lang.spanish'): 'Spanish',
            t('lang.italian'): 'Italian',
        }

    def _create_widgets(self):
        """Create all GUI widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Logo and Title (left-aligned)
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15), anchor=tk.W)

        try:
            from PIL import Image, ImageTk
            if LOGO_PATH.exists():
                img = Image.open(LOGO_PATH)
                # Crop to icon only (left ~25% is the teardrop symbol)
                icon_width = int(img.width * 0.25)
                img = img.crop((0, 0, icon_width, img.height))
                max_height = 35
                ratio = max_height / img.height
                new_width = int(img.width * ratio)
                img = img.resize((new_width, max_height), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(img)
                logo_label = ttk.Label(header_frame, image=self.logo_photo)
                logo_label.pack(side=tk.LEFT, padx=(0, 12))
        except Exception:
            pass

        title_container = ttk.Frame(header_frame)
        title_container.pack(side=tk.LEFT)

        title_label = ttk.Label(
            title_container,
            text=APP_NAME,
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(
            title_container,
            text=APP_SUBTITLE,
            font=('Segoe UI', 9),
            foreground='gray'
        )
        subtitle_label.pack(anchor=tk.W)

        # Device selection frame
        device_frame = ttk.LabelFrame(main_frame, text=t('devices.frame_title'))
        device_frame.pack(fill=tk.X, pady=(0, 15))

        device_inner = ttk.Frame(device_frame, padding=10)
        device_inner.pack(fill=tk.X, expand=True)

        # Microphone selection
        mic_frame = ttk.Frame(device_inner)
        mic_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mic_frame, text=t('devices.microphone'), width=12).pack(side=tk.LEFT)
        self.mic_var = tk.StringVar()
        self.mic_combo = ttk.Combobox(
            mic_frame,
            textvariable=self.mic_var,
            state='readonly',
            width=30
        )
        self.mic_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.mic_combo.bind('<<ComboboxSelected>>', lambda e: self._on_device_change())

        # System audio selection
        sys_frame = ttk.Frame(device_inner)
        sys_frame.pack(fill=tk.X)

        ttk.Label(sys_frame, text=t('devices.system_audio'), width=12).pack(side=tk.LEFT)
        self.sys_var = tk.StringVar()
        self.sys_combo = ttk.Combobox(
            sys_frame,
            textvariable=self.sys_var,
            state='readonly',
            width=30
        )
        self.sys_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.sys_combo.bind('<<ComboboxSelected>>', lambda e: self._on_device_change())

        # Audio level meters
        mic_level_frame = ttk.Frame(device_inner)
        mic_level_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(mic_level_frame, text=t('devices.mic_level'), width=12).pack(side=tk.LEFT)
        self.mic_level_bar = ttk.Progressbar(
            mic_level_frame,
            orient='horizontal',
            length=200,
            mode='determinate',
            maximum=100,
            bootstyle="success"
        )
        self.mic_level_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        sys_level_frame = ttk.Frame(device_inner)
        sys_level_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(sys_level_frame, text=t('devices.sys_level'), width=12).pack(side=tk.LEFT)
        self.sys_level_bar = ttk.Progressbar(
            sys_level_frame,
            orient='horizontal',
            length=200,
            mode='determinate',
            maximum=100,
            bootstyle="success"
        )
        self.sys_level_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Refresh button
        refresh_btn = RoundedButton(
            device_inner,
            text=t('devices.refresh'),
            command=self._refresh_devices,
            bg_color='#1a4a6e',
            fg_color='#e0e0e0',
            corner_radius=12,
            height=34,
            font=('Segoe UI', 9)
        )
        refresh_btn.pack(fill=tk.X, pady=(10, 0))
        self._rounded_buttons = [refresh_btn]

        # Status label
        self.status_var = tk.StringVar(value=t('status.ready'))
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 11)
        )
        self.status_label.pack(pady=(5, 10))

        # Record button
        self.record_btn = RoundedButton(
            main_frame,
            text=t('button.start_recording'),
            command=self._toggle_recording,
            bg_color='#e74c3c',
            fg_color='#ffffff',
            corner_radius=20,
            height=48,
            font=('Segoe UI', 12, 'bold')
        )
        self.record_btn.pack(fill=tk.X, pady=10)
        self._rounded_buttons.append(self.record_btn)

        # Duration label
        self.duration_var = tk.StringVar(value=t('duration.label', time='00:00:00'))
        self.duration_label = ttk.Label(
            main_frame,
            textvariable=self.duration_var,
            font=('Segoe UI', 10)
        )
        self.duration_label.pack(pady=(5, 15))

        # Output folder frame
        output_frame = ttk.LabelFrame(main_frame, text=t('output.frame_title'))
        output_frame.pack(fill=tk.X, pady=(0, 10))

        output_inner = ttk.Frame(output_frame, padding=10)
        output_inner.pack(fill=tk.X)

        self.output_dir_var = tk.StringVar(value=self.config.get('output_dir', str(DEFAULT_OUTPUT_DIR)))
        output_entry = ttk.Entry(
            output_inner,
            textvariable=self.output_dir_var,
            state='readonly',
            width=35
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = RoundedButton(
            output_inner,
            text="...",
            command=self._browse_output_dir,
            bg_color='#1a4a6e',
            fg_color='#e0e0e0',
            corner_radius=10,
            height=30,
            width=40,
            font=('Segoe UI', 10)
        )
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        self._rounded_buttons.append(browse_btn)

        # Transcription options frame
        trans_frame = ttk.LabelFrame(main_frame, text=t('transcription.frame_title'))
        trans_frame.pack(fill=tk.X, pady=(0, 10))

        trans_inner = ttk.Frame(trans_frame, padding=10)
        trans_inner.pack(fill=tk.X, expand=True)

        # Auto-transcribe checkbox
        self.auto_transcribe_var = tk.BooleanVar(value=self.config.get('auto_transcribe', False))
        trans_check = ttk.Checkbutton(
            trans_inner,
            text=t('transcription.auto_transcribe'),
            variable=self.auto_transcribe_var,
            command=self._save_config
        )
        trans_check.pack(anchor=tk.W)

        # Language selection
        lang_frame = ttk.Frame(trans_inner)
        lang_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(lang_frame, text=t('transcription.language')).pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.config.get('language', t('lang.auto')))
        lang_labels = self._get_language_labels()
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=list(lang_labels.keys()),
            state='readonly',
            width=15
        )
        lang_combo.pack(side=tk.LEFT, padx=(10, 0))
        lang_combo.bind('<<ComboboxSelected>>', lambda e: self._save_config())

        # Model info
        model_label = ttk.Label(
            trans_inner,
            text=t('transcription.model', model=self.transcriber.model_name),
            font=('Segoe UI', 8),
            foreground='gray'
        )
        model_label.pack(anchor=tk.W, pady=(8, 0))

        # Transcription progress bar (hidden initially)
        self.trans_progress_frame = ttk.Frame(trans_inner)

        self.trans_progress_label = ttk.Label(
            self.trans_progress_frame,
            text=t('transcription.progress', percent=0),
            font=('Segoe UI', 9)
        )
        self.trans_progress_label.pack(anchor=tk.W)

        self.trans_progress_bar = ttk.Progressbar(
            self.trans_progress_frame,
            orient='horizontal',
            length=200,
            mode='determinate',
            maximum=100,
            bootstyle="info-striped"
        )
        self.trans_progress_bar.pack(fill=tk.X, pady=(5, 5))

        self.cancel_trans_btn = RoundedButton(
            self.trans_progress_frame,
            text=t('transcription.cancel'),
            command=self._cancel_transcription,
            bg_color='#e74c3c',
            fg_color='#ffffff',
            corner_radius=12,
            height=34,
            font=('Segoe UI', 9)
        )
        self.cancel_trans_btn.pack(fill=tk.X)
        self._rounded_buttons.append(self.cancel_trans_btn)

        # Check whisper installation and model status
        if not check_whisper_installed():
            self.auto_transcribe_var.set(False)
            trans_check.config(state='disabled')
            warning_label = ttk.Label(
                trans_inner,
                text=t('transcription.whisper_not_installed'),
                foreground='red'
            )
            warning_label.pack(anchor=tk.W, pady=(5, 0))
        elif not check_whisper_model_cached(self.transcriber.model_name):
            info_label = ttk.Label(
                trans_inner,
                text=t('transcription.model_first_download'),
                foreground='orange',
                wraplength=360,
                font=('Segoe UI', 8)
            )
            info_label.pack(anchor=tk.W, pady=(5, 0))

    def _set_theme(self, theme_name):
        """Switch theme live and save to config."""
        self.root.style.theme_use(theme_name)
        self.config['theme'] = theme_name
        # Update rounded button canvas backgrounds
        for btn in self._rounded_buttons:
            btn.update_theme_bg()
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _set_ui_language(self, lang_code):
        """Set UI language, save config, and show restart message."""
        self.config['ui_language'] = lang_code
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        messagebox.showinfo(
            t('settings.restart_title'),
            t('settings.restart_msg')
        )

    def _refresh_devices(self):
        """Refresh the list of available audio devices."""
        import sounddevice as sd

        self.mic_devices = AudioCapture.get_input_devices()
        non_loopback_mics = [d for d in self.mic_devices if not d.get('is_loopback')]
        mic_names = [t('devices.no_microphone')] + [d['name'] for d in non_loopback_mics]
        self.mic_combo['values'] = mic_names

        # Auto-select default input device
        default_mic_idx = 0
        try:
            default_input = sd.query_devices(kind='input')
            default_name = default_input['name']
            for i, d in enumerate(non_loopback_mics):
                if d['name'] == default_name or default_name in d['name']:
                    default_mic_idx = i + 1
                    break
        except Exception:
            pass
        if default_mic_idx == 0 and len(mic_names) > 1:
            default_mic_idx = 1
        self.mic_combo.current(default_mic_idx)

        # Get loopback devices
        self.loopback_devices = AudioCapture.get_loopback_devices()
        sys_names = [t('devices.no_system_audio')] + [d['name'] for d in self.loopback_devices]
        self.sys_combo['values'] = sys_names

        if len(self.loopback_devices) > 0:
            self.sys_combo.current(1)
        else:
            self.sys_combo.current(0)

        # Restart preview with new devices
        if not self.is_recording:
            self._start_preview()

    def _toggle_recording(self):
        """Start or stop recording."""
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """Start audio recording."""
        mic_index, sys_index = self._get_selected_devices()

        if mic_index is None and sys_index is None:
            messagebox.showwarning(
                t('dialog.no_source_title'),
                t('dialog.no_source_msg')
            )
            return

        try:
            self._stop_preview()

            output_dir = Path(self.output_dir_var.get())
            output_dir.mkdir(parents=True, exist_ok=True)

            self.current_wav_file = self.audio_capture.start_recording(
                mic_device_index=mic_index,
                loopback_device_index=sys_index,
                output_dir=output_dir
            )

            self.is_recording = True
            self.recording_start_time = time.time()

            self.status_var.set(t('status.recording'))
            self.record_btn.configure(text=t('button.stop_recording'), bg_color='#FFB300', fg_color='#012b45')
            self.mic_combo.config(state='disabled')
            self.sys_combo.config(state='disabled')

            self._start_timer()

        except Exception as e:
            messagebox.showerror(
                t('dialog.error'),
                t('dialog.error_start', error=str(e))
            )

    def _stop_recording(self):
        """Stop audio recording."""
        self.is_recording = False

        if self.timer_thread:
            self.timer_thread = None

        wav_file = self.audio_capture.stop_recording()

        self.status_var.set(t('status.processing'))
        self.record_btn.configure(state='disabled')
        self.root.update()

        def process():
            try:
                mp3_file = convert_to_mp3(wav_file, delete_wav=True)

                if self.auto_transcribe_var.get():
                    self.root.after(0, lambda: self.status_var.set(t('status.transcribing')))
                    self.root.after(0, self._show_transcription_progress)

                    def on_progress(percent):
                        self.root.after(0, lambda p=percent: self._update_transcription_progress(p))

                    def on_status(status_key):
                        status_map = {
                            'downloading_model': t('status.downloading_model'),
                            'loading_model': t('status.loading_model'),
                        }
                        msg = status_map.get(status_key)
                        if msg:
                            self.root.after(0, lambda m=msg: self._show_indeterminate_progress(m))
                        if status_key == 'model_ready':
                            self.root.after(0, self._switch_to_determinate_progress)

                    lang_labels = self._get_language_labels()
                    language = lang_labels.get(self.lang_var.get())
                    txt_file = self.transcriber.transcribe(
                        mp3_file,
                        language=language,
                        on_progress=on_progress,
                        on_status=on_status
                    )

                    self.root.after(0, lambda: (
                        messagebox.showinfo(
                            t('dialog.done'),
                            t('dialog.done_recording_transcript', file=mp3_file, transcript=txt_file)
                        ),
                        self._open_in_explorer(txt_file)
                    ))
                else:
                    self.root.after(0, lambda: (
                        messagebox.showinfo(
                            t('dialog.done'),
                            t('dialog.done_recording', file=mp3_file)
                        ),
                        self._open_in_explorer(mp3_file)
                    ))

            except RuntimeError as e:
                error_msg = str(e)
                if "cancelled" in error_msg.lower():
                    pass
                else:
                    self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                        t('dialog.error'),
                        t('dialog.error_processing', error=msg)
                    ))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    t('dialog.error'),
                    t('dialog.error_processing', error=msg)
                ))
            finally:
                self.root.after(0, self._reset_ui)

        threading.Thread(target=process, daemon=True).start()

    def _reset_ui(self):
        """Reset UI to ready state."""
        self.status_var.set(t('status.ready'))
        self.duration_var.set(t('duration.label', time='00:00:00'))
        self.record_btn.configure(text=t('button.start_recording'), state='normal', bg_color='#e74c3c', fg_color='#ffffff')
        self.mic_combo.config(state='readonly')
        self.sys_combo.config(state='readonly')
        self.trans_progress_frame.pack_forget()
        self.is_transcribing = False
        self._start_preview()

    def _show_transcription_progress(self):
        """Show transcription progress UI."""
        self.is_transcribing = True
        self.trans_progress_bar.configure(mode='determinate')
        self.trans_progress_bar['value'] = 0
        self.trans_progress_label.config(text=t('transcription.progress', percent=0))
        self.trans_progress_frame.pack(fill=tk.X, pady=(10, 0))

    def _show_indeterminate_progress(self, status_text):
        """Show animated progress bar for model download/loading."""
        self.is_transcribing = True
        self.trans_progress_bar.configure(mode='indeterminate')
        self.trans_progress_bar.start(15)
        self.trans_progress_label.config(text=status_text)
        self.trans_progress_frame.pack(fill=tk.X, pady=(10, 0))

    def _switch_to_determinate_progress(self):
        """Switch progress bar back to determinate mode after model is ready."""
        self.trans_progress_bar.stop()
        self.trans_progress_bar.configure(mode='determinate')
        self.trans_progress_bar['value'] = 0
        self.trans_progress_label.config(text=t('transcription.progress', percent=0))

    def _update_transcription_progress(self, percent: int):
        """Update transcription progress bar."""
        if str(self.trans_progress_bar.cget('mode')) == 'indeterminate':
            self.trans_progress_bar.stop()
            self.trans_progress_bar.configure(mode='determinate')
        self.trans_progress_bar['value'] = percent
        self.trans_progress_label.config(text=t('transcription.progress', percent=percent))

    def _cancel_transcription(self):
        """Cancel ongoing transcription."""
        if self.is_transcribing:
            self.transcriber.cancel()
            self.status_var.set(t('status.cancelled'))
            self._reset_ui()

    def _start_timer(self):
        """Start the recording duration timer."""
        def update_timer():
            while self.is_recording:
                elapsed = time.time() - self.recording_start_time
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.duration_var.set(t('duration.label', time=time_str))
                time.sleep(0.5)

        self.timer_thread = threading.Thread(target=update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def _get_selected_devices(self):
        """Get currently selected device indices."""
        mic_index = None
        sys_index = None

        mic_selection = self.mic_combo.current()
        if mic_selection > 0:
            non_loopback_mics = [d for d in self.mic_devices if not d.get('is_loopback')]
            if mic_selection - 1 < len(non_loopback_mics):
                mic_index = non_loopback_mics[mic_selection - 1]['index']

        sys_selection = self.sys_combo.current()
        if sys_selection > 0:
            if sys_selection - 1 < len(self.loopback_devices):
                sys_index = self.loopback_devices[sys_selection - 1]['index']

        return mic_index, sys_index

    def _on_device_change(self):
        """Called when device selection changes - restart preview."""
        if not self.is_recording:
            self._start_preview()

    def _start_preview(self):
        """Start audio preview for live level monitoring."""
        mic_index, sys_index = self._get_selected_devices()
        self.audio_capture.start_preview(
            mic_device_index=mic_index,
            loopback_device_index=sys_index
        )

    def _stop_preview(self):
        """Stop audio preview."""
        self.audio_capture.stop_preview()

    def _update_audio_level_preview(self):
        """Update audio level meters."""
        mic_level, sys_level = self.audio_capture.get_current_level()
        self.mic_level_bar['value'] = mic_level
        self.sys_level_bar['value'] = sys_level
        self.level_update_id = self.root.after(50, self._update_audio_level_preview)

    def _transcribe_file(self):
        """Open file dialog and transcribe selected audio/video file."""
        filetypes = [
            (t('filedialog.audio_video'), "*.mp3 *.wav *.mp4 *.mkv *.avi *.m4a *.webm"),
            (t('filedialog.audio'), "*.mp3 *.wav *.m4a"),
            (t('filedialog.video'), "*.mp4 *.mkv *.avi *.webm"),
            (t('filedialog.all'), "*.*")
        ]

        file_path = filedialog.askopenfilename(
            title=t('filedialog.transcribe_title'),
            filetypes=filetypes
        )

        if not file_path:
            return

        file_path = Path(file_path)

        self.status_var.set(t('status.transcribing'))
        self.root.update()

        def process():
            try:
                audio_path = file_path

                video_extensions = {'.mp4', '.mkv', '.avi', '.webm', '.mov'}
                if file_path.suffix.lower() in video_extensions:
                    self.root.after(0, lambda: self.status_var.set(t('status.extracting_audio')))
                    audio_path = extract_audio_from_video(file_path)

                self.root.after(0, lambda: self.status_var.set(t('status.transcribing')))
                self.root.after(0, self._show_transcription_progress)

                def on_progress(percent):
                    self.root.after(0, lambda p=percent: self._update_transcription_progress(p))

                def on_status(status_key):
                    status_map = {
                        'downloading_model': t('status.downloading_model'),
                        'loading_model': t('status.loading_model'),
                    }
                    msg = status_map.get(status_key)
                    if msg:
                        self.root.after(0, lambda m=msg: self._show_indeterminate_progress(m))
                    if status_key == 'model_ready':
                        self.root.after(0, self._switch_to_determinate_progress)

                lang_labels = self._get_language_labels()
                language = lang_labels.get(self.lang_var.get())
                output_dir = self.output_dir_var.get()

                txt_file = self.transcriber.transcribe(
                    audio_path,
                    language=language,
                    output_dir=output_dir,
                    on_progress=on_progress,
                    on_status=on_status
                )

                self.root.after(0, lambda: (
                    messagebox.showinfo(
                        t('dialog.done'),
                        t('dialog.done_transcription', file=txt_file)
                    ),
                    self._open_in_explorer(txt_file)
                ))

            except RuntimeError as e:
                error_msg = str(e)
                if "cancelled" in error_msg.lower():
                    pass
                else:
                    self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                        t('dialog.error'),
                        t('dialog.error_transcription', error=msg)
                    ))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    t('dialog.error'),
                    t('dialog.error_transcription', error=msg)
                ))
            finally:
                self.root.after(0, self._reset_ui)

        threading.Thread(target=process, daemon=True).start()


def main():
    """Main entry point."""
    # Load config to get saved theme
    config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            pass

    # Create window with temporary theme, then switch to brand theme
    root = ttk.Window(
        title=f"{APP_NAME} v{APP_VERSION}",
        themename='darkly',
        size=(420, 720),
        resizable=(False, True)
    )
    root.minsize(420, 600)

    # Register and apply brand themes
    register_brand_themes(root.style)
    theme = config.get('theme', 'ct-dark')
    if theme not in VALID_THEMES:
        theme = 'ct-dark'
    root.style.theme_use(theme)

    # Set window icon from logo
    try:
        from PIL import Image, ImageTk
        if LOGO_PATH.exists():
            img = Image.open(LOGO_PATH)
            icon_img = img.resize((32, 32), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(icon_img)
            root.iconphoto(True, photo)
    except Exception:
        pass

    app = RecordAndTranscribeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
