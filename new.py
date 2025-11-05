#!/usr/bin/env python3
"""
Unified script to create new talks or blog posts from templates.
Combines functionality from newtalk.sh and newpost.sh.
"""
import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


def create_talk():
    """Create a new talk from template."""
    # Get date with default to today
    default_date = date.today().strftime("%Y-%m-%d")
    date_input = input(f"Enter date [{default_date}]: ").strip()
    date_str = date_input if date_input else default_date

    # Extract year and month
    year, month, _ = date_str.split("-")

    # Get directory name
    dir_name = input("Enter directory name: ").strip()
    if not dir_name:
        print("Error: directory name cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Create target directory
    script_dir = Path(__file__).parent
    target_dir = script_dir / "blog" / "talk" / year / month / dir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy template files
    template_dir = script_dir / "blog" / "talk" / "template"
    if not template_dir.exists():
        print(f"Error: template not found at {template_dir}", file=sys.stderr)
        sys.exit(1)

    for item in template_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, target_dir)
        elif item.is_dir():
            shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)

    print(f"New talk created at {target_dir}")
    print("Files copied from template")


def create_post():
    """Create a new blog post from template."""
    # Built-in template
    template = """---
draft: true
date: {date}
title: "{title}"
categories:
  - Post
tags:
  - spy

---

# {title}

<!-- more -->
"""

    # Get slug
    slug = input("Slug (e.g. spy-pycon-de): ").strip()
    if not slug:
        print("Error: slug cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Compute year/month and format date
    today = date.today()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    date_str = today.strftime("%Y-%m-%d")

    # Paths
    script_dir = Path(__file__).parent
    base_dir = script_dir / "blog" / "posts"
    new_dir = base_dir / year / f"{month}-{slug}"
    new_file = new_dir / "index.md"

    # Create directory
    new_dir.mkdir(parents=True, exist_ok=True)

    # Write template with today's date and slug as title
    new_file.write_text(template.format(date=date_str, title=slug))

    print(f"New post created at {new_dir}")

    # Open in editor using `e`
    try:
        subprocess.run(["e", str(new_file)], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"Could not open editor. File created at: {new_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Create new talks or blog posts from templates"
    )
    parser.add_argument(
        "type",
        choices=["talk", "post"],
        help="Type of content to create"
    )

    args = parser.parse_args()

    if args.type == "talk":
        create_talk()
    elif args.type == "post":
        create_post()


if __name__ == "__main__":
    main()
