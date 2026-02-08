# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Record & Transcribe

import os

block_cipher = None

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
    ],
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
    icon=None,
)
