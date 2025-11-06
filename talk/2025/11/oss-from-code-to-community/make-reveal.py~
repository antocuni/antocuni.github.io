#!/usr/bin/env python3
"""
Offline reveal.js presentation generator.
Reads slides.md.txt and generates index.html ready to be opened in the browser.
"""
# /// script
# dependencies = ["watchdog"]
# ///

import argparse
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Tracing JIT and real world Python</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">

    <!-- Reveal.js CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reset.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/white.min.css">

    <!-- Highlight.js -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/zenburn.min.css">

    <!-- Reveal.js Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/highlight/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/markdown/markdown.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/plugin/notes/notes.js"></script>
</head>
<body>

<div class="reveal">
  <div class="slides">
    <section data-markdown>
      <textarea data-template>
{content}
      </textarea>
    </section>
  </div>
</div>

<script>
    Reveal.initialize({{
        plugins: [
            RevealMarkdown,
            RevealHighlight,
            RevealNotes
        ],
        hash: true
    }});
</script>

</body>
</html>"""


def read_slides(filename):
    """Read and process the slides content."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply the same indentation fix as in pyreveal.py
    content = content.replace('    ', '\t')
    return content


def generate_html(slides_content):
    """Generate the complete HTML with slides content."""
    return HTML_TEMPLATE.format(content=slides_content)


def build_presentation(input_file, output_file):
    """Build the presentation from input to output file."""
    try:
        slides_content = read_slides(input_file)
        html_content = generate_html(slides_content)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Generated '{output_file}' successfully!")
        return True
    except Exception as e:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Error: {e}", file=sys.stderr)
        return False


class SlidesHandler(FileSystemEventHandler):
    """Handle file system events for slides file."""

    def __init__(self, input_file, output_file):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)

    def on_modified(self, event):
        if not event.is_directory and Path(event.src_path) == self.input_file:
            build_presentation(self.input_file, self.output_file)


def watch_file(input_file, output_file):
    """Watch the input file for changes and rebuild automatically."""
    input_path = Path(input_file)

    print(f"Watching '{input_file}' for changes... (Press Ctrl+C to stop)")

    # Initial build
    if not build_presentation(input_path, Path(output_file)):
        return

    event_handler = SlidesHandler(input_path, output_file)
    observer = Observer()
    observer.schedule(event_handler, str(input_path.parent), recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching.")
    observer.join()


def main():
    parser = argparse.ArgumentParser(description='Generate reveal.js presentation from markdown')
    parser.add_argument('input', nargs='?', default='slides.md.txt',
                       help='Input markdown file (default: slides.md.txt)')
    parser.add_argument('-o', '--output', default='index.html',
                       help='Output HTML file (default: index.html)')
    parser.add_argument('-w', '--watch', action='store_true',
                       help='Watch input file for changes and rebuild automatically')

    args = parser.parse_args()

    input_file = Path(args.input)
    output_file = Path(args.output)

    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    if args.watch:
        watch_file(input_file, output_file)
    else:
        if build_presentation(input_file, output_file):
            print(f"Open it in your browser to view the presentation.")


if __name__ == '__main__':
    main()
