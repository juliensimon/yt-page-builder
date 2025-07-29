# YouTube Video Transcription Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Latest-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![DistilWhisper](https://img.shields.io/badge/DistilWhisper-Latest-purple.svg)](https://github.com/guillaumekln/faster-whisper)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/your-username/yt-page-builder)

This Python program downloads YouTube videos using yt-dlp and converts them to JSON with transcriptions using DistilWhisper.

## Overview

This tool downloads YouTube videos, extracts audio, and generates transcriptions using AI. It's designed to work with the YouTube Page Builder to create comprehensive video pages.

## Features

- **YouTube Download**: Download videos, playlists, or entire channels using yt-dlp
- **Audio Extraction**: Automatically extract audio in Opus format
- **Metadata Extraction**: Download video descriptions, thumbnails, and upload dates
- **Speech Recognition**: Transcribe audio using DistilWhisper with MPS acceleration
- **JSON Output**: Structured output with all video metadata and transcriptions

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make the script executable (optional):
```bash
chmod +x audio_to_json.py
```

## Usage

### Download and Transcribe YouTube Videos

```bash
# Single video
python audio_to_json.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Playlist
python audio_to_json.py --url "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Channel
python audio_to_json.py --url "https://youtube.com/@channelname"

# Specify output directory
python audio_to_json.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir "/path/to/output"
```

### Process Local Audio Files

```bash
# Convert all audio files in current directory
python audio_to_json.py

# Convert specific audio file
python audio_to_json.py --file "audio_file.opus"

# Convert files in specific directory
python audio_to_json.py --directory "/path/to/audio/files"
```

## Command Line Options

- `--url, -u`: YouTube URL, playlist, or channel ID to download and transcribe
- `--directory, -d`: Directory containing audio files (default: current directory)
- `--output-dir, -o`: Output directory for files (default: same as input)
- `--model, -m`: DistilWhisper model to use (default: distil-whisper/distil-large-v3)
- `--file, -f`: Convert a specific audio file

## Output

The program generates JSON files with the following structure:

```json
{
  "title": "Video Title",
  "publication_date": "2025-07-14",
  "transcription": "Transcription text...",
  "video_id": "VIDEO_ID",
  "channel": "Channel Name",
  "channel_id": "CHANNEL_ID",
  "duration": 1234,
  "view_count": 10000,
  "like_count": 500,
  "description": "Video description...",
  "thumbnail": "/path/to/thumbnail.webp",
  "audio_file": "/path/to/audio.opus",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

## Downloaded Files

For each video, the program downloads:
- **Audio file**: `.opus` format (high quality)
- **Thumbnail**: `.webp` format
- **Description**: `.description` text file
- **Metadata**: `.info.json` with full video information
- **Transcription**: `_transcription.json` with transcription text

## Requirements

- Python 3.8+
- PyTorch
- Transformers
- Librosa
- NumPy
- Accelerate
- yt-dlp

## Notes

- The first run will download the DistilWhisper model (several GB)
- GPU acceleration is automatically used if available (CUDA, MPS on macOS, or CPU)
- Audio files are automatically converted to 16kHz mono for processing
- The program supports various audio formats through Librosa
- yt-dlp handles YouTube rate limiting and geo-restrictions automatically

## Examples

### Download a Single Video
```bash
python audio_to_json.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Download a Playlist
```bash
python audio_to_json.py --url "https://www.youtube.com/playlist?list=PLbpiA5h8JmO7e0rG9HrHjuy4F4l9XaCk9" --output-dir "playlist_transcriptions"
```

### Download Channel Videos
```bash
python audio_to_json.py --url "https://youtube.com/@examplechannel"
```

## Integration with YouTube Page Builder

The output from this tool is designed to work seamlessly with the YouTube Page Builder. The generated files follow the expected structure:

```
output/
├── 20250103_Video_Title_Here/
│   ├── Video_Title_Here.info.json
│   ├── Video_Title_Here.description
│   ├── Video_Title_Here.webp
│   └── Video_Title_Here_transcription.json
└── ...
```

These files can be moved to the `input/` directory of the YouTube Page Builder for HTML generation.
