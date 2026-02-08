# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Record & Transcribe

import os
import importlib

block_cipher = None

# Find whisper assets directory
whisper_assets = []
try:
    whisper_spec = importlib.util.find_spec('whisper')
    if whisper_spec and whisper_spec.origin:
        whisper_dir = os.path.dirname(whisper_spec.origin)
        assets_dir = os.path.join(whisper_dir, 'assets')
        if os.path.isdir(assets_dir):
            whisper_assets = [(assets_dir, os.path.join('whisper', 'assets'))]
except Exception:
    pass

# Check if bundled FFmpeg exists
ffmpeg_path = os.path.join('bundled_ffmpeg', 'ffmpeg.exe')
binaries = []
if os.path.exists(ffmpeg_path):
    binaries.append((ffmpeg_path, 'bundled_ffmpeg'))

a = Analysis(
    ['src/recorder.py'],
    pathex=['src'],
    binaries=binaries,
    datas=[
        ('assets/logo.png', 'assets'),
        ('assets/logo.ico', 'assets'),
    ] + whisper_assets,
    hiddenimports=[
        'whisper',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        'sounddevice',
        'numpy',
        'pydub',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RecordAndTranscribe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico',
)
