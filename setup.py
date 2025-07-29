#!/usr/bin/env python3
"""
Setup script for YouTube Page Builder
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install dependencies for the project."""
    print("\n📦 Installing project dependencies...")

    # Install main project dependencies
    if os.path.exists("requirements.txt"):
        if not run_command(
            "pip install -r requirements.txt", "Installing main project dependencies"
        ):
            return False
    else:
        print("⚠️  No main requirements.txt found")
        return False

    # Install test dependencies (optional)
    if os.path.exists("requirements-test.txt"):
        print("Installing test dependencies...")
        if not run_command(
            "pip install -r requirements-test.txt", "Installing test dependencies"
        ):
            print(
                "⚠️  Test dependencies installation failed, but core functionality should still work"
            )
    else:
        print("⚠️  No requirements-test.txt found")

    return True


def setup_spacy():
    """Download spaCy language model."""
    print("\n🧠 Setting up spaCy language model...")
    return run_command(
        "python -m spacy download en_core_web_sm", "Downloading spaCy model"
    )


def create_directories():
    """Create necessary directories."""
    directories = [
        "yt-page-builder/input",
        "yt-page-builder/output",
        "yt-page-builder/logs",
    ]

    print("\n📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}")


def main():
    """Main setup function."""
    print("🚀 Setting up YouTube Page Builder...\n")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        sys.exit(1)

    # Setup spaCy
    if not setup_spacy():
        print("\n❌ Failed to setup spaCy")
        sys.exit(1)

    # Create directories
    create_directories()

    print("\n🎉 Setup completed successfully!")
    print("\n📖 Next steps:")
    print(
        "1. Download videos: cd audio-to-json && python audio_to_json.py --url <YOUTUBE_URL>"
    )
    print("2. Generate pages: cd yt-page-builder && python yt_page_builder.py")
    print("3. Create index: python create_index.py")
    print("\n📚 See README.md for detailed documentation")


if __name__ == "__main__":
    main()
