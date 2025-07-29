#!/usr/bin/env python3
"""
Script to update GitHub badges with your repository URL
"""

import re
import sys
from pathlib import Path


def update_badges_in_file(file_path: str, new_username: str, new_repo: str):
    """Update GitHub badges in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace the placeholder GitHub URLs
        old_pattern = r'your-username/yt-page-builder'
        new_pattern = f'{new_username}/{new_repo}'

        updated_content = re.sub(old_pattern, new_pattern, content)

        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated badges in {file_path}")
            return True
        else:
            print(f"⚠️  No changes needed in {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    """Main function to update badges."""
    print("🔧 GitHub Badge Updater")
    print("=" * 30)

    if len(sys.argv) != 3:
        print("Usage: python update_badges.py <github-username> <repository-name>")
        print("Example: python update_badges.py myusername my-yt-builder")
        sys.exit(1)

    username = sys.argv[1]
    repo_name = sys.argv[2]

    print(f"Updating badges for: {username}/{repo_name}")
    print()

    # Files to update
    files_to_update = [
        "README.md",
        "yt-page-builder/README.md",
        "audio-to-json/README.md",
    ]

    updated_count = 0
    for file_path in files_to_update:
        if Path(file_path).exists():
            if update_badges_in_file(file_path, username, repo_name):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")

    print()
    print(f"🎉 Updated {updated_count} files!")
    print()
    print("📝 Next steps:")
    print("1. Review the updated files to ensure the badges are correct")
    print("2. Commit and push your changes")
    print("3. The badges will automatically update with your repository information")


if __name__ == "__main__":
    main()
