#!/usr/bin/env python3
"""
Tests for create_index.py
"""

import json
import shutil

# Add parent directory to path to import the module
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).parent.parent / "yt-page-builder"))

from create_index import _generate_links_html, generate_index_html, parse_filename


class TestCreateIndex(unittest.TestCase):
    """Test cases for create_index module."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_parse_filename_valid(self):
        """Test parsing valid filenames."""
        test_cases = [
            (
                "20250103_Video_Title_Here.html",
                {
                    'date': 'January 03, 2025',
                    'title': 'Video Title Here',
                    'filename': '20250103_Video_Title_Here.html',
                    'sort_date': '2025-01-03',
                },
            ),
            (
                "20241225_Christmas_Special.html",
                {
                    'date': 'December 25, 2024',
                    'title': 'Christmas Special',
                    'filename': '20241225_Christmas_Special.html',
                    'sort_date': '2024-12-25',
                },
            ),
            (
                "20240101_New_Year_Dash-Test.html",
                {
                    'date': 'January 01, 2024',
                    'title': 'New Year Dash Test',
                    'filename': '20240101_New_Year_Dash-Test.html',
                    'sort_date': '2024-01-01',
                },
            ),
        ]

        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = parse_filename(filename)
                self.assertEqual(result['date'], expected['date'])
                self.assertEqual(result['title'], expected['title'])
                self.assertEqual(result['filename'], expected['filename'])

    def test_parse_filename_invalid(self):
        """Test parsing invalid filenames."""
        test_cases = [
            "invalid_filename.html",
            "20250103.html",
            "Video_Title_Here.html",
            "20250103",
            "",
        ]

        for filename in test_cases:
            with self.subTest(filename=filename):
                result = parse_filename(filename)
                self.assertEqual(result['date'], 'Unknown Date')
                self.assertEqual(result['filename'], filename)

    def test_generate_index_html_empty_list(self):
        """Test generating index HTML with empty video list."""
        videos = []
        html = generate_index_html(videos)

        self.assertIn('YouTube Videos Collection', html)
        self.assertIn('Total Videos: 0', html)
        self.assertIn('Latest: N/A', html)
        # The CSS class 'video-item' is in the stylesheet, so it will be present
        # We should check that there are no actual video items in the list
        self.assertNotIn('<div class="video-item">', html)

    def test_generate_index_html_with_videos(self):
        """Test generating index HTML with videos."""
        videos = [
            {
                'title': 'Test Video 1',
                'date': 'January 03, 2025',
                'filename': '20250103_Test_Video_1.html',
                'sort_date': '2025-01-03',
            },
            {
                'title': 'Test Video 2',
                'date': 'January 02, 2025',
                'filename': '20250102_Test_Video_2.html',
                'sort_date': '2025-01-02',
            },
        ]

        html = generate_index_html(videos)

        self.assertIn('YouTube Videos Collection', html)
        self.assertIn('Total Videos: 2', html)
        self.assertIn('Latest: January 03, 2025', html)
        self.assertIn('Test Video 1', html)
        self.assertIn('Test Video 2', html)
        self.assertIn('20250103_Test_Video_1.html', html)
        self.assertIn('20250102_Test_Video_2.html', html)

    def test_generate_links_html_with_config(self):
        """Test links HTML generation with config."""
        # Mock the config import in the function
        with patch('sys.path') as mock_path:
            with patch('os.path.dirname') as mock_dirname:
                with patch('os.path.abspath') as mock_abspath:
                    with patch('builtins.__import__') as mock_import:
                        # Mock the config module
                        mock_config = MagicMock()
                        mock_config.YT_PAGE_BUILDER_CONFIG = {
                            'links': {
                                'website': 'https://example.com',
                                'youtube_channel': 'https://youtube.com/@example',
                            }
                        }
                        mock_import.return_value = mock_config

                        links_html = _generate_links_html()
                        self.assertIn('https://example.com', links_html)
                        self.assertIn('https://youtube.com/@example', links_html)
                        self.assertIn('Website', links_html)
                        self.assertIn('Youtube Channel', links_html)

    def test_generate_links_html_empty_config(self):
        """Test links HTML generation with empty config."""
        # Mock the config import in the function
        with patch('sys.path') as mock_path:
            with patch('os.path.dirname') as mock_dirname:
                with patch('os.path.abspath') as mock_abspath:
                    with patch('builtins.__import__') as mock_import:
                        # Mock the config module
                        mock_config = MagicMock()
                        mock_config.YT_PAGE_BUILDER_CONFIG = {'links': {}}
                        mock_import.return_value = mock_config

                        links_html = _generate_links_html()
                        self.assertEqual(links_html, "")

    def test_generate_links_html_import_error(self):
        """Test links HTML generation with import error."""
        # Mock the config import to raise ImportError
        with patch('sys.path') as mock_path:
            with patch('os.path.dirname') as mock_dirname:
                with patch('os.path.abspath') as mock_abspath:
                    with patch('builtins.__import__', side_effect=ImportError):
                        links_html = _generate_links_html()
                        self.assertEqual(links_html, "")

    def test_index_html_structure(self):
        """Test that generated HTML has proper structure."""
        videos = [
            {
                'title': 'Test Video',
                'date': 'January 03, 2025',
                'filename': '20250103_Test_Video.html',
                'sort_date': '2025-01-03',
            }
        ]

        html = generate_index_html(videos)

        # Check for essential HTML elements
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('<html lang="en">', html)
        self.assertIn('<head>', html)
        self.assertIn('<body>', html)
        self.assertIn('<title>', html)
        self.assertIn('<style>', html)

        # Check for content elements
        self.assertIn('<h1>', html)
        self.assertIn('<div class="container">', html)
        self.assertIn('<div class="video-list">', html)
        self.assertIn('<div class="links">', html)


if __name__ == '__main__':
    unittest.main()
