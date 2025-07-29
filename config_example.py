#!/usr/bin/env python3
"""
Example configuration file for YouTube Page Builder
Copy this to config.py and customize for your needs
"""

# YouTube Page Builder Settings
YT_PAGE_BUILDER_CONFIG = {
    # Default directories
    "input_dir": "input",
    "output_dir": "output",
    "logs_dir": "logs",
    # Processing settings
    "max_workers": 5,
    "chunk_size": 32000,  # Characters per chunk for transcript processing
    # AI settings
    "api_url": "https://api.openai.com/v1/chat/completions",
    "model": "gpt-3.5-turbo",
    "max_tokens": 4000,
    "temperature": 0.7,
    # HTML generation settings
    "include_transcript": True,
    "include_tags": True,
    "include_description": True,
    "include_links": True,
    # Custom links to include - customize these for your needs
    "links": {
        # Example links - replace with your own
        "website": "https://your-website.com",
        "youtube_channel": "https://youtube.com/@your-channel",
        "github": "https://github.com/your-username",
        "twitter": "https://twitter.com/your-handle",
        "linkedin": "https://linkedin.com/in/your-profile",
        "blog": "https://your-blog.com",
    },
}

# Audio-to-JSON Settings
AUDIO_TO_JSON_CONFIG = {
    # Default directories
    "output_dir": "output",
    # Download settings
    "audio_format": "opus",
    "audio_quality": "best",
    # Transcription settings
    "whisper_model": "distil-whisper/distil-large-v3",
    "language": "en",
    "task": "transcribe",
    # Processing settings
    "sample_rate": 16000,
    "chunk_length": 30,  # seconds
    "stride_length": 5,  # seconds
}

# Common Settings
COMMON_CONFIG = {
    # Logging
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(levelname)s - %(message)s",
    # File patterns
    "video_patterns": {
        "info_json": "*info.json",
        "description": "*.description",
        "transcription": "*_transcription.json",
        "thumbnail": "*.webp",
    },
    # Date formats
    "date_formats": {"folder": "%Y%m%d", "display": "%B %d, %Y"},
}

# Development/Testing Settings
DEV_CONFIG = {
    "test_mode": False,
    "limit_folders": None,
    "verbose_logging": False,
    "save_intermediate": False,
}

# Customization Instructions:
# 1. Copy this file to config.py
# 2. Replace the example links with your own URLs
# 3. Customize other settings as needed
# 4. To disable links entirely, set "links": {}
# 5. To disable specific sections, set include_* to False
