#!/usr/bin/env python3
"""
Test script to verify YouTube Page Builder installation
"""

import importlib
import os
import sys
from pathlib import Path


def test_import(module_name, description):
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description} ({module_name})")
        return True
    except ImportError as e:
        print(f"❌ {description} ({module_name}): {e}")
        return False


def test_file_exists(file_path, description):
    """Test if a file exists."""
    if os.path.exists(file_path):
        print(f"✅ {description} ({file_path})")
        return True
    else:
        print(f"❌ {description} ({file_path})")
        return False


def test_directory_exists(dir_path, description):
    """Test if a directory exists."""
    if os.path.exists(dir_path):
        print(f"✅ {description} ({dir_path})")
        return True
    else:
        print(f"❌ {description} ({dir_path})")
        return False


def test_spacy_model():
    """Test if spaCy model is installed."""
    try:
        import spacy

        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy English model (en_core_web_sm)")
        return True
    except OSError:
        print(
            "❌ spaCy English model (en_core_web_sm) - Run: python -m spacy download en_core_web_sm"
        )
        return False


def main():
    """Main test function."""
    print("🧪 YouTube Page Builder - Installation Test")
    print("=" * 50)

    all_tests_passed = True

    # Test Python version
    print(f"\n🐍 Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        all_tests_passed = False
    else:
        print("✅ Python version is compatible")

    # Test required Python packages
    print("\n📦 Testing Python packages...")
    packages = [
        ("requests", "HTTP library"),
        ("tqdm", "Progress bars"),
        ("pathlib", "Path utilities"),
    ]

    # Test optional packages
    print("\n📦 Testing optional packages...")
    optional_packages = [
        ("spacy", "NLP library (optional)"),
    ]

    for package, description in packages:
        if not test_import(package, description):
            all_tests_passed = False

    for package, description in optional_packages:
        if test_import(package, description):
            print(f"✅ {description} (installed)")
        else:
            print(f"⚠️  {description} (not installed)")

    # Test spaCy model
    print("\n🧠 Testing spaCy model...")
    if not test_spacy_model():
        all_tests_passed = False

    # Test project structure
    print("\n📁 Testing project structure...")
    directories = [
        ("audio-to-json", "Audio-to-JSON component"),
        ("yt-page-builder", "YouTube Page Builder component"),
        ("yt-page-builder/input", "Input directory"),
        ("yt-page-builder/output", "Output directory"),
        ("yt-page-builder/logs", "Logs directory"),
    ]

    for directory, description in directories:
        if not test_directory_exists(directory, description):
            all_tests_passed = False

    # Test configuration files
    print("\n⚙️  Testing configuration files...")
    files = [
        ("README.md", "Main documentation"),
        ("setup.py", "Setup script"),
        ("example.py", "Example script"),
        ("config.py", "Configuration file"),
        ("requirements.txt", "Main project dependencies"),
        ("requirements-test.txt", "Test dependencies"),
        ("audio-to-json/requirements.txt", "Audio-to-JSON dependencies"),
        ("yt-page-builder/requirements.txt", "YouTube Page Builder dependencies"),
        ("audio-to-json/audio_to_json.py", "Audio-to-JSON main script"),
        ("yt-page-builder/yt_page_builder.py", "YouTube Page Builder main script"),
        ("yt-page-builder/create_index.py", "Index page generator"),
    ]

    for file_path, description in files:
        if not test_file_exists(file_path, description):
            all_tests_passed = False

    # Test script permissions
    print("\n🔧 Testing script permissions...")
    scripts = [
        ("audio-to-json/audio_to_json.py", "Audio-to-JSON script"),
        ("yt-page-builder/yt_page_builder.py", "YouTube Page Builder script"),
        ("yt-page-builder/create_index.py", "Index generator script"),
    ]

    for script_path, description in scripts:
        if os.path.exists(script_path):
            if os.access(script_path, os.X_OK):
                print(f"✅ {description} (executable)")
            else:
                print(f"⚠️  {description} (not executable)")
        else:
            print(f"❌ {description} (not found)")
            all_tests_passed = False

    # Summary
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Installation is complete.")
        print("\n📖 Next steps:")
        print("1. Run: python example.py (for a complete demo)")
        print("2. Or follow the manual steps in README.md")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n🔧 To fix common issues:")
        print("1. Run: python setup.py")
        print("2. Install missing packages: pip install <package_name>")
        print("3. Download spaCy model: python -m spacy download en_core_web_sm")

    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
