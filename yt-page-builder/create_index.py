#!/usr/bin/env python3
"""
Create an index page for all generated YouTube video pages
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def parse_filename(filename: str) -> Dict[str, str]:
    """Parse HTML filename to extract date and title."""
    # Remove .html extension
    name = filename.replace('.html', '')

    # Pattern: YYYYMMDD_Video_Title_here
    pattern = r'^(\d{8})_(.+)$'
    match = re.match(pattern, name)

    if match:
        date_str = match.group(1)
        title = match.group(2)

        # Parse date
        try:
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
            sort_date = date_obj
        except ValueError:
            formatted_date = date_str
            sort_date = datetime.min

        return {
            'date': formatted_date,
            'title': title.replace('_', ' ').replace('-', ' '),
            'filename': filename,
            'sort_date': sort_date,
        }

    return {
        'date': 'Unknown Date',
        'title': name.replace('_', ' ').replace('-', ' '),
        'filename': filename,
        'sort_date': datetime.min,
    }


def _generate_links_html() -> str:
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


def generate_index_html(videos: List[Dict[str, str]]) -> str:
    """Generate index HTML page."""
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Videos Collection</title>
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
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 1.2em;
            text-align: center;
            margin-bottom: 40px;
        }}
        .video-list {{
            display: grid;
            gap: 20px;
        }}
        .video-item {{
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .video-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .video-title {{
            color: #2c3e50;
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 8px;
            text-decoration: none;
        }}
        .video-title:hover {{
            color: #3498db;
        }}
        .video-date {{
            color: #7f8c8d;
            font-size: 0.95em;
            font-weight: 500;
        }}
        .stats {{
            text-align: center;
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 30px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .links {{
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 40px;
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
                font-size: 2em;
            }}
            .video-title {{
                font-size: 1.1em;
            }}
            .links {{
                flex-direction: column;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>YouTube Videos Collection</h1>
        <div class="subtitle">A curated collection of videos</div>

        <div class="stats">
            Total Videos: {total_videos} • Latest: {latest_date}
        </div>

        <div class="video-list">
{video_items}
        </div>

        <div class="links">
            {links_html}
        </div>
    </div>
</body>
</html>"""

    # Generate video items HTML
    video_items_html = ""
    for video in videos:
        video_items_html += f"""            <div class="video-item">
                <a href="{video['filename']}" class="video-title">{video['title']}</a>
                <div class="video-date">{video['date']}</div>
            </div>
"""

    # Generate links HTML
    links_html = _generate_links_html()

    return html_template.format(
        total_videos=len(videos),
        latest_date=videos[0]['date'] if videos else 'N/A',
        video_items=video_items_html,
        links_html=links_html,
    )


def main():
    output_dir = Path("output")

    if not output_dir.exists():
        print("Error: Output directory does not exist. Run yt_page_builder.py first.")
        return

    # Get all HTML files
    html_files = list(output_dir.glob("*.html"))

    if not html_files:
        print("No HTML files found in output directory.")
        return

    # Parse filenames and sort by date (newest first)
    videos = []
    for html_file in html_files:
        video_info = parse_filename(html_file.name)
        videos.append(video_info)

    # Sort by date (newest first)
    videos.sort(key=lambda x: x['sort_date'], reverse=True)

    # Generate index HTML
    index_html = generate_index_html(videos)

    # Write index file
    index_path = output_dir / "index.html"
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)
        print(f"✓ Generated index.html with {len(videos)} videos")
        print(f"✓ Latest video: {videos[0]['title']} ({videos[0]['date']})")
    except IOError as e:
        print(f"✗ Error writing index.html: {e}")


if __name__ == "__main__":
    main()
