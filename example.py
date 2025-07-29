#!/usr/bin/env python3
"""
Example script demonstrating YouTube Page Builder usage
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


def download_video():
    """Download a sample video for demonstration."""
    print("\n📥 Step 1: Downloading a sample video...")

    # Example video URL (replace with your own)
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll example

    print(f"Using sample video: {video_url}")
    print("You can replace this with any YouTube video URL")
    print("Edit this script to use your own video URLs")

    # Change to audio-to-json directory
    os.chdir("audio-to-json")

    # Download the video
    command = f"python audio_to_json.py --url '{video_url}'"
    success = run_command(command, "Downloading video and generating transcription")

    if success:
        print("✅ Video downloaded successfully!")
        print("📁 Check the output directory for downloaded files")
    else:
        print("❌ Video download failed")
        return False

    return True


def generate_pages():
    """Generate HTML pages from downloaded videos."""
    print("\n📄 Step 2: Generating HTML pages...")

    # Change to yt-page-builder directory
    os.chdir("../yt-page-builder")

    # Copy downloaded files to input directory (if they exist)
    if os.path.exists("../audio-to-json/output"):
        import shutil

        for item in os.listdir("../audio-to-json/output"):
            src = os.path.join("../audio-to-json/output", item)
            dst = os.path.join("input", item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"✅ Copied {item} to input directory")

    # Generate HTML pages
    command = "python yt_page_builder.py --limit 1"
    success = run_command(command, "Generating HTML pages")

    if success:
        print("✅ HTML pages generated successfully!")
        print("📁 Check the output directory for generated HTML files")
    else:
        print("❌ HTML generation failed")
        return False

    return True


def create_index():
    """Create an index page."""
    print("\n📋 Step 3: Creating index page...")

    command = "python create_index.py"
    success = run_command(command, "Creating index page")

    if success:
        print("✅ Index page created successfully!")
        print("📁 Check output/index.html for the index page")
    else:
        print("❌ Index page creation failed")
        return False

    return True


def main():
    """Main example function."""
    print("🎬 YouTube Page Builder - Example Usage")
    print("=" * 50)
    print()
    print("💡 See a real-world example: https://www.julien.org/youtube/2025/index.html")
    print()

    # Check if we're in the right directory
    if not os.path.exists("audio-to-json") or not os.path.exists("yt-page-builder"):
        print("❌ Please run this script from the project root directory")
        print("   (where audio-to-json/ and yt-page-builder/ directories are located)")
        sys.exit(1)

    # Store original directory
    original_dir = os.getcwd()

    try:
        # Step 1: Download video
        if not download_video():
            print("\n❌ Example failed at video download step")
            sys.exit(1)

        # Step 2: Generate pages
        if not generate_pages():
            print("\n❌ Example failed at page generation step")
            sys.exit(1)

        # Step 3: Create index
        if not create_index():
            print("\n❌ Example failed at index creation step")
            sys.exit(1)

        print("\n🎉 Example completed successfully!")
        print("\n📁 Generated files:")
        print("   - audio-to-json/output/: Downloaded video files")
        print("   - yt-page-builder/output/: Generated HTML pages")
        print("   - yt-page-builder/output/index.html: Index page")

        print("\n🌐 To view the pages:")
        print("   1. Open yt-page-builder/output/index.html in your browser")
        print("   2. Or open any individual HTML file in the output directory")

    except KeyboardInterrupt:
        print("\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Return to original directory
        os.chdir(original_dir)


if __name__ == "__main__":
    main()
