"""
Internationalization (i18n) module for Record & Transcribe.
Simple dict-based translation system supporting English and German.
"""

_current_language = 'en'

translations = {
    'en': {
        # Menu
        'menu.file': 'File',
        'menu.transcribe_file': 'Transcribe file...',
        'menu.exit': 'Exit',
        'menu.help': 'Help',
        'menu.system_check': 'System Check',
        'menu.about': 'About...',
        'menu.check_updates': 'Check for Updates...',

        # System Check
        'syscheck.title': 'System Status',
        'syscheck.ffmpeg': 'FFmpeg (MP3 conversion)',
        'syscheck.ffmpeg_desc': 'Not found - MP3 conversion may not work',
        'syscheck.whisper': 'Whisper (transcription engine)',
        'syscheck.whisper_desc': 'Not installed - transcription unavailable',
        'syscheck.model': 'Whisper Model',
        'syscheck.model_desc': 'Model "{model}" not yet downloaded (~460 MB)',
        'syscheck.output_dir': 'Output folder: {path}',
        'syscheck.loopback': 'System Audio (Loopback)',
        'syscheck.loopback_desc': 'No loopback device found - install VB-Audio Virtual Cable (free): vb-audio.com/Cable',
        'syscheck.gpu': 'GPU Acceleration (CUDA)',
        'syscheck.gpu_desc': 'No NVIDIA GPU found - using CPU (slower)',
        'syscheck.gpu_exe_desc': 'Not available in .exe version - run from source for GPU support',

        # GPU Installation
        'menu.install_gpu': 'Install GPU Support...',
        'gpu.already_installed': 'GPU support is already active!\nUsing: {gpu}',
        'gpu.exe_not_supported': 'GPU support cannot be installed in the portable .exe version.\n\nTo use GPU acceleration, run from source:\n1. pip install torch --index-url https://download.pytorch.org/whl/cu121\n2. python src/recorder.py',
        'gpu.confirm_install': 'This will install NVIDIA CUDA support for faster transcription (~2.5 GB download).\n\nRequires an NVIDIA GPU with CUDA support.\n\nProceed?',
        'gpu.installing': 'Installing GPU support... This may take a few minutes.',
        'gpu.install_success': 'GPU support installed! Restart the app to use GPU acceleration.',
        'gpu.install_failed': 'GPU installation failed:\n{error}',

        # Audio Sources
        'devices.frame_title': 'Audio Sources',
        'devices.microphone': 'Microphone:',
        'devices.system_audio': 'System Audio:',
        'devices.no_microphone': '(No Microphone)',
        'devices.no_system_audio': '(No System Audio)',
        'devices.mic_level': 'Mic Level:',
        'devices.sys_level': 'Sys Level:',
        'devices.refresh': 'Refresh Devices',

        # Status
        'status.ready': 'Ready',
        'status.recording': 'Recording...',
        'status.processing': 'Processing...',
        'status.transcribing': 'Transcribing...',
        'status.extracting_audio': 'Extracting audio...',
        'status.downloading_model': 'Downloading Whisper model (~460 MB)... Please wait.',
        'status.loading_model': 'Loading Whisper model...',
        'status.cancelled': 'Cancelled',

        # Buttons
        'button.start_recording': 'Start Recording',
        'button.stop_recording': 'Stop Recording',

        # Duration
        'duration.label': 'Duration: {time}',

        # Output folder
        'output.frame_title': 'Output Folder',
        'output.browse_title': 'Choose Output Folder',

        # Transcription
        'transcription.frame_title': 'Transcription',
        'transcription.auto_transcribe': 'Auto-transcribe after recording',
        'transcription.language': 'Language:',
        'transcription.model': 'Model: {model}',
        'transcription.progress': 'Transcribing... {percent}%',
        'transcription.cancel': 'Cancel',
        'transcription.whisper_not_installed': 'Whisper not installed',
        'transcription.model_first_download': 'Note: The Whisper model (~460 MB) will be downloaded on first transcription. Internet connection required.',

        # Transcription language names
        'lang.auto': 'Auto',
        'lang.german': 'German',
        'lang.english': 'English',
        'lang.french': 'French',
        'lang.spanish': 'Spanish',
        'lang.italian': 'Italian',

        # Dialogs
        'dialog.no_source_title': 'No Audio Source',
        'dialog.no_source_msg': 'Please select at least one microphone or system audio source.',
        'dialog.error': 'Error',
        'dialog.error_start': 'Could not start recording:\n{error}',
        'dialog.error_processing': 'Processing failed:\n{error}',
        'dialog.error_transcription': 'Transcription failed:\n{error}',
        'dialog.done': 'Done',
        'dialog.done_recording': 'Recording saved:\n{file}',
        'dialog.done_recording_transcript': 'Recording saved:\n{file}\n\nTranscript:\n{transcript}',
        'dialog.done_transcription': 'Transcript saved:\n{file}',

        # File dialog
        'filedialog.transcribe_title': 'Select File to Transcribe',
        'filedialog.audio_video': 'Audio/Video Files',
        'filedialog.audio': 'Audio Files',
        'filedialog.video': 'Video Files',
        'filedialog.all': 'All Files',

        # About
        'about.description': 'Simple audio recorder with built-in transcription.\nRecord meetings, interviews, or any audio\nand transcribe locally using OpenAI Whisper.',
        'about.license': 'License: GPL-3.0',
        'about.author': 'by conversion-traffic.de',

        # Update
        'update.title': 'Update Available',
        'update.downloading': 'Downloading update...',
        'update.ready': 'Version {version} is ready to install!\n\nInstall now and restart?',
        'update.failed': 'Update check failed.',
        'update.up_to_date': 'You are using the latest version (v{version}).',
        'update.install_btn': 'Install & Restart',
        'update.later_btn': 'Later',

        # Settings
        'settings.frame_title': 'Settings',
        'settings.ui_language': 'Interface:',
        'settings.theme': 'Theme:',
        'settings.theme_light': 'Light',
        'settings.theme_dark': 'Dark',
        'settings.restart_title': 'Restart Required',
        'settings.restart_msg': 'Please restart the application for the language change to take effect.',
    },
    'de': {
        # Menu
        'menu.file': 'Datei',
        'menu.transcribe_file': 'Datei transkribieren...',
        'menu.exit': 'Beenden',
        'menu.help': 'Hilfe',
        'menu.system_check': 'Systemcheck',
        'menu.about': '\u00dcber...',
        'menu.check_updates': 'Nach Updates suchen...',

        # System Check
        'syscheck.title': 'Systemstatus',
        'syscheck.ffmpeg': 'FFmpeg (MP3-Konvertierung)',
        'syscheck.ffmpeg_desc': 'Nicht gefunden - MP3-Konvertierung funktioniert evtl. nicht',
        'syscheck.whisper': 'Whisper (Transkriptions-Engine)',
        'syscheck.whisper_desc': 'Nicht installiert - Transkription nicht verfügbar',
        'syscheck.model': 'Whisper-Modell',
        'syscheck.model_desc': 'Modell "{model}" noch nicht heruntergeladen (~460 MB)',
        'syscheck.output_dir': 'Ausgabeordner: {path}',
        'syscheck.loopback': 'System-Audio (Loopback)',
        'syscheck.loopback_desc': 'Kein Loopback-Ger\u00e4t gefunden - VB-Audio Virtual Cable installieren (kostenlos): vb-audio.com/Cable',
        'syscheck.gpu': 'GPU-Beschleunigung (CUDA)',
        'syscheck.gpu_desc': 'Keine NVIDIA-GPU gefunden - CPU wird verwendet (langsamer)',
        'syscheck.gpu_exe_desc': 'In der .exe nicht verf\u00fcgbar - f\u00fcr GPU-Support aus dem Quellcode starten',

        # GPU Installation
        'menu.install_gpu': 'GPU-Support installieren...',
        'gpu.already_installed': 'GPU-Support ist bereits aktiv!\nVerwendet: {gpu}',
        'gpu.exe_not_supported': 'GPU-Support kann in der portablen .exe nicht installiert werden.\n\nFür GPU-Beschleunigung aus dem Quellcode starten:\n1. pip install torch --index-url https://download.pytorch.org/whl/cu121\n2. python src/recorder.py',
        'gpu.confirm_install': 'NVIDIA CUDA-Support für schnellere Transkription installieren (~2,5 GB Download).\n\nBenötigt eine NVIDIA-GPU mit CUDA-Unterstützung.\n\nFortfahren?',
        'gpu.installing': 'GPU-Support wird installiert... Das kann einige Minuten dauern.',
        'gpu.install_success': 'GPU-Support installiert! App neustarten, um GPU-Beschleunigung zu nutzen.',
        'gpu.install_failed': 'GPU-Installation fehlgeschlagen:\n{error}',

        # Audio Sources
        'devices.frame_title': 'Audio-Quellen',
        'devices.microphone': 'Mikrofon:',
        'devices.system_audio': 'System-Audio:',
        'devices.no_microphone': '(Kein Mikrofon)',
        'devices.no_system_audio': '(Kein System-Audio)',
        'devices.mic_level': 'Mic-Pegel:',
        'devices.sys_level': 'Sys-Pegel:',
        'devices.refresh': 'Geräte aktualisieren',

        # Status
        'status.ready': 'Bereit',
        'status.recording': 'Aufnahme läuft...',
        'status.processing': 'Verarbeite...',
        'status.transcribing': 'Transkribiere...',
        'status.extracting_audio': 'Extrahiere Audio...',
        'status.downloading_model': 'Whisper-Modell wird heruntergeladen (~460 MB)... Bitte warten.',
        'status.loading_model': 'Whisper-Modell wird geladen...',
        'status.cancelled': 'Abgebrochen',

        # Buttons
        'button.start_recording': 'Aufnahme starten',
        'button.stop_recording': 'Aufnahme stoppen',

        # Duration
        'duration.label': 'Dauer: {time}',

        # Output folder
        'output.frame_title': 'Ausgabeordner',
        'output.browse_title': 'Ausgabeordner wählen',

        # Transcription
        'transcription.frame_title': 'Transkription',
        'transcription.auto_transcribe': 'Automatisch transkribieren',
        'transcription.language': 'Sprache:',
        'transcription.model': 'Modell: {model}',
        'transcription.progress': 'Transkribiere... {percent}%',
        'transcription.cancel': 'Abbrechen',
        'transcription.whisper_not_installed': 'Whisper nicht installiert',
        'transcription.model_first_download': 'Hinweis: Das Whisper-Modell (~460 MB) wird bei der ersten Transkription heruntergeladen. Internetverbindung erforderlich.',

        # Transcription language names
        'lang.auto': 'Auto',
        'lang.german': 'Deutsch',
        'lang.english': 'Englisch',
        'lang.french': 'Französisch',
        'lang.spanish': 'Spanisch',
        'lang.italian': 'Italienisch',

        # Dialogs
        'dialog.no_source_title': 'Keine Audioquelle',
        'dialog.no_source_msg': 'Bitte wähle mindestens ein Mikrofon oder System-Audio aus.',
        'dialog.error': 'Fehler',
        'dialog.error_start': 'Aufnahme konnte nicht gestartet werden:\n{error}',
        'dialog.error_processing': 'Verarbeitung fehlgeschlagen:\n{error}',
        'dialog.error_transcription': 'Transkription fehlgeschlagen:\n{error}',
        'dialog.done': 'Fertig',
        'dialog.done_recording': 'Aufnahme gespeichert:\n{file}',
        'dialog.done_recording_transcript': 'Aufnahme gespeichert:\n{file}\n\nTranskript:\n{transcript}',
        'dialog.done_transcription': 'Transkript gespeichert:\n{file}',

        # File dialog
        'filedialog.transcribe_title': 'Datei zum Transkribieren auswählen',
        'filedialog.audio_video': 'Audio/Video Dateien',
        'filedialog.audio': 'Audio Dateien',
        'filedialog.video': 'Video Dateien',
        'filedialog.all': 'Alle Dateien',

        # About
        'about.description': 'Einfacher Audio-Recorder mit integrierter Transkription.\nMeetings, Interviews oder beliebiges Audio aufnehmen\nund lokal mit OpenAI Whisper transkribieren.',
        'about.license': 'Lizenz: GPL-3.0',
        'about.author': 'von conversion-traffic.de',

        # Update
        'update.title': 'Update verf\u00fcgbar',
        'update.downloading': 'Update wird heruntergeladen...',
        'update.ready': 'Version {version} ist bereit zur Installation!\n\nJetzt installieren und neustarten?',
        'update.failed': 'Update-Pr\u00fcfung fehlgeschlagen.',
        'update.up_to_date': 'Du verwendest die neueste Version (v{version}).',
        'update.install_btn': 'Installieren & Neustarten',
        'update.later_btn': 'Sp\u00e4ter',

        # Settings
        'settings.frame_title': 'Einstellungen',
        'settings.ui_language': 'Oberfläche:',
        'settings.theme': 'Design:',
        'settings.theme_light': 'Hell',
        'settings.theme_dark': 'Dunkel',
        'settings.restart_title': 'Neustart erforderlich',
        'settings.restart_msg': 'Bitte starte die Anwendung neu, damit die Sprachänderung wirksam wird.',
    }
}


def set_language(lang: str):
    """Set the active UI language. Supported: 'en', 'de'."""
    global _current_language
    if lang in translations:
        _current_language = lang


def get_language() -> str:
    """Get the current UI language code."""
    return _current_language


def t(key: str, **kwargs) -> str:
    """
    Get translated string for the given key.

    Args:
        key: Translation key (e.g. 'menu.file')
        **kwargs: Format parameters (e.g. time='00:00:00')

    Returns:
        Translated string, or the key itself if not found.
    """
    text = translations.get(_current_language, translations['en']).get(key)
    if text is None:
        text = translations['en'].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
