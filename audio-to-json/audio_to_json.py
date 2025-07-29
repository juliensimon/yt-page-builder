#!/usr/bin/env python3
"""
Audio to JSON Converter using DistilWhisper and SmolLM3-3B

This script converts audio files to JSON with transcription and metadata,
and optionally cleans up transcriptions using SmolLM3-3B.
"""

import argparse
import glob
import json
import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import librosa
import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor


class AudioToMarkdownConverter:
    """Converts audio files to JSON text using Whisper."""

    def __init__(self, model_name: str = "openai/whisper-large-v3-turbo"):
        """
        Initialize the converter with DistilWhisper model.

        Args:
            model_name: The DistilWhisper model to use
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        # Check for available devices in order of preference: CUDA > MPS > CPU
        if torch.cuda.is_available():
            self.device = "cuda:0"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"

    def load_model(self):
        """Load the Whisper model and processor."""
        print(f"Loading Whisper model: {self.model_name}")
        print(f"Using device: {self.device}")

        # Load model and processor
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda:0" else torch.float32,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(self.model_name)
        print("Model loaded successfully!")

    def sanitize_title(self, title: str) -> str:
        """
        Sanitize a title for use in file paths and directory names.

        Args:
            title: The title to sanitize

        Returns:
            Sanitized title safe for file systems
        """
        if not title or title.strip() == "":
            return "untitled"

        # Remove or replace problematic characters
        # Replace common problematic characters with safe alternatives
        title = re.sub(r'[<>:"/\\|?*]', '_', title)

        # Replace multiple spaces with single space
        title = re.sub(r'\s+', ' ', title)

        # Remove leading/trailing spaces and dots
        title = title.strip(' .')

        # Limit length to avoid filesystem issues
        if len(title) > 100:
            title = title[:97] + "..."

        # Ensure it's not empty after sanitization
        if not title or title.strip() == "":
            return "untitled"

        return title

    def find_audio_files(self, directory: str = ".") -> List[str]:
        """
        Find all audio files in the specified directory.

        Args:
            directory: Directory to search for audio files

        Returns:
            List of audio file paths
        """
        audio_extensions = [
            "*.mp3",
            "*.wav",
            "*.flac",
            "*.m4a",
            "*.aac",
            "*.ogg",
            "*.opus",
            "*.wma",
            "*.aiff",
            "*.au",
        ]

        audio_files = []
        for ext in audio_extensions:
            pattern = os.path.join(directory, ext)
            audio_files.extend(glob.glob(pattern))

        return sorted(audio_files)

    def get_video_list(self, url: str, limit: Optional[int] = None) -> List[str]:
        """
        Get list of video URLs from a channel/playlist without downloading.
        """
        # Clean up the URL by removing any escaped characters
        clean_url = url.replace('\\', '')

        cmd = ["yt-dlp", "--flat-playlist", "--get-id", "--ignore-errors", clean_url]

        if limit:
            cmd.extend(["--playlist-items", f"1-{limit}"])

        try:
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            video_ids = result.stdout.strip().split('\n')
            video_ids = [vid for vid in video_ids if vid]  # Remove empty lines

            print(f"Found {len(video_ids)} video IDs")

            # Convert to full URLs
            video_urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]
            return video_urls

        except subprocess.CalledProcessError as e:
            error_msg = f"Error getting video list from {clean_url}: {e}"
            print(f"Error getting video list: {e}")
            print(f"stderr: {e.stderr}")
            logging.error(error_msg, exc_info=True)
            return []

    def download_single_video(
        self, video_url: str, output_dir: str = "."
    ) -> Optional[Dict[str, Any]]:
        """
        Download a single video and return its metadata.
        """
        # Clean up the URL by removing any escaped characters
        clean_video_url = video_url.replace('\\', '')

        # First check what title yt-dlp would extract
        print(f"Checking video title for: {clean_video_url}")
        title_cmd = [
            "yt-dlp",
            "--cookies-from-browser",
            "chrome",
            "--get-title",
            "--no-playlist",
            clean_video_url,
        ]

        try:
            title_result = subprocess.run(
                title_cmd, capture_output=True, text=True, check=True
            )
            extracted_title = title_result.stdout.strip()
            print(f"Extracted title: '{extracted_title}'")

            if "youtube video" in extracted_title.lower() or not extracted_title:
                print(
                    "WARNING: Title extraction failed, yt-dlp is using fallback title"
                )
        except subprocess.CalledProcessError as e:
            print(f"Could not extract title: {e}")

        # yt-dlp command to download audio and extract metadata
        cmd = [
            "yt-dlp",
            "--cookies-from-browser",
            "chrome",  # Use browser cookies for better metadata access
            "--extract-audio",
            "--audio-quality",
            "0",  # Best quality available
            "--write-thumbnail",
            "--write-description",
            "--write-info-json",
            "--restrict-filenames",  # This helps with title extraction
            "--output",
            os.path.join(output_dir, "%(upload_date)s_%(title)s", "%(title)s.%(ext)s"),
            "--ignore-errors",
            "--no-playlist",  # Force single video processing
            clean_video_url,
        ]

        print("Running yt-dlp command...")
        print(f"Command: {' '.join(cmd)}")

        try:
            # Run yt-dlp
            result = subprocess.run(cmd, check=True)

            # Find the downloaded audio file
            audio_files = []
            audio_extensions = ['.opus', '.m4a', '.mp3', '.webm', '.wav', '.flac']
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in audio_extensions):
                        audio_files.append(os.path.join(root, file))

            if not audio_files:
                print("No audio files found after download")
                return None

            # Get the most recently created audio file
            audio_file = max(audio_files, key=os.path.getctime)
            video_dir = os.path.dirname(audio_file)

            # Load metadata
            base_name = Path(audio_file).stem
            info_file = os.path.join(video_dir, f"{base_name}.info.json")
            description_file = os.path.join(video_dir, f"{base_name}.description")
            thumbnail_file = os.path.join(video_dir, f"{base_name}.webp")

            metadata = {}
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

            description = ""
            if os.path.exists(description_file):
                with open(description_file, 'r', encoding='utf-8') as f:
                    description = f.read()

            # Extract upload date from metadata or directory name
            upload_date = metadata.get("upload_date")
            if not upload_date:
                # Try to extract from directory name
                dir_name = os.path.basename(video_dir)
                if dir_name.startswith("20"):  # YYYY-MM-DD format
                    upload_date = dir_name[:10]

            video_info = {
                "title": metadata.get("title", base_name),
                "upload_date": upload_date,
                "description": description,
                "thumbnail": thumbnail_file if os.path.exists(thumbnail_file) else "",
                "url": clean_video_url,
                "video_id": metadata.get("id", ""),
                "channel": metadata.get("channel", ""),
                "duration": metadata.get("duration", 0),
                "audio_file": audio_file,
                "video_dir": video_dir,
            }

            return video_info

        except subprocess.CalledProcessError as e:
            error_msg = f"Error downloading video {clean_video_url}: {e}"
            print(f"Error downloading video: {e}")
            logging.error(error_msg, exc_info=True)
            return None

    def download_video_with_ytdlp(
        self, url: str, output_dir: str = ".", limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Download videos using yt-dlp and extract metadata.

        Args:
            url: YouTube URL, playlist, or channel ID
            output_dir: Directory to save downloaded files

        Returns:
            List of video metadata dictionaries
        """
        # Clean up the URL by removing any escaped characters
        clean_url = url.replace('\\', '')

        print(f"Downloading videos from: {clean_url}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # yt-dlp command to download audio and extract metadata
        cmd = [
            "yt-dlp",
            "--cookies-from-browser",
            "chrome",  # Use browser cookies for better metadata access
            "--extract-audio",
            "--audio-quality",
            "0",  # Best quality available
            "--write-thumbnail",
            "--write-description",
            "--write-info-json",
            "--output",
            os.path.join(output_dir, "%(upload_date)s_%(title)s", "%(title)s.%(ext)s"),
            "--ignore-errors",
            "--verbose",
            "--progress",
            "--newline",
            clean_url,
        ]

        # Add playlist limit if specified
        if limit:
            cmd.extend(["--playlist-items", f"1-{limit}"])
            print(f"Limiting download to first {limit} videos")

        print("Running yt-dlp command...")
        print(f"Command: {' '.join(cmd)}")
        print("Starting download with verbose output...")

        try:
            result = subprocess.run(cmd, check=True)
            print("\nDownload completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\nyt-dlp error: {e}")
            raise

        # Find downloaded files and metadata
        downloaded_videos = []

        # Find audio files recursively in subdirectories
        audio_files = []
        audio_extensions = ['.opus', '.m4a', '.mp3', '.webm', '.wav', '.flac']
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if any(file.endswith(ext) for ext in audio_extensions):
                    audio_files.append(os.path.join(root, file))

        for audio_file in audio_files:
            video_dir = os.path.dirname(audio_file)
            base_name = Path(audio_file).stem

            # Find corresponding metadata files in the same directory
            info_json = os.path.join(video_dir, f"{base_name}.info.json")
            description_file = os.path.join(video_dir, f"{base_name}.description")
            thumbnail_file = os.path.join(video_dir, f"{base_name}.webp")

            # Load metadata
            metadata = {}
            if os.path.exists(info_json):
                with open(info_json, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

            # Load description
            description = ""
            if os.path.exists(description_file):
                with open(description_file, 'r', encoding='utf-8') as f:
                    description = f.read().strip()

            # Load upload date from metadata
            upload_date = metadata.get("upload_date", "")

            video_info = {
                "audio_file": audio_file,
                "title": metadata.get("title", base_name),
                "upload_date": upload_date,
                "description": description,
                "thumbnail": thumbnail_file if os.path.exists(thumbnail_file) else None,
                "metadata": metadata,
                "video_dir": video_dir,
            }

            downloaded_videos.append(video_info)

        print(f"Found {len(downloaded_videos)} downloaded videos")
        return downloaded_videos

    def load_audio(self, file_path: str, target_sr: int = 16000) -> np.ndarray:
        """
        Load and preprocess audio file.

        Args:
            file_path: Path to the audio file
            target_sr: Target sample rate (Whisper expects 16kHz)

        Returns:
            Audio array
        """
        print(f"Loading audio file: {file_path}")

        # Load audio with librosa
        audio, sr = librosa.load(file_path, sr=target_sr)

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        return audio

    def transcribe_audio(
        self, audio: np.ndarray, language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio using DistilWhisper with proper chunking for long files.

        Args:
            audio: Audio array
            language: Language code (optional, model will auto-detect if None)

        Returns:
            Transcribed text
        """
        if self.model is None or self.processor is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        print("Transcribing audio...")

        # Calculate audio duration and chunk size
        sample_rate = 16000
        audio_duration = len(audio) / sample_rate
        chunk_duration = 25  # 25 seconds per chunk (safe for Whisper)
        chunk_samples = int(chunk_duration * sample_rate)

        print(f"Audio duration: {audio_duration:.1f} seconds")
        print(f"Processing in {chunk_duration}-second chunks...")

        transcriptions = []
        total_chunks = (len(audio) + chunk_samples - 1) // chunk_samples

        # Process audio in chunks with progress bar
        with tqdm(total=total_chunks, desc="Transcribing", unit="chunk") as pbar:
            for i in range(0, len(audio), chunk_samples):
                chunk = audio[i : i + chunk_samples]
                chunk_duration_actual = len(chunk) / sample_rate

                pbar.set_postfix(
                    {
                        "chunk": len(transcriptions) + 1,
                        "duration": f"{chunk_duration_actual:.1f}s",
                    }
                )

                # Process chunk with explicit attention mask
                inputs = self.processor(
                    chunk,
                    sampling_rate=sample_rate,
                    return_tensors="pt",
                    return_attention_mask=True,
                )

                # Move to device and ensure consistent data types
                for key in inputs:
                    if isinstance(inputs[key], torch.Tensor):
                        inputs[key] = inputs[key].to(self.device)
                        if self.device == "mps":
                            inputs[key] = inputs[key].to(torch.float32)

                # Generate transcription for chunk with safe token limit
                with torch.no_grad():
                    # Ensure attention mask is properly set
                    if "attention_mask" not in inputs:
                        # Create attention mask for the input features
                        input_features = inputs["input_features"]
                        attention_mask = torch.ones(
                            input_features.shape[:2],
                            dtype=torch.long,
                            device=input_features.device,
                        )
                        inputs["attention_mask"] = attention_mask

                    generated_ids = self.model.generate(
                        inputs["input_features"],
                        attention_mask=inputs.get("attention_mask"),
                        max_new_tokens=400,  # Safe limit to avoid token overflow
                        language=language,
                        task="transcribe",
                    )

                # Decode transcription
                chunk_transcription = self.processor.batch_decode(
                    generated_ids, skip_special_tokens=True
                )[0]

                transcriptions.append(chunk_transcription)
                pbar.update(1)

        # Combine all transcriptions
        full_transcription = " ".join(transcriptions)
        print(
            f"\nTranscription completed! Total chunks processed: {len(transcriptions)}"
        )

        return full_transcription

    def format_as_markdown(self, text: str, title: str = "Transcription") -> str:
        """
        Format transcribed text as markdown.

        Args:
            text: Transcribed text
            title: Title for the markdown document

        Returns:
            Formatted markdown text
        """
        markdown_content = f"# {title}\n\n"
        markdown_content += f"*Generated using DistilWhisper model*\n\n"
        markdown_content += "---\n\n"
        markdown_content += text.strip()
        markdown_content += "\n\n---\n\n"
        markdown_content += f"*Transcription completed*\n"

        return markdown_content

    def format_as_json(
        self,
        text: str,
        title: str = "Transcription",
        audio_file: str = "",
        video_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format transcribed text as JSON with metadata.

        Args:
            text: Transcribed text
            title: Title for the transcription
            audio_file: Path to the original audio file
            video_metadata: Additional video metadata from yt-dlp

        Returns:
            JSON-formatted dictionary
        """
        # Extract publication date from filename if possible
        publication_date = None

        # Use video metadata if available
        if video_metadata:
            publication_date = video_metadata.get("upload_date")
            if publication_date:
                # Convert YYYYMMDD format to ISO format
                try:
                    publication_date = f"{publication_date[:4]}-{publication_date[4:6]}-{publication_date[6:8]}"
                except:
                    pass

        # Fallback to local date file
        if not publication_date:
            try:
                # Look for date file with same base name (remove video ID if present)
                base_name = Path(audio_file).stem
                # Remove video ID pattern like [Zdu5UyA46io] from the end
                if '[' in base_name and ']' in base_name:
                    base_name = base_name.rsplit('[', 1)[0].strip()
                date_file = f"{base_name}_date.txt"
                if os.path.exists(date_file):
                    with open(date_file, 'r') as f:
                        publication_date = f.read().strip()
            except Exception:
                pass

        # If no date found, use current date
        if not publication_date:
            publication_date = datetime.now().isoformat()

        json_data = {
            "title": title,
            "publication_date": publication_date,
            "transcription": text.strip(),
        }

        # Add video metadata if available
        if video_metadata:
            json_data.update(
                {
                    "video_id": video_metadata.get("metadata", {}).get("id"),
                    "channel": video_metadata.get("metadata", {}).get("channel"),
                    "channel_id": video_metadata.get("metadata", {}).get("channel_id"),
                    "duration": video_metadata.get("metadata", {}).get("duration"),
                    "view_count": video_metadata.get("metadata", {}).get("view_count"),
                    "like_count": video_metadata.get("metadata", {}).get("like_count"),
                    "description": video_metadata.get("description", ""),
                    "thumbnail": video_metadata.get("thumbnail"),
                    "audio_file": video_metadata.get("audio_file"),
                    "url": video_metadata.get("metadata", {}).get("webpage_url"),
                }
            )

        return json_data

    def convert_file(self, audio_file: str, output_file: Optional[str] = None) -> str:
        """
        Convert a single audio file to JSON.

        Args:
            audio_file: Path to the audio file
            output_file: Output JSON file path (optional, defaults to output/ directory)

        Returns:
            Path to the generated JSON file

        Note:
            The audio file is automatically deleted after transcription is complete.
        """
        # Generate output filename if not provided
        if output_file is None:
            base_name = Path(audio_file).stem
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            output_file = os.path.join("output", f"{base_name}_transcription.json")

        # Load and transcribe audio
        audio = self.load_audio(audio_file)
        transcription = self.transcribe_audio(audio)

        # Format title
        title = Path(audio_file).stem.replace("_", " ").title()

        # Format and save as JSON
        json_data = self.format_as_json(transcription, title, audio_file)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print(f"Transcription saved to: {output_file}")

        # Delete audio file after transcription is complete
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"Audio file deleted: {audio_file}")

        return output_file

    def convert_directory(
        self, directory: str = ".", output_dir: Optional[str] = "output"
    ):
        """
        Convert all audio files in a directory to JSON.

        Args:
            directory: Directory containing audio files
            output_dir: Output directory for JSON files (default: "output")
        """
        audio_files = self.find_audio_files(directory)

        if not audio_files:
            print(f"No audio files found in {directory}")
            return

        print(f"Found {len(audio_files)} audio file(s):")
        for file in audio_files:
            print(f"  - {file}")

        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Convert each file with progress indicator
        for i, audio_file in enumerate(audio_files, 1):
            try:
                print(f"\n[{i}/{len(audio_files)}] Processing: {Path(audio_file).name}")

                if output_dir:
                    base_name = Path(audio_file).stem
                    output_file = os.path.join(
                        output_dir, f"{base_name}_transcription.json"
                    )
                else:
                    output_file = None

                self.convert_file(audio_file, output_file)
                print(f"✓ Completed: {audio_file}")

            except Exception as e:
                error_msg = f"Error processing {audio_file}: {e}"
                print(f"✗ {error_msg}")
                logging.error(error_msg, exc_info=True)

    def process_videos_from_url(
        self, url: str, output_dir: str = "output", limit: Optional[int] = None
    ) -> List[str]:
        """
        Download and transcribe videos from URL one at a time.

        Args:
            url: YouTube URL, playlist, or channel ID
            output_dir: Directory to save files (default: "output")
            limit: Maximum number of videos to process

        Returns:
            List of generated JSON file paths

        Note:
            Audio files are automatically deleted after transcription is complete.
        """
        print(f"Processing videos from URL: {url}")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get video list first
        video_list = self.get_video_list(url, limit)

        if not video_list:
            print("No videos found.")
            return []

        print(f"Found {len(video_list)} videos to process")
        processed_files = []

        # Process each video one at a time
        for i, video_url in enumerate(video_list, 1):
            try:
                print(f"\n[{i}/{len(video_list)}] Processing video: {video_url}")

                # Download single video
                video_info = self.download_single_video(video_url, output_dir)

                if not video_info:
                    print(f"  ✗ Failed to download video")
                    continue

                audio_file = video_info['audio_file']
                title = video_info['title']
                video_dir = video_info['video_dir']

                print(f"  ✓ Downloaded: {title}")

                # Load and transcribe audio
                print(f"  Transcribing audio...")
                audio = self.load_audio(audio_file)
                transcription = self.transcribe_audio(audio)

                # Format as JSON
                json_data = self.format_as_json(
                    transcription, title, audio_file, video_info
                )

                # Save transcription - use the base name from the actual audio file for consistency
                base_name = os.path.splitext(os.path.basename(audio_file))[0]
                output_file = os.path.join(video_dir, f"{base_name}_transcription.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)

                print(f"  ✓ Transcription saved: {output_file}")
                processed_files.append(output_file)

                # Delete audio file after transcription is complete
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    print(f"  Audio file deleted: {audio_file}")

            except Exception as e:
                error_msg = f"Error processing video {i}: {e}"
                print(f"✗ {error_msg}")
                logging.error(error_msg, exc_info=True)

        print(
            f"\nProcessing complete! {len(processed_files)} videos processed successfully."
        )
        return processed_files


def main():
    """Main function to run the audio to JSON converter."""
    # Set up logging
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('error.log'),
            logging.StreamHandler(),  # Also print to console
        ],
    )

    parser = argparse.ArgumentParser(
        description="Download YouTube videos and convert to JSON using Whisper"
    )
    parser.add_argument(
        "--directory",
        "-d",
        default=".",
        help="Directory containing audio files (default: current directory)",
    )
    parser.add_argument(
        "--output-dir", "-o", help="Output directory for JSON files (default: output)"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="openai/whisper-large-v3-turbo",
        help="Whisper model to use (default: openai/whisper-large-v3-turbo)",
    )
    parser.add_argument("--file", "-f", help="Convert a specific audio file")
    parser.add_argument(
        "--url",
        "-u",
        help="YouTube URL, playlist, or channel ID to download and transcribe",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        help="Limit number of videos to download (e.g., --limit 10 for first 10 videos)",
    )

    args = parser.parse_args()

    # Initialize converter
    converter = AudioToMarkdownConverter(model_name=args.model)

    try:
        # Load model
        converter.load_model()

        # Handle URL mode (download and transcribe)
        if args.url:
            output_dir = args.output_dir if args.output_dir else "output"
            converter.process_videos_from_url(args.url, output_dir, args.limit)
        else:
            # Convert files
            if args.file:
                # Convert single file
                if not os.path.exists(args.file):
                    print(f"Error: File '{args.file}' not found")
                    return

                converter.convert_file(args.file)
            else:
                # Convert all audio files in directory
                output_dir = args.output_dir if args.output_dir else "output"
                converter.convert_directory(args.directory, output_dir)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
