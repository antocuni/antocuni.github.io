#!/usr/bin/env python3
"""
Convert a slides.md.txt file to a blog post with slide containers and annotation sections.

Usage:
    python annotate_slides.py slides.md.txt [output.md]
"""

import sys
import re
from pathlib import Path
from datetime import date


def extract_title_from_slides(slides_content):
    """Extract the main title from the slides content."""
    lines = slides_content.strip().split('\n')

    # Look for the first ## heading after the style section
    in_style = False
    for line in lines:
        line = line.strip()
        if line.startswith('<style>'):
            in_style = True
        elif line.startswith('</style>'):
            in_style = False
        elif not in_style and line.startswith('## '):
            return line[3:].strip()

    # Fallback: look for any heading
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        elif line.startswith('## '):
            return line[3:].strip()

    return "Slides"


def parse_slides(slides_content):
    """Parse the slides content and extract individual slides."""
    # Remove the style section at the beginning
    content = slides_content
    style_start = content.find('<style>')
    if style_start != -1:
        style_end = content.find('</style>')
        if style_end != -1:
            content = content[style_end + 8:].strip()

    # Split by slide separators
    slides = content.split('\n---\n')

    # Clean up each slide
    cleaned_slides = []
    for slide in slides:
        slide = slide.strip()
        if slide:  # Skip empty slides
            # Remove slide-specific reveal.js directives
            slide = re.sub(r'<!-- \.slide:.*? -->', '', slide, flags=re.DOTALL)
            # Remove transition directives
            slide = re.sub(r'<!-- \.slide: data-transition="none" -->', '', slide)
            cleaned_slides.append(slide)

    return cleaned_slides


def create_frontmatter(title):
    """Create the frontmatter for the blog post."""
    today = date.today()
    return f"""---
draft: true
date: {today.strftime('%Y-%m-%d')}
title: "{title}"
categories:
  - Post
tags:
  - slides
  - presentation
---"""


def create_css():
    """Create the CSS for slide styling."""
    return """<style>
.slide {
  border: 2px solid #ddd;
  border-radius: 8px;
  margin: 2em 0;
  background: #f9f9f9;
  max-width: 100%;

  /* Slide content box */
  aspect-ratio: 16 / 9;
  box-sizing: border-box;
  padding: 2em;
  background: white;
  border-radius: 6px 6px 0 0;
  border-bottom: 2px solid #eee;
  display: block;
  width: 100%;
}

.slide h1, .slide h2, .slide h3 {
  margin-top: 0;
  color: #333;
}
</style>
"""

def create_slide_div(slide_content):
    """Create a slide container div."""
    return f"""---
<div class="slide" markdown="1">
{slide_content}
</div>"""

def convert_slides_to_blog(slides_path, output_path=None):
    """Convert slides.md.txt to a blog post format."""
    slides_path = Path(slides_path)

    if output_path is None:
        output_path = slides_path.parent / "index.md"
    else:
        output_path = Path(output_path)

    # Read the slides file
    try:
        with open(slides_path, 'r', encoding='utf-8') as f:
            slides_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{slides_path}' not found.")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    # Extract title and parse slides
    title = extract_title_from_slides(slides_content)
    slides = parse_slides(slides_content)

    if not slides:
        print("No slides found in the input file.")
        return False

    # Generate the blog post content
    blog_content = []

    # Add frontmatter
    blog_content.append(create_frontmatter(title))
    blog_content.append("")

    # Add CSS
    blog_content.append(create_css())
    blog_content.append("")

    # Add title and introduction
    blog_content.append(f"# {title}")
    blog_content.append("")
    blog_content.append("This is an annotated version of the slides.")
    blog_content.append("")
    blog_content.append("<!-- more -->")
    blog_content.append("")

    # Add each slide as a div container
    for slide in slides:
        blog_content.append(create_slide_div(slide))
        blog_content.append("")

    # Write the output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(blog_content))
        print(f"Successfully converted slides to '{output_path}'")
        print(f"Found {len(slides)} slides")
        return True
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python slides_to_blog.py slides.md.txt [output.md]")
        print("Example: python slides_to_blog.py talk/slides.md.txt blog/index.md")
        sys.exit(1)

    slides_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    success = convert_slides_to_blog(slides_path, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
