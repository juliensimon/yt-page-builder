#!/usr/bin/env python3
"""
Template configuration file for YouTube Page Builder
Copy this file to config.py and customize it for your needs
"""

# =============================================================================
# SITE CONFIGURATION
# =============================================================================

# Site branding and information
SITE_CONFIG = {
    "site_name": "Your YouTube Videos Collection",
    "site_description": "A curated collection of videos",
    "site_author": "Your Name",
    "site_url": "https://your-website.com",
    # Page titles and headings
    "index_title": "YouTube Videos Collection",
    "index_subtitle": "A curated collection of videos",
    "video_page_title_template": "{title} - {site_name}",
    # Custom branding
    "brand_name": "Your Brand",
    "brand_logo_url": "",  # Optional: URL to your logo
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
    # Custom links (set to empty to disable)
    "links": {
        "website": "https://your-website.com",
        "youtube_channel": "https://youtube.com/@your-channel",
        "github": "https://github.com/your-username",
        "twitter": "https://twitter.com/your-handle",
        "linkedin": "https://linkedin.com/in/your-profile",
        "blog": "https://your-blog.com",
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
# CUSTOMIZATION INSTRUCTIONS
# =============================================================================

"""
CUSTOMIZATION GUIDE:

1. SITE CONFIGURATION:
   - Change site_name, site_description, site_author to your information
   - Update site_url to your website
   - Customize page titles and branding colors

2. LINKS SECTION:
   - Add your own social media and website links
   - Set include_links to False to disable the links section entirely
   - Customize link names and URLs as needed

3. PROCESSING SETTINGS:
   - Adjust max_workers based on your system capabilities
   - Modify chunk_size for transcript processing
   - Update API settings if using different AI services

4. STYLING:
   - Change brand_color and brand_secondary_color to match your brand
   - Add brand_logo_url if you have a logo

5. CONTENT OPTIONS:
   - Set include_transcript, include_tags, include_description to control what appears
   - Customize which sections are shown on video pages

6. YOUTUBE DOWNLOAD SETTINGS:
   - Set cookies_file to path of your cookies.txt file
   - Set cookies_browser to automatically extract cookies from your browser
   - Customize user_agent if needed for specific video access

EXAMPLE USAGE:
   - Copy this file to config.py
   - Replace all placeholder values with your actual information
   - Run the tool with your custom configuration
"""
