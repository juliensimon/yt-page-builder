# YouTube Page Builder

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/your-username/yt-page-builder)
[![Maintenance](https://img.shields.io/badge/Maintenance-Yes-brightgreen.svg)](https://github.com/your-username/yt-page-builder/commits/main)
[![Issues](https://img.shields.io/badge/Issues-Welcome-orange.svg)](https://github.com/your-username/yt-page-builder/issues)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Latest-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![spaCy](https://img.shields.io/badge/spaCy-3.7+-orange.svg)](https://spacy.io/)
[![DistilWhisper](https://img.shields.io/badge/DistilWhisper-Latest-purple.svg)](https://github.com/guillaumekln/faster-whisper)
[![Stars](https://img.shields.io/github/stars/your-username/yt-page-builder?style=social)](https://github.com/your-username/yt-page-builder)
[![Forks](https://img.shields.io/github/forks/your-username/yt-page-builder?style=social)](https://github.com/your-username/yt-page-builder)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/your-username/yt-page-builder)
[![Last Commit](https://img.shields.io/github/last-commit/your-username/yt-page-builder)](https://github.com/your-username/yt-page-builder/commits/main)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](https://github.com/your-username/yt-page-builder/actions)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-YouTube%20Collection-blue.svg)](https://www.julien.org/youtube/2025/index.html)

A comprehensive Python toolkit for downloading YouTube videos, extracting transcriptions, and generating beautiful HTML pages with embedded videos, descriptions, and AI-enhanced content.

## 🎯 Live Demo

See the tool in action: **[YouTube Videos Collection - 2025](https://www.julien.org/youtube/2025/index.html)**

This demo shows 35 videos from 2025, all processed and organized using this YouTube Page Builder tool.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Input Structure](#input-structure)
- [Output](#output)
- [Advanced Usage](#advanced-usage)
  - [Customizing Links](#customizing-links)
  - [Customizing Badges](#customizing-badges)
  - [Command Line Options](#command-line-options)
- [Error Handling](#error-handling)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Overview

This project consists of two main components:

1. **Audio-to-JSON Tool** (`audio-to-json/`) - Downloads YouTube videos and converts them to structured JSON with transcriptions
2. **YouTube Page Builder** (`yt-page-builder/`) - Generates beautiful HTML pages from processed video data

## Features

### Audio-to-JSON Tool
- **YouTube Download**: Download videos, playlists, or entire channels using yt-dlp
- **Audio Extraction**: Automatically extract audio in Opus format
- **Metadata Extraction**: Download video descriptions, thumbnails, and upload dates
- **Speech Recognition**: Transcribe audio using DistilWhisper with MPS acceleration
- **JSON Output**: Structured output with all video metadata and transcriptions

### YouTube Page Builder
- **Automatic video embedding**: Extracts YouTube video IDs and creates embedded players
- **Clean, responsive design**: Modern, mobile-friendly HTML pages with CSS styling
- **Video metadata**: Displays video titles and publication dates
- **Description section**: Includes complete video descriptions with clickable hyperlinks and timestamp links
- **Transcript section**: Full video transcripts with semantic paragraph organization and filler word removal
- **AI-generated tags**: 3-5 relevant tags automatically generated using NLP analysis
- **Custom links**: Configurable links section (optional)
- **Batch processing**: Process all videos at once or limit for testing
- **Index page**: Generate a beautiful index page listing all videos with links
- **Live demo available**: See [YouTube Videos Collection - 2025](https://www.julien.org/youtube/2025/index.html) for a real-world example

## Quick Start

### Prerequisites

- Python 3.8+
- PyTorch
- Transformers
- Librosa
- NumPy
- Accelerate
- yt-dlp
- spaCy (for NLP processing)

### Why Cookies Are Required

**Important**: YouTube requires authentication cookies to download videos. This is necessary because:

1. **Age-restricted content**: Many videos are age-restricted and require login
2. **Private videos**: Access to private or unlisted videos requires authentication
3. **Rate limiting**: Authenticated requests have higher rate limits
4. **Geo-restrictions**: Some videos are region-locked and require location-based authentication
5. **Premium content**: YouTube Premium content requires authentication
6. **Anti-bot measures**: YouTube uses cookies to distinguish legitimate users from automated bots

#### How to Get YouTube Cookies

**Method 1: Using Browser Developer Tools (Recommended)**

1. **Open YouTube** in your browser (Chrome, Firefox, Safari, or Edge)
2. **Log in** to your YouTube/Google account
3. **Open Developer Tools**:
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Option+I` (Mac)
   - Safari: Enable Developer menu in Preferences > Advanced, then press `Cmd+Option+I`

4. **Go to the Application/Storage tab**:
   - Chrome/Edge: Click "Application" tab, then "Cookies" in the left sidebar
   - Firefox: Click "Storage" tab, then "Cookies"
   - Safari: Click "Storage" tab, then "Cookies"

5. **Find YouTube cookies**:
   - Look for `youtube.com` or `google.com` in the domain list
   - Key cookies to export: `SID`, `HSID`, `SSID`, `APISID`, `SAPISID`, `__Secure-3PAPISID`

6. **Export cookies**:
   - Right-click on each cookie and copy the name and value
   - Or use browser extensions like "Cookie Editor" to export all cookies

**Method 2: Using Cookie Extensions**

1. **Install a cookie export extension**:
   - Chrome: "Cookie Editor" or "EditThisCookie"
   - Firefox: "Cookie Quick Manager"
   - Safari: "Cookie Editor"

2. **Export cookies**:
   - Go to YouTube while logged in
   - Use the extension to export cookies
   - Save as a `.txt` file

**Method 3: Using yt-dlp's Built-in Cookie Extraction**

```bash
# Extract cookies from browser (Chrome/Edge)
yt-dlp --cookies-from-browser chrome

# Extract cookies from Firefox
yt-dlp --cookies-from-browser firefox

# Extract cookies from Safari
yt-dlp --cookies-from-browser safari
```

#### Using Cookies with the Tool

**Option 1: Automated Setup (Recommended)**
```bash
# Run the cookie setup helper
python setup_cookies.py
```

This interactive script will guide you through the entire cookie setup process.

**Option 2: Cookie File**
```bash
# Save cookies to a file
python audio_to_json.py --url "VIDEO_URL" --cookies cookies.txt
```

**Option 3: Environment Variable**
```bash
# Set cookies as environment variable
export YT_COOKIES="SID=value; HSID=value; SSID=value; APISID=value; SAPISID=value; __Secure-3PAPISID=value"
python audio_to_json.py --url "VIDEO_URL"
```

**Option 4: Direct Cookie String**
```bash
# Pass cookies directly
python audio_to_json.py --url "VIDEO_URL" --cookies "SID=value; HSID=value; SSID=value; APISID=value; SAPISID=value; __Secure-3PAPISID=value"
```

#### Cookie Security Notes

⚠️ **Important Security Considerations**:

- **Never share your cookies**: They contain your authentication credentials
- **Use a dedicated account**: Consider creating a separate YouTube account for downloading
- **Regular rotation**: Update cookies periodically as they expire
- **Local storage only**: Store cookies locally, never commit them to version control
- **Limited scope**: Only use cookies for legitimate content you have permission to download

#### Troubleshooting Cookie Issues

**Common Problems**:
- **"Video unavailable"**: Cookies may be expired or invalid
- **"Age-restricted content"**: Need valid authentication cookies
- **"Private video"**: Requires cookies from an account with access
- **"Rate limited"**: Too many requests, try with authenticated cookies

**Solutions**:
1. **Refresh cookies**: Get new cookies from your browser
2. **Check account access**: Ensure your account can view the video
3. **Wait and retry**: YouTube may temporarily block requests
4. **Use different account**: Try with a different YouTube account

### Installation

#### Option 1: Automated Setup (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd yt-page-builder
```

2. Run the automated setup:
```bash
python setup.py
```

3. Set up development environment (optional but recommended):
```bash
python setup_dev.py
```

4. Test the installation:
```bash
python test_installation.py
```

#### Option 2: Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd yt-page-builder
```

2. Install project dependencies:
```bash
# Install main project dependencies
pip install -r requirements.txt

# Install test dependencies (optional)
pip install -r requirements-test.txt
```

3. Download spaCy language model (optional):
```bash
python -m spacy download en_core_web_sm
```

### Usage

#### Step 1: Download and Transcribe YouTube Videos

```bash
cd audio-to-json

# Download a single video
python audio_to_json.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Download a playlist
python audio_to_json.py --url "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Download an entire channel
python audio_to_json.py --url "https://youtube.com/@channelname"
```

#### Step 2: Generate HTML Pages

```bash
cd ../yt-page-builder

# Process all video folders in the input directory
python yt_page_builder.py

# Generate an index page for all videos
python create_index.py
```

## Project Structure

```
yt-page-builder/
├── audio-to-json/                 # YouTube download and transcription tool
│   ├── audio_to_json.py          # Main transcription script
│   ├── requirements.txt           # Component-specific dependencies
│   └── README.md                 # Detailed documentation
├── yt-page-builder/              # HTML page generation tool
│   ├── yt_page_builder.py        # Main page builder script
│   ├── create_index.py           # Index page generator
│   ├── requirements.txt           # Component-specific dependencies
│   ├── input/                    # Video folders (created by audio-to-json)
│   ├── output/                   # Generated HTML pages
│   ├── logs/                     # Processing logs
│   └── README.md                 # Detailed documentation
├── requirements.txt               # Main project dependencies
├── setup.py                      # Automated setup script
├── example.py                    # Complete workflow example
├── test_installation.py          # Installation verification
├── config.py                     # Configuration settings
├── config_template.py            # Template configuration file
├── config_julien_simon.py        # Julien Simon's specific configuration
├── setup_cookies.py              # Cookie setup helper script
├── setup_dev.py                  # Development environment setup
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── pyproject.toml                # Black and isort configuration
├── requirements-dev.txt          # Development dependencies
├── update_badges.py              # Badge updater script
├── run_tests.py                  # Test runner script
├── requirements-test.txt          # Testing dependencies
├── pytest.ini                   # pytest configuration
├── tests/                        # Test suite
│   ├── __init__.py              # Tests package
│   ├── test_yt_page_builder.py  # YouTube Page Builder tests
│   ├── test_create_index.py     # Index creation tests
│   └── test_utilities.py        # Utility script tests
├── .github/workflows/            # GitHub Actions
│   └── tests.yml                # Automated testing workflow
├── LICENSE                       # MIT License
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Input Structure

The YouTube Page Builder expects video folders in the `input` directory with this structure:

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

## Output

### Audio-to-JSON Output

For each video, the tool downloads:
- **Audio file**: `.opus` format (high quality)
- **Thumbnail**: `.webp` format
- **Description**: `.description` text file
- **Metadata**: `.info.json` with full video information
- **Transcription**: `_transcription.json` with transcription text

### HTML Page Output

The YouTube Page Builder generates HTML files with:

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

## Advanced Usage

### Customizing Links

To add custom links to your generated pages, edit the `config.py` file:

```python
# In config.py, modify the links section:
"links": {
    "website": "https://your-website.com",
    "youtube_channel": "https://youtube.com/@your-channel",
    "github": "https://github.com/your-username",
    "twitter": "https://twitter.com/your-handle",
}
```

The links will appear at the bottom of each video page and the index page. To disable links entirely, set the `links` dictionary to empty: `"links": {}`

**Note**: See `config_example.py` for a complete example configuration file.

### Customizing Badges

The badges in this README are set to placeholder GitHub URLs. To update them for your repository:

```bash
python update_badges.py <your-github-username> <your-repository-name>
```

Example:
```bash
python update_badges.py myusername my-yt-builder
```

This will update all the GitHub badges to point to your repository.

### Command Line Options

#### Audio-to-JSON Tool
```bash
# Specify output directory
python audio_to_json.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir "/path/to/output"

# Convert local audio files
python audio_to_json.py --file "audio_file.opus"
python audio_to_json.py --directory "/path/to/audio/files"
```

#### YouTube Page Builder
```bash
# Specify custom input/output directories
python yt_page_builder.py --input /path/to/input --output /path/to/output

# Process only first 5 folders (for testing)
python yt_page_builder.py --limit 5

# Short form options
python yt_page_builder.py -i input -o output -l 3
```

### Testing

#### Quick Demo

Run the complete example to see the full workflow:

```bash
python example.py
```

This will:
1. Download a sample YouTube video
2. Generate HTML pages
3. Create an index page
4. Show you where to find the results

#### Real-World Example

See the tool in action with a live demo: **[YouTube Videos Collection - 2025](https://www.julien.org/youtube/2025/index.html)**

This demonstrates:
- 35 videos from 2025 processed and organized
- Beautiful responsive design
- AI-generated tags for each video
- Clean transcriptions and descriptions
- Professional styling and navigation

#### Automated Tests

##### Quick Tests (Recommended)
```bash
python run_tests.py quick
```

##### All Tests
```bash
python run_tests.py all
```

##### Specific Test Module
```bash
python run_tests.py test_utilities
python run_tests.py test_create_index
python run_tests.py test_yt_page_builder
```

##### Using pytest
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests with coverage
pytest tests/ -v --cov=yt-page-builder --cov=audio-to-json

# Run quick tests only
pytest tests/ -m quick

# Run tests in parallel
pytest tests/ -n auto
```

#### Test Coverage
- **Unit Tests**: Core functionality testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Tests**: External API testing without real calls
- **Configuration Tests**: Settings validation

**Note**: Some tests require external dependencies (spaCy, API keys) and may fail in certain environments. The quick tests focus on core functionality that doesn't require external services.

#### Manual Testing

To test the tools with a small subset of videos:

```bash
# Test audio-to-json with a single video
python audio_to_json.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Test page builder with limited folders
python yt_page_builder.py --limit 3
```

## Error Handling

Both tools include robust error handling:

- **Missing files**: Gracefully handles missing files or corrupted data
- **Invalid JSON**: Skips folders with corrupted JSON data
- **File permissions**: Reports write errors for output files
- **Network issues**: Handles YouTube rate limiting and geo-restrictions
- **Transcript processing**: Manages long transcripts by chunking them

## Performance

- **Concurrent processing**: Uses ThreadPoolExecutor for parallel video processing
- **Memory management**: Processes large transcripts in chunks
- **Progress tracking**: Shows progress bars and detailed logging
- **GPU acceleration**: Automatically uses available GPU (CUDA, MPS on macOS, or CPU)

## Troubleshooting

### Common Issues

1. **Missing spaCy model**: Run `python -m spacy download en_core_web_sm`
2. **Large transcript errors**: The tool automatically chunks long transcripts
3. **YouTube download failures**: Check network connection and video availability
4. **Memory issues**: Reduce the `--limit` parameter for testing

### Logs

Check the following log files for detailed information:
- `yt-page-builder/logs/error.log` - Processing logs and errors
- `yt-page-builder/output.log` - Output processing logs

## Contributing

### Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone <your-fork-url>
   cd yt-page-builder
   ```

3. **Set up development environment**:
   ```bash
   python setup_dev.py
   ```
   This will install pre-commit hooks, black, isort, and other development tools.

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Make your changes** - Pre-commit hooks will automatically format your code

6. **Run tests**:
   ```bash
   python run_tests.py all
   ```

7. **Commit your changes** - Pre-commit hooks will run automatically

8. **Submit a pull request**

### Code Style

This project uses:
- **Black** for code formatting (line length: 88)
- **isort** for import sorting (compatible with Black)
- **Pre-commit hooks** that run automatically on every commit

The pre-commit hooks will **automatically modify files** to ensure consistent formatting.

### Manual Formatting

If you need to format files manually:
```bash
# Format all Python files
black .

# Sort imports
isort .

# Run all pre-commit hooks
pre-commit run --all-files
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the logs in the `logs/` directory
2. Review the detailed documentation in each component's README
3. Test with a small subset of videos using the `--limit` option
