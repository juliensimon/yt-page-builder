#!/usr/bin/env python3
"""
YouTube Cookie Setup Helper
This script helps users set up cookies for YouTube video downloading.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def print_header():
    """Print the setup header."""
    print("=" * 60)
    print("🎬 YouTube Cookie Setup Helper")
    print("=" * 60)
    print()


def print_why_cookies():
    """Explain why cookies are needed."""
    print("📋 Why are YouTube cookies required?")
    print()
    print("YouTube requires authentication cookies to download videos because:")
    print("• Age-restricted content requires login")
    print("• Private/unlisted videos need authentication")
    print("• Higher rate limits for authenticated requests")
    print("• Geo-restricted content needs location-based auth")
    print("• Premium content requires authentication")
    print("• Anti-bot measures distinguish legitimate users")
    print()


def get_cookie_method():
    """Get the user's preferred method for obtaining cookies."""
    print("🔧 Choose your method for getting YouTube cookies:")
    print()
    print("1. Use yt-dlp's built-in browser extraction (Easiest)")
    print("2. Manual browser extraction (More control)")
    print("3. Use existing cookies file")
    print("4. Skip for now (some videos may not work)")
    print()

    while True:
        choice = input("Enter your choice (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("Please enter 1, 2, 3, or 4.")


def setup_yt_dlp_cookies():
    """Set up cookies using yt-dlp's built-in extraction."""
    print("\n🔍 Setting up cookies with yt-dlp...")
    print()

    # Check if yt-dlp is available
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ yt-dlp not found. Please install it first:")
        print("   pip install yt-dlp")
        return False

    # Get browser choice
    print("Choose your browser:")
    print("1. Chrome/Edge")
    print("2. Firefox")
    print("3. Safari")
    print()

    browser_map = {'1': 'chrome', '2': 'firefox', '3': 'safari'}

    while True:
        browser_choice = input("Enter browser choice (1-3): ").strip()
        if browser_choice in browser_map:
            browser = browser_map[browser_choice]
            break
        print("Please enter 1, 2, or 3.")

    # Extract cookies
    print(f"\n📥 Extracting cookies from {browser}...")
    try:
        result = subprocess.run(
            ["yt-dlp", "--cookies-from-browser", browser, "--print", "cookies"],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout.strip():
            # Save cookies to file
            cookies_file = "cookies.txt"
            with open(cookies_file, 'w') as f:
                f.write(result.stdout)

            print(f"✅ Cookies extracted and saved to {cookies_file}")
            return cookies_file
        else:
            print(
                "❌ No cookies found. Make sure you're logged into YouTube in your browser."
            )
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ Error extracting cookies: {e}")
        print("Make sure you're logged into YouTube in your browser.")
        return None


def manual_cookie_setup():
    """Guide user through manual cookie extraction."""
    print("\n🔧 Manual Cookie Extraction Guide")
    print()
    print("Follow these steps:")
    print()
    print("1. Open YouTube in your browser")
    print("2. Log in to your YouTube/Google account")
    print("3. Open Developer Tools (F12)")
    print("4. Go to Application/Storage tab > Cookies")
    print("5. Find youtube.com or google.com cookies")
    print("6. Export these key cookies:")
    print("   - SID")
    print("   - HSID")
    print("   - SSID")
    print("   - APISID")
    print("   - SAPISID")
    print("   - __Secure-3PAPISID")
    print()

    print(
        "You can use browser extensions like 'Cookie Editor' to export all cookies at once."
    )
    print()

    cookies_file = input(
        "Enter path to your cookies file (or press Enter to skip): "
    ).strip()

    if cookies_file and os.path.exists(cookies_file):
        print(f"✅ Cookies file found: {cookies_file}")
        return cookies_file
    elif cookies_file:
        print(f"❌ Cookies file not found: {cookies_file}")
        return None
    else:
        print("⏭️  Skipping cookie setup")
        return None


def use_existing_cookies():
    """Use an existing cookies file."""
    print("\n📁 Using existing cookies file")
    print()

    cookies_file = input("Enter path to your cookies file: ").strip()

    if os.path.exists(cookies_file):
        print(f"✅ Cookies file found: {cookies_file}")
        return cookies_file
    else:
        print(f"❌ Cookies file not found: {cookies_file}")
        return None


def update_config(cookies_file=None, cookies_browser=None):
    """Update the configuration file with cookie settings."""
    config_file = "config.py"

    if not os.path.exists(config_file):
        print(f"❌ Configuration file {config_file} not found.")
        print("Please copy config_template.py to config.py first.")
        return False

    print(f"\n⚙️  Updating configuration file: {config_file}")

    try:
        with open(config_file, 'r') as f:
            content = f.read()

        # Update cookies_file setting
        if cookies_file:
            if '"cookies_file": ""' in content:
                content = content.replace(
                    '"cookies_file": ""', f'"cookies_file": "{cookies_file}"'
                )
            elif '"cookies_file":' in content:
                # Replace existing value
                import re

                content = re.sub(
                    r'"cookies_file":\s*"[^"]*"',
                    f'"cookies_file": "{cookies_file}"',
                    content,
                )

        # Update cookies_browser setting
        if cookies_browser:
            if '"cookies_browser": ""' in content:
                content = content.replace(
                    '"cookies_browser": ""', f'"cookies_browser": "{cookies_browser}"'
                )
            elif '"cookies_browser":' in content:
                # Replace existing value
                import re

                content = re.sub(
                    r'"cookies_browser":\s*"[^"]*"',
                    f'"cookies_browser": "{cookies_browser}"',
                    content,
                )

        with open(config_file, 'w') as f:
            f.write(content)

        print("✅ Configuration updated successfully!")
        return True

    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False


def print_next_steps(cookies_file=None):
    """Print next steps for the user."""
    print("\n🎯 Next Steps:")
    print()

    if cookies_file:
        print(f"✅ Cookies are set up: {cookies_file}")
        print("You can now download YouTube videos using:")
        print("   python audio_to_json.py --url 'VIDEO_URL'")
    else:
        print("⚠️  No cookies configured")
        print(
            "Some videos may not download due to age restrictions or privacy settings"
        )
        print("You can still try downloading public videos:")
        print("   python audio_to_json.py --url 'VIDEO_URL'")

    print()
    print("📚 For more information, see the README.md file")
    print("🔗 Live demo: https://www.julien.org/youtube/2025/index.html")


def main():
    """Main setup function."""
    print_header()
    print_why_cookies()

    method = get_cookie_method()

    cookies_file = None
    cookies_browser = None

    if method == '1':
        # yt-dlp extraction
        cookies_file = setup_yt_dlp_cookies()
        if cookies_file:
            cookies_browser = "chrome"  # Default, could be made more specific

    elif method == '2':
        # Manual extraction
        cookies_file = manual_cookie_setup()

    elif method == '3':
        # Existing file
        cookies_file = use_existing_cookies()

    elif method == '4':
        # Skip
        print("\n⏭️  Skipping cookie setup")

    # Update configuration
    if cookies_file or method == '1':
        update_config(cookies_file, cookies_browser)

    print_next_steps(cookies_file)


if __name__ == "__main__":
    main()
