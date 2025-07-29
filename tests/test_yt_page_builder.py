#!/usr/bin/env python3
"""
Tests for YouTube Page Builder
"""

import json
import os
import shutil

# Add parent directory to path to import the module
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).parent.parent / "yt-page-builder"))

from yt_page_builder import YouTubePageBuilder


class TestYouTubePageBuilder(unittest.TestCase):
    """Test cases for YouTubePageBuilder class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.logs_dir = Path(self.temp_dir) / "logs"

        # Create directories
        self.input_dir.mkdir()
        self.output_dir.mkdir()
        self.logs_dir.mkdir()

        # Initialize builder
        self.builder = YouTubePageBuilder(
            input_dir=str(self.input_dir), output_dir=str(self.output_dir)
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_parse_folder_name_valid(self):
        """Test parsing valid folder names."""
        test_cases = [
            (
                "20250103_Video_Title_Here",
                {'date': 'January 03, 2025', 'title': 'Video Title Here'},
            ),
            (
                "20241225_Christmas_Special",
                {'date': 'December 25, 2024', 'title': 'Christmas Special'},
            ),
            (
                "20240101_New_Year_Dash-Test",
                {'date': 'January 01, 2024', 'title': 'New Year Dash Test'},
            ),
        ]

        for folder_name, expected in test_cases:
            with self.subTest(folder_name=folder_name):
                result = self.builder.parse_folder_name(folder_name)
                self.assertEqual(result, expected)

    def test_parse_folder_name_invalid(self):
        """Test parsing invalid folder names."""
        test_cases = [
            "invalid_folder_name",
            "20250103",
            "Video_Title_Here",
            "20250103",
            "",
        ]

        for folder_name in test_cases:
            with self.subTest(folder_name=folder_name):
                result = self.builder.parse_folder_name(folder_name)
                self.assertEqual(result['date'], 'Unknown Date')
                self.assertEqual(
                    result['title'], folder_name.replace('_', ' ').replace('-', ' ')
                )

    def test_get_video_id_success(self):
        """Test extracting video ID from info.json."""
        # Create test folder and info.json
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        info_json = {
            "id": "dQw4w9WgXcQ",
            "title": "Test Video",
            "upload_date": "20250103",
        }

        with open(test_folder / "Test_Video.info.json", 'w') as f:
            json.dump(info_json, f)

        video_id = self.builder.get_video_id(test_folder)
        self.assertEqual(video_id, "dQw4w9WgXcQ")

    def test_get_video_id_missing_file(self):
        """Test handling missing info.json file."""
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        video_id = self.builder.get_video_id(test_folder)
        self.assertIsNone(video_id)

    def test_get_video_id_invalid_json(self):
        """Test handling invalid JSON in info.json."""
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        with open(test_folder / "Test_Video.info.json", 'w') as f:
            f.write("invalid json content")

        video_id = self.builder.get_video_id(test_folder)
        self.assertIsNone(video_id)

    def test_get_video_description_success(self):
        """Test reading video description."""
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        description_content = (
            "This is a test video description with https://example.com link."
        )

        with open(test_folder / "Test_Video.description", 'w') as f:
            f.write(description_content)

        description = self.builder.get_video_description(test_folder)
        self.assertIn("This is a test video description", description)
        self.assertIn("https://example.com", description)

    def test_get_video_description_missing_file(self):
        """Test handling missing description file."""
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        description = self.builder.get_video_description(test_folder)
        self.assertEqual(description, "No description available.")

    def test_get_video_transcript_success(self):
        """Test reading video transcript."""
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        transcript_content = "This is a test transcript with some content."

        with open(test_folder / "Test_Video_transcription.json", 'w') as f:
            json.dump({"transcription": transcript_content}, f)

        transcript = self.builder.get_video_transcript(test_folder)
        self.assertIn("This is a test transcript", transcript)

    def test_get_video_transcript_missing_file(self):
        """Test handling missing transcript file."""
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        transcript = self.builder.get_video_transcript(test_folder)
        self.assertEqual(transcript, "No transcript available.")

    @patch('yt_page_builder.requests.post')
    def test_clean_transcript_with_ai_success(self, mock_post):
        """Test AI transcript cleaning with successful API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Cleaned transcript content."}}]
        }
        mock_post.return_value = mock_response

        transcript = "Original transcript content."
        result = self.builder.clean_transcript_with_ai(transcript)

        self.assertEqual(result, "Cleaned transcript content.")
        mock_post.assert_called_once()

    @patch('yt_page_builder.requests.post')
    def test_clean_transcript_with_ai_failure(self, mock_post):
        """Test AI transcript cleaning with API failure."""
        mock_post.side_effect = Exception("API Error")

        transcript = "Original transcript content."
        result = self.builder.clean_transcript_with_ai(transcript)

        self.assertEqual(result, transcript)

    def test_generate_tags_success(self):
        """Test tag generation from transcript."""
        transcript = "This is a video about machine learning and artificial intelligence. We discuss deep learning, neural networks, and data science."

        tags = self.builder.generate_tags(transcript)

        self.assertIsInstance(tags, list)
        self.assertGreater(len(tags), 0)
        self.assertLessEqual(len(tags), 5)

        # Check that tags are strings
        for tag in tags:
            self.assertIsInstance(tag, str)

    def test_generate_tags_empty_transcript(self):
        """Test tag generation with empty transcript."""
        tags = self.builder.generate_tags("")

        self.assertIsInstance(tags, list)
        self.assertEqual(len(tags), 0)

    def test_generate_html_success(self):
        """Test HTML generation."""
        video_data = {
            'title': 'Test Video',
            'date': 'January 03, 2025',
            'video_id': 'dQw4w9WgXcQ',
            'description': 'Test description',
            'transcript': 'Test transcript',
            'tags': ['test', 'video', 'example'],
        }

        html = self.builder.generate_html(video_data)

        self.assertIn('Test Video', html)
        self.assertIn('January 03, 2025', html)
        self.assertIn('dQw4w9WgXcQ', html)
        self.assertIn('Test description', html)
        self.assertIn('Test transcript', html)
        self.assertIn('test', html)
        self.assertIn('video', html)
        self.assertIn('example', html)

    def test_process_folder_success(self):
        """Test successful folder processing."""
        # Create test folder with all required files
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        # Create info.json
        info_json = {
            "id": "dQw4w9WgXcQ",
            "title": "Test Video",
            "upload_date": "20250103",
        }
        with open(test_folder / "Test_Video.info.json", 'w') as f:
            json.dump(info_json, f)

        # Create description
        with open(test_folder / "Test_Video.description", 'w') as f:
            f.write("Test video description")

        # Create transcript
        with open(test_folder / "Test_Video_transcription.json", 'w') as f:
            json.dump({"transcription": "Test transcript content"}, f)

        result = self.builder.process_folder(test_folder)

        self.assertTrue(result['success'])
        self.assertIsNone(result['error'])
        self.assertIn('duration', result)

        # Check that HTML file was created
        html_file = self.output_dir / "20250103_Test_Video.html"
        self.assertTrue(html_file.exists())

    def test_process_folder_missing_video_id(self):
        """Test folder processing with missing video ID."""
        test_folder = self.input_dir / "20250103_Test_Video"
        test_folder.mkdir()

        result = self.builder.process_folder(test_folder)

        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
        self.assertIn('Could not find video ID', result['error'])

    def test_generate_links_html_with_config(self):
        """Test links HTML generation with config."""
        with patch(
            'yt_page_builder.YT_PAGE_BUILDER_CONFIG',
            {
                'links': {
                    'website': 'https://example.com',
                    'youtube_channel': 'https://youtube.com/@example',
                }
            },
        ):
            links_html = self.builder._generate_links_html()
            self.assertIn('https://example.com', links_html)
            self.assertIn('https://youtube.com/@example', links_html)
            self.assertIn('Website', links_html)
            self.assertIn('Youtube Channel', links_html)

    def test_generate_links_html_empty_config(self):
        """Test links HTML generation with empty config."""
        with patch('yt_page_builder.YT_PAGE_BUILDER_CONFIG', {'links': {}}):
            links_html = self.builder._generate_links_html()
            self.assertEqual(links_html, "")

    def test_generate_links_html_import_error(self):
        """Test links HTML generation with import error."""
        with patch('yt_page_builder.YT_PAGE_BUILDER_CONFIG', {}, create=True):
            with patch('builtins.__import__', side_effect=ImportError):
                links_html = self.builder._generate_links_html()
                self.assertEqual(links_html, "")


if __name__ == '__main__':
    unittest.main()
