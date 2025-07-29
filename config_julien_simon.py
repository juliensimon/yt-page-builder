#!/usr/bin/env python3
"""
Julien Simon's specific configuration for YouTube Page Builder
This file contains Julien's actual settings and branding
"""

# =============================================================================
# SITE CONFIGURATION - JULIEN SIMON
# =============================================================================

SITE_CONFIG = {
    "site_name": "Julien Simon - YouTube Videos",
    "site_description": "A curated collection of AI and technology videos",
    "site_author": "Julien Simon",
    "site_url": "https://www.julien.org",
    # Page titles and headings
    "index_title": "Julien Simon",
    "index_subtitle": "YouTube Videos Collection",
    "video_page_title_template": "{title} - Julien Simon",
    # Custom branding
    "brand_name": "Julien Simon",
    "brand_logo_url": "",  # Optional: URL to logo
    "brand_color": "#3498db",  # Primary brand color
    "brand_secondary_color": "#2980b9",  # Secondary brand color
}

# =============================================================================
# YOUTUBE PAGE BUILDER SETTINGS
# =============================================================================

YT_PAGE_BUILDER_CONFIG = {
    # Directory settings
    "input_dir": "input",
    "output_dir": "output",
    "logs_dir": "logs",
    # Processing settings
    "max_workers": 5,
    "chunk_size": 32000,
    # AI/API settings
    "api_url": "https://api.openai.com/v1/chat/completions",
    "model": "gpt-3.5-turbo",
    "max_tokens": 4000,
    "temperature": 0.7,
    # YouTube download settings
    "cookies_file": "",  # Path to cookies.txt file (optional)
    "cookies_browser": "",  # Browser to extract cookies from: "chrome", "firefox", "safari" (optional)
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    # Content options
    "include_transcript": True,
    "include_tags": True,
    "include_description": True,
    "include_links": True,
    # Julien Simon's custom links
    "links": {
        "julien_org": "https://www.julien.org/youtube.html",
        "youtube_channel": "https://youtube.com/@juliensimon.fr",
        "github": "https://github.com/juliensimon",
        "twitter": "https://twitter.com/juliensimon",
        "linkedin": "https://linkedin.com/in/juliensimon",
    },
}

# =============================================================================
# AUDIO-TO-JSON SETTINGS
# =============================================================================

AUDIO_TO_JSON_CONFIG = {
    "output_dir": "output",
    "audio_format": "opus",
    "audio_quality": "192K",
    "whisper_model": "openai/whisper-large-v3-turbo",
    "language": "en",
    "task": "transcribe",
    "sample_rate": 16000,
    "chunk_length": 30,
    "stride_length": 5,
}

# =============================================================================
# COMMON SETTINGS
# =============================================================================

COMMON_CONFIG = {
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(levelname)s - %(message)s",
    "video_patterns": ["*.mp4", "*.webm", "*.opus"],
    "date_formats": ["%Y%m%d", "%Y-%m-%d", "%d/%m/%Y"],
}

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================

DEV_CONFIG = {
    "test_mode": False,
    "limit_folders": None,
    "verbose_logging": False,
    "save_intermediate": False,
}

# =============================================================================
# JULIEN SIMON SPECIFIC NOTES
# =============================================================================

"""
JULIEN SIMON'S CONFIGURATION:

This configuration is specifically tailored for Julien Simon's YouTube channel
and includes his actual branding, links, and preferences.

Key Features:
- Julien Simon branding and site information
- Links to his actual social media and website
- Optimized for AI and technology content
- Professional presentation for his video collection

Live Demo: https://www.julien.org/youtube/2025/index.html

To use this configuration:
1. Copy this file to config.py
2. Run the YouTube Page Builder tool
3. The generated pages will use Julien's branding and links
"""
