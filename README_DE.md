# Record & Transcribe

**Einfacher Audio-Recorder mit integrierter Transkription.** Meetings, Interviews oder beliebiges Audio vom Mikrofon und/oder System-Audio aufnehmen und lokal mit OpenAI Whisper transkribieren.

*von [conversion-traffic.de](https://www.conversion-traffic.de)*

[English Version](README.md)

---

## Features

- **Mikrofon** und/oder **System-Audio** (WASAPI Loopback) aufnehmen
- **Live Audio-Pegelanzeige** fuer beide Quellen
- Automatische **MP3-Konvertierung** nach Aufnahme
- Integrierte **Transkription** mit OpenAI Whisper (laeuft lokal, kein API-Key noetig)
- **Bestehende Dateien transkribieren** (MP3, WAV, MP4, MKV, AVI, M4A, WebM)
- **Zweisprachige Oberflaeche** - Deutsch und Englisch
- Portable **Single-File .exe** (Windows)
- Alles laeuft **lokal** - keine Daten verlassen deinen Rechner

## Download

Gehe zu [Releases](../../releases) und lade die neueste `record-and-transcribe-vX.Y.Z-windows.exe` herunter.

## Systemvoraussetzungen

- **OS:** Windows 10/11
- **Python:** 3.9+ (nur fuer Ausfuehrung aus dem Quellcode)
- **FFmpeg:** In der .exe enthalten, oder separat installieren fuer Entwicklung

### System-Audio aufnehmen

Um System-Audio aufzunehmen (z.B. Meeting-Audio von Zoom/Teams), brauchst du eines davon:

- **Stereo Mix** - Aktivieren unter Windows Soundeinstellungen > Aufnahmegeraete
- **VB-Audio Virtual Cable** (kostenlos) - [Download hier](https://vb-audio.com/Cable/)
- **WASAPI Loopback** - Manche Audio-Treiber stellen das automatisch bereit

## Schnellstart

### Option 1: .exe herunterladen (Empfohlen)

1. Von [Releases](../../releases) herunterladen
2. `record-and-transcribe-vX.Y.Z-windows.exe` ausfuehren
3. Audio-Quellen auswaehlen
4. "Aufnahme starten" klicken

### Option 2: Aus dem Quellcode starten

```bash
git clone https://github.com/YOUR_USERNAME/record-and-transcribe.git
cd record-and-transcribe

# Abhaengigkeiten installieren
pip install -r requirements.txt

# Optional: Whisper fuer Transkription installieren
pip install openai-whisper

# Starten
python src/recorder.py
```

## Transkription

Die Transkription nutzt [OpenAI Whisper](https://github.com/openai/whisper) und laeuft komplett lokal.

- **Modell:** `small` (gute Balance aus Geschwindigkeit und Genauigkeit)
- **Sprachen:** Auto-Erkennung, Deutsch, Englisch, Franzoesisch, Spanisch, Italienisch
- **Hinweis:** Die erste Transkription laedt das Modell herunter (~460 MB)

Whisper ist **optional** - der Recorder funktioniert auch ohne. Installation:

```bash
pip install openai-whisper
```

## Aus dem Quellcode bauen

### Voraussetzungen

- Python 3.9+
- FFmpeg (`ffmpeg.exe` in `bundled_ffmpeg/` fuer das Bundling ablegen)

### .exe bauen

```bash
# Dev-Abhaengigkeiten installieren
pip install -r requirements-dev.txt

# Bauen (Windows)
build.bat

# Oder manuell:
pyinstaller record-and-transcribe.spec --noconfirm
```

Ausgabe: `dist/RecordAndTranscribe.exe`

## Konfiguration

Einstellungen werden in `config.json` neben der .exe gespeichert (oder im Projektordner bei Ausfuehrung aus dem Quellcode):

- **Ausgabeordner** - Wo Aufnahmen gespeichert werden (Standard: `~/Dokumente/Record & Transcribe`)
- **Auto-Transkription** - Automatisch nach Aufnahme transkribieren
- **Sprache** - Transkriptions-Sprache
- **Oberflaechensprache** - Deutsch/Englisch (erfordert Neustart)

## Lizenz

GPL-3.0 License - siehe [LICENSE](LICENSE)

## Autor

Benjamin Haentzschel - [conversion-traffic.de](https://www.conversion-traffic.de)
