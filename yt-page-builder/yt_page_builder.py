#!/usr/bin/env python3
"""
YouTube Page Builder CLI Tool

This tool processes YouTube video folders in the 'input' directory and generates
HTML pages in the 'output' directory with embedded videos, descriptions, and links.
"""

import argparse
import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from tqdm import tqdm


class YouTubePageBuilder:
    def __init__(
        self, input_dir: str = "input", output_dir: str = "output", max_workers: int = 5
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.output_dir.mkdir(exist_ok=True)

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration."""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler('logs/error.log'), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def parse_folder_name(self, folder_name: str) -> Dict[str, str]:
        """Parse folder name to extract date and video info."""
        # Pattern: YYYYMMDD_Video_Title_here
        pattern = r'^(\d{8})_(.+)$'
        match = re.match(pattern, folder_name)

        if match:
            date_str = match.group(1)
            title = match.group(2)

            # Parse date
            try:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                formatted_date = date_obj.strftime('%B %d, %Y')
            except ValueError:
                formatted_date = date_str

            return {
                'date': formatted_date,
                'title': title.replace('_', ' ').replace('-', ' '),
            }

        return {
            'date': 'Unknown Date',
            'title': folder_name.replace('_', ' ').replace('-', ' '),
        }

    def get_video_id(self, folder_path: Path) -> Optional[str]:
        """Extract video ID from info.json file."""
        info_files = list(folder_path.glob("*info.json"))
        if not info_files:
            return None

        try:
            with open(info_files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('id')
        except (json.JSONDecodeError, IOError):
            return None

    def get_video_description(self, folder_path: Path) -> str:
        """Get video description from .description file."""
        desc_files = list(folder_path.glob("*.description"))
        if not desc_files:
            return "No description available."

        try:
            with open(desc_files[0], 'r', encoding='utf-8') as f:
                description = f.read().strip()

                # Convert timestamps to clickable links
                import re

                # Pattern to match timestamps (MM:SS or HH:MM:SS format)
                timestamp_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)'

                def replace_timestamp(match):
                    timestamp = match.group(1)
                    # Convert timestamp to seconds for YouTube URL
                    parts = timestamp.split(':')
                    if len(parts) == 2:
                        # MM:SS format
                        minutes, seconds = parts
                        total_seconds = int(minutes) * 60 + int(seconds)
                    elif len(parts) == 3:
                        # HH:MM:SS format
                        hours, minutes, seconds = parts
                        total_seconds = (
                            int(hours) * 3600 + int(minutes) * 60 + int(seconds)
                        )
                    else:
                        return timestamp

                    # Get video ID for the URL
                    video_id = self.get_video_id(folder_path)
                    if video_id:
                        return f'<a href="https://www.youtube.com/watch?v={video_id}&t={total_seconds}" target="_blank" rel="noopener noreferrer">{timestamp}</a>'
                    else:
                        return timestamp

                # Convert URLs to clickable links
                url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

                def replace_url(match):
                    url = match.group(0)
                    # Skip if it's an email address
                    if '@' in url and not url.startswith(
                        ('http://', 'https://', 'www.')
                    ):
                        return url

                    # Add https:// if missing
                    if url.startswith('www.'):
                        url = 'https://' + url

                    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'

                # Replace URLs with clickable links
                description = re.sub(url_pattern, replace_url, description)

                # Replace timestamps with clickable links
                description = re.sub(timestamp_pattern, replace_timestamp, description)

                return description
        except IOError:
            return "No description available."

    def get_video_transcript(self, folder_path: Path) -> str:
        """Get video transcript from .json file and clean it with AI."""
        transcript_files = list(folder_path.glob("*transcription.json"))
        if not transcript_files:
            return "No transcript available."

        try:
            with open(transcript_files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
                transcript = data.get('transcription', '')

                if not transcript:
                    return "No transcript content available."

                # Clean transcript with AI
                return self.clean_transcript_with_ai(transcript)

        except (json.JSONDecodeError, IOError, UnicodeDecodeError) as e:
            return "Error reading transcript file."

    def clean_transcript_with_ai(self, transcript: str) -> str:
        """Clean transcript using Arcee Virtuoso Small model with chunking for long texts."""
        api_key = os.getenv('TOGETHER_API_KEY')
        if not api_key:
            self.logger.warning(
                "TOGETHER_API_KEY not found, returning original transcript"
            )
            return transcript

        try:
            # If transcript is short enough, process it directly
            if len(transcript) <= 32000:
                cleaned_transcript = self._clean_transcript_chunk(transcript, api_key)
                # Apply the same formatting normalization
                return self._normalize_paragraph_formatting(cleaned_transcript)

            # For long transcripts, split into chunks and process each
            self.logger.info(
                f"Transcript too long ({len(transcript)} chars), processing in chunks..."
            )

            # Split transcript into chunks of ~32k characters with overlap
            chunk_size = 32000
            overlap = 2000  # Overlap to maintain context between chunks

            chunks = []
            start = 0
            while start < len(transcript):
                end = min(start + chunk_size, len(transcript))

                # Try to break at a sentence boundary
                if end < len(transcript):
                    # Look for sentence endings within the last 500 characters
                    search_start = max(start + chunk_size - 500, start)
                    for i in range(end - 1, search_start, -1):
                        if transcript[i] in '.!?':
                            end = i + 1
                            break

                chunk = transcript[start:end]
                chunks.append((start, end, chunk))

                # Move start position, accounting for overlap
                start = end - overlap if end < len(transcript) else end

            # Process each chunk
            cleaned_chunks = []
            for i, (start, end, chunk) in enumerate(chunks):
                self.logger.info(
                    f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)..."
                )
                cleaned_chunk = self._clean_transcript_chunk(
                    chunk, api_key, i, len(chunks)
                )
                cleaned_chunks.append((start, end, cleaned_chunk))

            # Combine cleaned chunks, handling overlaps
            combined_transcript = self._combine_chunks_without_duplication(
                cleaned_chunks, transcript
            )

            # Final pass to clean up any artifacts from chunking
            if len(combined_transcript) <= 32000:
                self.logger.info("Performing final cleanup pass...")
                combined_transcript = self._clean_transcript_chunk(
                    combined_transcript, api_key
                )

            # Final normalization to ensure consistent formatting
            combined_transcript = self._normalize_paragraph_formatting(
                combined_transcript
            )

            return combined_transcript

        except Exception as e:
            self.logger.error(f"Error in transcript cleaning: {str(e)}")
            return transcript

    def _combine_chunks_without_duplication(self, cleaned_chunks, original_transcript):
        """Combine cleaned chunks without duplication by using original positions."""
        if not cleaned_chunks:
            return ""

        # Sort chunks by start position
        cleaned_chunks.sort(key=lambda x: x[0])

        # For the first chunk, use it entirely
        result = cleaned_chunks[0][2]
        last_end = cleaned_chunks[0][1]

        # For subsequent chunks, only add the non-overlapping portion
        for start, end, cleaned_chunk in cleaned_chunks[1:]:
            if start < last_end:
                # There's overlap, find where the overlap ends
                overlap_end = last_end

                # Find a good break point in the cleaned chunk
                # Look for the first sentence ending after the overlap
                overlap_length = last_end - start
                if overlap_length < len(cleaned_chunk):
                    # Find a sentence boundary after the overlap
                    search_start = max(overlap_length, 0)
                    for i in range(search_start, len(cleaned_chunk)):
                        if cleaned_chunk[i] in '.!?':
                            # Add a space and the non-overlapping portion
                            if result and not result.endswith(' '):
                                result += ' '
                            result += cleaned_chunk[i + 1 :].lstrip()
                            break
                    else:
                        # No sentence boundary found, add everything after overlap
                        if result and not result.endswith(' '):
                            result += ' '
                        result += cleaned_chunk[overlap_length:].lstrip()
                else:
                    # Overlap is longer than the cleaned chunk, skip this chunk
                    continue
            else:
                # No overlap, add the entire chunk
                if result and not result.endswith(' '):
                    result += ' '
                result += cleaned_chunk

            last_end = end

        # Post-process to ensure consistent paragraph formatting
        result = self._normalize_paragraph_formatting(result)

        return result

    def _normalize_paragraph_formatting(self, text: str) -> str:
        """Normalize paragraph formatting to ensure consistency."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Ensure paragraphs are separated by double line breaks
        text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Ensure the text ends with a proper paragraph break
        if text and not text.endswith('\n\n'):
            text += '\n\n'

        return text

    def _clean_transcript_chunk(
        self,
        transcript_chunk: str,
        api_key: str,
        chunk_index: int = 0,
        total_chunks: int = 1,
    ) -> str:
        """Clean a single chunk of transcript."""
        url = "https://api.together.xyz/v1/chat/completions"

        # Enhanced prompt with better paragraph formatting instructions
        context_info = ""
        if total_chunks > 1:
            context_info = f"\nNote: This is chunk {chunk_index + 1} of {total_chunks}. Maintain consistent paragraph formatting with other chunks."

        prompt = f"""Clean and improve this transcript chunk:

{transcript_chunk}

Instructions:
- Remove filler words (um, uh, you know, like, etc.) while maintaining text integrity
- Fix obvious typos and spelling errors
- Break text into logical paragraphs for better readability
- Use double line breaks (\\n\\n) to separate paragraphs
- Ensure each paragraph is a complete thought or topic
- Replace "Julian from RC" with "Julien from Arcee"
- Replace "RC" with "Arcee" (case-insensitive, word-boundary aware)
- Replace "RCMaestro" with "Arcee Maestro"
- Replace "Quen" with "Qwen" (word-boundary aware)
- Replace "DeepSeq" with "DeepSeek" (word-boundary aware)
- Do NOT rewrite content or add commentary
- Do NOT add any explanations - just return the cleaned transcript{context_info}

Cleaned transcript:"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Calculate max_tokens more conservatively
        # The prompt includes instructions + transcript chunk, so we need to be more conservative
        total_prompt_length = len(prompt)

        # Use a more conservative estimate: 3 characters per token for the prompt
        estimated_prompt_tokens = total_prompt_length // 3

        # Set a conservative max_tokens limit
        # For long transcripts, we want to ensure we don't exceed the model's limit
        if estimated_prompt_tokens > 40000:  # Very long prompt
            max_tokens = 8000  # Very conservative limit
        elif estimated_prompt_tokens > 30000:  # Long prompt
            max_tokens = 12000  # Conservative limit
        elif estimated_prompt_tokens > 20000:  # Medium prompt
            max_tokens = 15000  # Moderate limit
        else:
            # For shorter prompts, we can be more generous
            max_tokens = 20000  # Generous limit for shorter content

        # Ensure we don't exceed the model's total token limit
        max_tokens = min(max_tokens, 65537 - estimated_prompt_tokens - 1000)

        # Additional safety check
        if max_tokens <= 0:
            print(
                f"Warning: Prompt too long ({estimated_prompt_tokens} estimated tokens), using fallback max_tokens"
            )
            max_tokens = 5000  # Fallback for extremely long prompts

        # Debug information for monitoring
        if total_chunks > 1:
            print(
                f"  Chunk {chunk_index + 1}: {estimated_prompt_tokens} estimated input tokens, {max_tokens} max output tokens"
            )

        data = {
            "model": "arcee-ai/virtuoso-large",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "stop": [
                "\n\nTranscript:",
                "Transcript:",
                "---",
                "Certainly!",
                "Here is the cleaned",
                "Cleaned transcript:",
            ],
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=600)
            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text}")
                return transcript_chunk
            response.raise_for_status()

            result = response.json()
            cleaned_transcript = result['choices'][0]['message']['content'].strip()

            if cleaned_transcript:
                return cleaned_transcript
            else:
                return transcript_chunk

        except Exception as e:
            print(f"AI cleaning failed: {e}")
            return transcript_chunk

    def generate_tags(self, transcript: str) -> List[str]:
        """Generate tags using Arcee Virtuoso Small model."""
        api_key = os.getenv('TOGETHER_API_KEY')
        if not api_key:
            self.logger.warning("TOGETHER_API_KEY not found, using default tags")
            return ["AI", "Machine Learning", "Technology"]

        try:
            # For very long transcripts, use only the first portion for tag generation
            if len(transcript) > 32000:
                self.logger.info(
                    "Transcript too long for tag generation, using first 32k characters..."
                )
                transcript_for_tags = transcript[:32000]
            else:
                transcript_for_tags = transcript

            url = "https://api.together.xyz/v1/chat/completions"

            prompt = f"""Generate 3-5 relevant tags for this video transcript. Return only the tags, one per line, no numbering or bullet points:

{transcript_for_tags}

Tags:"""

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "arcee-ai/virtuoso-large",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.3,
                "stop": ["\n\n", "---", "Transcript:", "Video:"],
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            tags_text = result['choices'][0]['message']['content'].strip()

            if tags_text:
                # Parse tags from the response
                tags = [tag.strip() for tag in tags_text.split('\n') if tag.strip()]
                return tags[:5]  # Limit to 5 tags
            else:
                return ["AI", "Machine Learning", "Technology"]

        except Exception as e:
            self.logger.error(f"Error generating tags: {str(e)}")
            return ["AI", "Machine Learning", "Technology"]

    def generate_html(self, video_data: Dict[str, Any]) -> str:
        """Generate HTML page for a video."""
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.2em;
        }}
        .date {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 30px;
            font-weight: 500;
        }}
        .video-container {{
            position: relative;
            width: 100%;
            height: 0;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            margin-bottom: 30px;
        }}
        .video-container iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
            border-radius: 8px;
        }}
        .description {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            white-space: pre-wrap;
            font-size: 1em;
        }}
        .description a {{
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }}
        .description a:hover {{
            color: #2980b9;
            text-decoration: underline;
        }}
        .transcript {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            white-space: pre-wrap;
            font-size: 1em;
        }}
        .transcript h2 {{
            color: #2c3e50;
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        .tags {{
            margin-bottom: 30px;
        }}
        .tags h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        .tag {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 6px 12px;
            margin: 4px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
        }}
        .links {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .link {{
            display: inline-block;
            padding: 12px 24px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: background-color 0.3s;
        }}
        .link:hover {{
            background: #2980b9;
        }}
        .link.youtube {{
            background: #e74c3c;
        }}
        .link.youtube:hover {{
            background: #c0392b;
        }}
        @media (max-width: 600px) {{
            .container {{
                padding: 20px;
                margin: 10px;
            }}
            h1 {{
                font-size: 1.8em;
            }}
            .links {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="date">{date}</div>

        <div class="video-container">
            <iframe src="https://www.youtube.com/embed/{video_id}"
                    allowfullscreen
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
            </iframe>
        </div>

        <div class="description">{description}</div>

        <div class="transcript">
            <h2>Transcript</h2>
            {transcript}
        </div>

        <div class="tags">
            <h2>Tags</h2>
            {tags_html}
        </div>

        <div class="links">
            {links_html}
        </div>
    </div>
</body>
</html>"""

        # Convert tags to HTML
        tags_html = ''.join(
            [f'<span class="tag">{tag}</span>' for tag in video_data['tags']]
        )

        # Generate links HTML from config
        links_html = self._generate_links_html()

        return html_template.format(
            title=video_data['title'],
            date=video_data['date'],
            video_id=video_data['video_id'],
            description=video_data['description'],
            transcript=video_data['transcript'],
            tags_html=tags_html,
            links_html=links_html,
        )

    def process_folder(self, folder_path: Path) -> Dict[str, Any]:
        """Process a single video folder and return result status."""
        folder_name = folder_path.name
        result = {
            'folder': folder_name,
            'success': False,
            'error': None,
            'start_time': time.time(),
        }

        try:
            # Parse folder name
            parsed = self.parse_folder_name(folder_name)

            # Get video ID
            video_id = self.get_video_id(folder_path)
            if not video_id:
                error_msg = f"Could not find video ID for {folder_name}"
                self.logger.error(error_msg)
                result['error'] = error_msg
                return result

            # Get description and transcript
            description = self.get_video_description(folder_path)
            transcript = self.get_video_transcript(folder_path)

            # Generate tags from the cleaned transcript
            tags = self.generate_tags(transcript)

            # Prepare video data
            video_data = {
                'title': parsed['title'],
                'date': parsed['date'],
                'video_id': video_id,
                'description': description,
                'transcript': transcript,
                'tags': tags,
            }

            # Generate HTML
            html_content = self.generate_html(video_data)

            # Create output filename
            output_filename = f"{folder_name}.html"
            output_path = self.output_dir / output_filename

            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            result['success'] = True
            result['duration'] = time.time() - result['start_time']
            self.logger.info(
                f"✓ Generated: {output_filename} ({result['duration']:.2f}s)"
            )

        except Exception as e:
            error_msg = f"Error processing {folder_name}: {str(e)}"
            self.logger.error(error_msg)
            result['error'] = error_msg
            result['duration'] = time.time() - result['start_time']

        return result

    def _generate_links_html(self) -> str:
        """Generate HTML for custom links from configuration."""
        try:
            # Import config here to avoid circular imports
            import os
            import sys

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from config import YT_PAGE_BUILDER_CONFIG

            links = YT_PAGE_BUILDER_CONFIG.get('links', {})
            if not links:
                return ""

            links_html = ""
            for link_name, link_url in links.items():
                # Convert link name to display name (e.g., "youtube_channel" -> "YouTube Channel")
                display_name = link_name.replace('_', ' ').title()
                links_html += f'<a href="{link_url}" class="link">{display_name}</a>'

            return links_html
        except ImportError:
            # If config import fails, return empty string
            return ""

    def process_all_folders(self, limit: Optional[int] = None) -> None:
        """Process all video folders in the input directory using parallel processing."""
        if not self.input_dir.exists():
            self.logger.error(f"Input directory '{self.input_dir}' does not exist.")
            return

        folders = [f for f in self.input_dir.iterdir() if f.is_dir()]
        folders.sort()  # Sort alphabetically

        if limit:
            folders = folders[:limit]

        if not folders:
            self.logger.info("No folders found in input directory.")
            return

        self.logger.info(
            f"Processing {len(folders)} folder(s) with {self.max_workers} workers..."
        )
        print(f"\n🚀 Starting parallel processing of {len(folders)} videos...")
        print(f"📊 Using {self.max_workers} parallel workers")
        print("-" * 60)

        # Track results
        successful = 0
        failed = 0
        total_duration = 0
        results = []

        # Process folders in parallel with progress bar
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_folder = {
                executor.submit(self.process_folder, folder): folder
                for folder in folders
            }

            # Process completed tasks with progress bar
            with tqdm(
                total=len(folders), desc="Processing videos", unit="video"
            ) as pbar:
                for future in as_completed(future_to_folder):
                    result = future.result()
                    results.append(result)

                    if result['success']:
                        successful += 1
                        total_duration += result['duration']
                        pbar.set_postfix(
                            {
                                'Success': successful,
                                'Failed': failed,
                                'Avg Time': f"{total_duration/successful:.1f}s",
                            }
                        )
                    else:
                        failed += 1
                        pbar.set_postfix({'Success': successful, 'Failed': failed})

                    pbar.update(1)

        # Print summary
        print("\n" + "=" * 60)
        print("📈 PROCESSING SUMMARY")
        print("=" * 60)
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(successful/(successful+failed)*100):.1f}%")
        if successful > 0:
            print(f"⏱️  Average processing time: {total_duration/successful:.2f}s")
        print(f"⏱️  Total processing time: {sum(r['duration'] for r in results):.2f}s")

        # Log failed items
        failed_items = [r for r in results if not r['success']]
        if failed_items:
            print(f"\n❌ Failed items ({len(failed_items)}):")
            for item in failed_items:
                print(f"   • {item['folder']}: {item['error']}")
            self.logger.warning(
                f"Failed to process {len(failed_items)} videos. Check logs/error.log for details."
            )

        # Log successful items
        successful_items = [r for r in results if r['success']]
        if successful_items:
            print(f"\n✅ Successfully processed ({len(successful_items)}):")
            for item in successful_items:
                print(f"   • {item['folder']} ({item['duration']:.2f}s)")

        print("\n🎉 Processing complete!")
        if failed > 0:
            print("📝 Check logs/error.log for detailed error information.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML pages for YouTube videos from input folders with parallel processing"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="input",
        help="Input directory containing video folders (default: input)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output",
        help="Output directory for HTML files (default: output)",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=5,
        help="Number of parallel workers (default: 5)",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        help="Limit number of folders to process (for testing)",
    )
    parser.add_argument(
        "--folder", "-f", type=str, help="Process only a specific folder"
    )

    args = parser.parse_args()

    # Validate workers argument
    if args.workers < 1 or args.workers > 20:
        print("⚠️  Warning: Workers should be between 1 and 20. Using 5.")
        args.workers = 5

    builder = YouTubePageBuilder(args.input, args.output, args.workers)

    if args.folder:
        # Process only the specified folder
        folder_path = Path(args.input) / args.folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"🎯 Processing single folder: {args.folder}")
            result = builder.process_folder(folder_path)
            if result['success']:
                print(
                    f"✅ Successfully processed {args.folder} in {result['duration']:.2f}s"
                )
            else:
                print(f"❌ Failed to process {args.folder}: {result['error']}")
        else:
            print(f"❌ Error: Folder '{args.folder}' not found in '{args.input}'")
    else:
        # Process all folders with parallel processing
        builder.process_all_folders(args.limit)


if __name__ == "__main__":
    main()
