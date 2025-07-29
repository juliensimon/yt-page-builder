#!/usr/bin/env python3
"""
Development Setup Script
Installs pre-commit hooks and development dependencies
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
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


def main():
    """Main setup function."""
    print("🚀 Setting up development environment...")
    print()

    # Install development dependencies
    if not run_command(
        "pip install -r requirements-dev.txt", "Installing development dependencies"
    ):
        return False

    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False

    # Run pre-commit on all files to format them
    print("🎨 Formatting all Python files with black and isort...")
    if not run_command("pre-commit run --all-files", "Running pre-commit on all files"):
        print("⚠️  Some files may need manual formatting")

    print()
    print("✅ Development environment setup complete!")
    print()
    print("📋 What was installed:")
    print("• pre-commit hooks (black, isort, and other checks)")
    print("• Development dependencies (pytest, flake8, mypy, etc.)")
    print("• All Python files have been formatted")
    print()
    print("🔧 Next steps:")
    print("• Pre-commit hooks will run automatically on every commit")
    print("• Run 'pre-commit run --all-files' to format all files")
    print("• Run 'black .' to format with black only")
    print("• Run 'isort .' to sort imports only")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
