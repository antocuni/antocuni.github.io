#!/usr/bin/env python3
"""
List all talks found in blog/talk/**/index.html
"""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='List all talks with their URLs')
    parser.add_argument('--local', action='store_true',
                        help='Print local URLs (http://localhost:8000/...)')
    args = parser.parse_args()

    # Find all talk index.html files
    base_dir = Path(__file__).parent
    blog_dir = base_dir / 'blog' / 'talk'

    if not blog_dir.exists():
        print(f"Error: {blog_dir} does not exist")
        return

    # Find all index.html files under blog/talk
    talks = []
    for index_file in blog_dir.glob('**/index.html'):
        # Get relative path from blog/talk
        rel_path = index_file.relative_to(blog_dir)
        # Remove the index.html part
        talk_path = rel_path.parent

        # Extract date components for sorting
        parts = talk_path.parts
        if len(parts) >= 2:
            year = parts[0]
            month = parts[1]
            # Create sort key as YYYY-MM
            sort_key = f"{year}-{month}"
            talks.append((sort_key, talk_path))

    # Sort by date
    talks.sort(key=lambda x: x[0])

    # Print URLs
    if args.local:
        base_url = 'http://localhost:8000'
    else:
        base_url = 'https://antocuni.eu'

    for _, talk_path in talks:
        url = f"{base_url}/talk/{talk_path}/"
        print(url)


if __name__ == '__main__':
    main()
