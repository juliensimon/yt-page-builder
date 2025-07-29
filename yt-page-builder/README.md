# YouTube Page Builder

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![spaCy](https://img.shields.io/badge/spaCy-3.7+-orange.svg)](https://spacy.io/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/your-username/yt-page-builder)

A Python CLI tool that generates beautiful HTML pages for YouTube videos from organized input folders.

## Overview

This tool processes YouTube video folders in the `input` directory and generates HTML pages in the `output` directory with embedded videos, descriptions, transcripts, and AI-enhanced content.

## Features

- **Automatic video embedding**: Extracts YouTube video IDs and creates embedded players
- **Clean, responsive design**: Modern, mobile-friendly HTML pages with CSS styling
- **Video metadata**: Displays video titles and publication dates
- **Description section**: Includes complete video descriptions with clickable hyperlinks and timestamp links
- **Transcript section**: Full video transcripts with semantic paragraph organization and filler word removal
- **AI-generated tags**: 3-5 relevant tags automatically generated using NLP analysis
- **Custom links**: Configurable links section (optional)
- **Batch processing**: Process all videos at once or limit for testing
- **Index page**: Generate a beautiful index page listing all videos with links

## Requirements

- Python 3.6+
- spaCy (for NLP processing)
- en_core_web_sm language model (automatically downloaded)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

### Basic Usage

Process all video folders in the `input` directory:

```bash
python yt_page_builder.py
```

Generate an index page for all videos:

```bash
python create_index.py
```

### Advanced Options

```bash
# Specify custom input/output directories
python yt_page_builder.py --input /path/to/input --output /path/to/output

# Process only first 5 folders (for testing)
python yt_page_builder.py --limit 5

# Short form options
python yt_page_builder.py -i input -o output -l 3
```

### Command Line Options

- `--input, -i`: Input directory containing video folders (default: `input`)
- `--output, -o`: Output directory for HTML files (default: `output`)
- `--limit, -l`: Limit number of folders to process (for testing)

## Input Structure

The tool expects video folders in the input directory with this structure:

```
input/
├── 20250103_Video_Title_Here/
│   ├── Video_Title_Here.info.json
│   ├── Video_Title_Here.description
│   ├── Video_Title_Here.webp
│   └── Video_Title_Here_transcription.json
├── 20250110_Another_Video_Title/
│   ├── Another_Video_Title.info.json
│   ├── Another_Video_Title.description
│   ├── Another_Video_Title.webp
│   └── Another_Video_Title_transcription.json
└── ...
```

### Folder Naming Convention

Folders should follow the pattern: `YYYYMMDD_Video_Title_Here`

- `YYYYMMDD`: Publication date in YYYYMMDD format
- `Video_Title_Here`: Video title (underscores and hyphens are converted to spaces)

### Required Files

Each video folder must contain:

1. **`*info.json`**: Contains YouTube video metadata including the video ID
2. **`*.description`**: Contains the video description text
3. **`*_transcription.json`**: Contains the video transcript (optional)

## Output

The tool generates HTML files in the output directory with:

- **Video title** (parsed from folder name)
- **Publication date** (formatted from folder name)
- **Embedded YouTube video** (responsive iframe)
- **Description section** (from .description file with automatic hyperlink and timestamp conversion)
- **Transcript section** (from *_transcription.json file with semantic paragraph organization and filler word removal)
- **AI-generated tags** (automatically extracted using spaCy NLP)
- **Custom links** (optional): Configurable links section that can be customized in `config.py`

### Index Page

The `create_index.py` script generates an `index.html` file that provides:

- **Complete video list**: All videos sorted by date (newest first)
- **Clickable links**: Direct links to each video page
- **Video statistics**: Total count and latest video date
- **Responsive design**: Works on all devices
- **Navigation**: Easy browsing of the entire collection

## Generated HTML Features

- **Responsive design**: Works on desktop, tablet, and mobile
- **Modern styling**: Clean, professional appearance
- **Accessibility**: Proper HTML structure and semantic markup
- **Performance**: Lightweight CSS with no external dependencies
- **Cross-browser**: Compatible with all modern browsers

## Error Handling

The tool includes robust error handling:

- **Missing files**: Gracefully handles missing .info.json or .description files
- **Invalid JSON**: Skips folders with corrupted JSON data
- **File permissions**: Reports write errors for output files
- **Invalid dates**: Falls back to raw date string if parsing fails
- **Long transcripts**: Automatically chunks and processes large transcripts

## Testing

To test the tool with a small subset of videos:

```bash
python yt_page_builder.py --limit 3
```

This will process only the first 3 folders, allowing you to verify the output before processing all videos.

## Logs

Processing logs are saved to `logs/error.log` for debugging and monitoring.

## License

This tool is provided as-is for generating YouTube video pages.
