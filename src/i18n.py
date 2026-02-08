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
