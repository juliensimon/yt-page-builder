#!/usr/bin/env python3
"""
Tests for utility scripts
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path to import the modules
sys.path.append(str(Path(__file__).parent.parent))


class TestSetupScript(unittest.TestCase):
    """Test cases for setup.py script."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
        os.chdir(self.original_cwd)

    @patch('subprocess.run')
    def test_check_python_version_success(self, mock_run):
        """Test Python version checking with valid version."""
        from setup import check_python_version

        # Mock successful version check
        mock_run.return_value.returncode = 0

        result = check_python_version()
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_install_dependencies_success(self, mock_run):
        """Test dependency installation."""
        from setup import install_dependencies

        # Mock successful installation
        mock_run.return_value.returncode = 0

        result = install_dependencies()
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_setup_spacy_success(self, mock_run):
        """Test spaCy model setup."""
        from setup import setup_spacy

        # Mock successful spaCy download
        mock_run.return_value.returncode = 0

        result = setup_spacy()
        self.assertTrue(result)


class TestUpdateBadgesScript(unittest.TestCase):
    """Test cases for update_badges.py script."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test_readme.md"

        # Create test README with placeholder badges
        test_content = """# Test Project

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/your-username/yt-page-builder)
[![Stars](https://img.shields.io/github/stars/your-username/yt-page-builder?style=social)](https://github.com/your-username/yt-page-builder)

Test content.
"""

        with open(self.test_file, 'w') as f:
            f.write(test_content)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_update_badges_in_file_success(self):
        """Test updating badges in a file."""
        from update_badges import update_badges_in_file

        result = update_badges_in_file(str(self.test_file), "newusername", "new-repo")

        self.assertTrue(result)

        # Check that the file was updated
        with open(self.test_file, 'r') as f:
            content = f.read()

        self.assertIn("newusername/new-repo", content)
        self.assertNotIn("your-username/yt-page-builder", content)

    def test_update_badges_in_file_no_changes(self):
        """Test updating badges when no changes are needed."""
        from update_badges import update_badges_in_file

        # Create file without placeholder badges
        test_content = """# Test Project

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/actual-username/actual-repo)

Test content.
"""

        with open(self.test_file, 'w') as f:
            f.write(test_content)

        result = update_badges_in_file(str(self.test_file), "newusername", "new-repo")

        self.assertFalse(result)

    def test_update_badges_in_file_error(self):
        """Test updating badges with file error."""
        from update_badges import update_badges_in_file

        result = update_badges_in_file("nonexistent_file.md", "newusername", "new-repo")

        self.assertFalse(result)


class TestExampleScript(unittest.TestCase):
    """Test cases for example.py script."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

        # Create mock project structure
        (Path(self.temp_dir) / "audio-to-json").mkdir()
        (Path(self.temp_dir) / "yt-page-builder").mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
        os.chdir(self.original_cwd)

    @patch('subprocess.run')
    def test_download_video_success(self, mock_run):
        """Test video download step."""
        from example import download_video

        # Mock successful download
        mock_run.return_value.returncode = 0

        result = download_video()
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_generate_pages_success(self, mock_run):
        """Test page generation step."""
        from example import generate_pages

        # Mock successful page generation
        mock_run.return_value.returncode = 0

        result = generate_pages()
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_create_index_success(self, mock_run):
        """Test index creation step."""
        from example import create_index

        # Mock successful index creation
        mock_run.return_value.returncode = 0

        result = create_index()
        self.assertTrue(result)


class TestConfigModule(unittest.TestCase):
    """Test cases for config.py module."""

    def test_yt_page_builder_config_structure(self):
        """Test that YT_PAGE_BUILDER_CONFIG has required keys."""
        from config import YT_PAGE_BUILDER_CONFIG

        required_keys = [
            'input_dir',
            'output_dir',
            'logs_dir',
            'max_workers',
            'chunk_size',
            'api_url',
            'model',
            'max_tokens',
            'temperature',
            'include_transcript',
            'include_tags',
            'include_description',
            'include_links',
            'links',
        ]

        for key in required_keys:
            self.assertIn(key, YT_PAGE_BUILDER_CONFIG)

    def test_audio_to_json_config_structure(self):
        """Test that AUDIO_TO_JSON_CONFIG has required keys."""
        from config import AUDIO_TO_JSON_CONFIG

        required_keys = [
            'output_dir',
            'audio_format',
            'audio_quality',
            'whisper_model',
            'language',
            'task',
            'sample_rate',
            'chunk_length',
            'stride_length',
        ]

        for key in required_keys:
            self.assertIn(key, AUDIO_TO_JSON_CONFIG)

    def test_common_config_structure(self):
        """Test that COMMON_CONFIG has required keys."""
        from config import COMMON_CONFIG

        required_keys = ['log_level', 'log_format', 'video_patterns', 'date_formats']

        for key in required_keys:
            self.assertIn(key, COMMON_CONFIG)

    def test_dev_config_structure(self):
        """Test that DEV_CONFIG has required keys."""
        from config import DEV_CONFIG

        required_keys = [
            'test_mode',
            'limit_folders',
            'verbose_logging',
            'save_intermediate',
        ]

        for key in required_keys:
            self.assertIn(key, DEV_CONFIG)


if __name__ == '__main__':
    unittest.main()
