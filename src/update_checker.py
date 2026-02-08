"""
Auto-update checker for Record & Transcribe.
Checks GitHub releases for newer versions and downloads the installer.
"""

import re
import tempfile
import threading
import urllib.request
import urllib.error
import json
import os
from pathlib import Path

GITHUB_REPO = "conversiontraffic/record-and-transcribe"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
API_TIMEOUT = 5
DOWNLOAD_TIMEOUT = 120


def parse_version(version_str: str) -> tuple:
    """Parse a version string like 'v0.1.0' or '0.1.0' into a tuple of ints."""
    match = re.match(r'v?(\d+)\.(\d+)\.(\d+)', version_str)
    if not match:
        return (0, 0, 0)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def is_newer_version(current: str, remote: str) -> bool:
    """Return True if remote version is newer than current."""
    return parse_version(remote) > parse_version(current)


def _find_setup_asset(assets: list) -> dict | None:
    """Find the Setup installer asset from release assets."""
    for asset in assets:
        name = asset.get('name', '').lower()
        if 'setup' in name and name.endswith('.exe'):
            return asset
    return None


def check_for_updates(current_version: str, callback):
    """
    Check GitHub for a newer release in a background thread.

    Args:
        current_version: Current app version (e.g. "0.1.0")
        callback: Function called with (version, download_url, asset_name) if update found,
                  or (None, None, None) if no update or error.
    """
    def _check():
        try:
            req = urllib.request.Request(API_URL, headers={
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'RecordAndTranscribe-UpdateChecker'
            })
            with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            # Skip pre-releases
            if data.get('prerelease', False) or data.get('draft', False):
                callback(None, None, None)
                return

            tag = data.get('tag_name', '')
            if not is_newer_version(current_version, tag):
                callback(None, None, None)
                return

            # Find setup installer asset
            assets = data.get('assets', [])
            setup_asset = _find_setup_asset(assets)
            if setup_asset:
                callback(
                    tag,
                    setup_asset['browser_download_url'],
                    setup_asset['name']
                )
            else:
                callback(None, None, None)

        except Exception:
            callback(None, None, None)

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()
    return thread


def download_update(url: str, filename: str, on_complete, on_error=None):
    """
    Download the update installer in a background thread.

    Args:
        url: Download URL for the setup .exe
        filename: Name of the file to save
        on_complete: Called with the local file path when done
        on_error: Called on failure (optional)
    """
    def _download():
        try:
            temp_dir = tempfile.mkdtemp(prefix='rt_update_')
            dest_path = os.path.join(temp_dir, filename)

            req = urllib.request.Request(url, headers={
                'User-Agent': 'RecordAndTranscribe-UpdateChecker'
            })
            with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as resp:
                with open(dest_path, 'wb') as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

            on_complete(dest_path)

        except Exception as e:
            if on_error:
                on_error(str(e))

    thread = threading.Thread(target=_download, daemon=True)
    thread.start()
    return thread
