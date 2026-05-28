#!/usr/bin/env -S uv run --offline
"""
Offline reveal.js presentation generator.
Reads slides.md.txt and generates index.html ready to be opened in the browser.
"""
# /// script
# dependencies = ["watchdog", "ansi2html"]
# ///

import argparse
import hashlib
import http.server
import re
import socketserver
import sys
import threading
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>{title}</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <meta charset="utf-8">

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

    <script src="https://cdn.jsdelivr.net/npm/webcomponent-qr-code@1.3.0/dist/index.min.js"></script>

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
        width: 1920,      // base width (16:9 ratio)
        height: 1080,     // base height (16:9 ratio)
        margin: 0.04,     // optional spacing around slides
        minScale: 0.2,    // how small slides can scale
        maxScale: 2.0,    // how large slides can scale
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


def extract_title(content):
    """Extract the title from a special comment or the first markdown heading.

    First checks for a comment like: <!-- title: Custom Title -->
    If not found, uses the first markdown heading.
    Falls back to "Presentation" if neither is found.
    """
    # Check for special title comment first
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('<!--') and 'title:' in line.lower():
            # Extract title from comment: <!-- title: My Title -->
            start = line.lower().find('title:')
            if start != -1:
                # Find the content after 'title:'
                title_part = line[start + 6:]  # Skip 'title:'
                # Remove the closing -->
                if '-->' in title_part:
                    title_part = title_part[:title_part.find('-->')]
                title = title_part.strip()
                if title:
                    return title

    # If no comment found, look for first markdown heading
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            # Remove the leading # symbols and strip whitespace
            title = line.lstrip('#').strip()
            if title:
                return title

    # Fallback if no heading found
    return "Presentation"


QR_COMMENT_RE = re.compile(r'<!--\s*antocuni-qr:\s*(\S+?)\s*-->')


def expand_qr_comment(match):
    url = match.group(1)
    # Strip protocol for display label
    label = re.sub(r'^https?://', '', url)
    return (
        '<p class="small">\n'
        f'<a href="{url}">\n'
        f'<qr-code data="{url}" format="svg" modulesize="8" margin="4"></qr-code>\n'
        '<br>\n'
        f'{label}\n'
        '</a>\n'
        '<br>\n'
        '</p>'
    )


# Match an ```autorun ...``` (or ```autorun x ...```) fenced block.
# The body is captured: we'll re-render it with colors from the autorun cache.
AUTORUN_BLOCK_RE = re.compile(
    r'^(```+)autorun(?:[ \t]+[^\n]*)?\n(.*?)\n\1[ \t]*$',
    re.MULTILINE | re.DOTALL,
)


def render_autorun_block(body, autorun_dir):
    """Convert an autorun block body into colorized HTML.

    For each '$ cmd' line we look up the cached raw output in
    autorun_dir/<md5(cmd)>; on a miss we keep the plain text already in the
    body. The result is a styled <pre> mimicking a terminal.
    """
    try:
        from ansi2html import Ansi2HTMLConverter
    except ImportError:
        return None

    conv = Ansi2HTMLConverter(inline=True, scheme='dracula')

    lines = body.split('\n')
    pieces = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('$ '):
            cmd = stripped[2:]
            cache = autorun_dir / hashlib.md5(cmd.encode()).hexdigest()
            pieces.append(f'$ {cmd}\n')
            if cache.exists():
                pieces.append(cache.read_text())
                # Skip subsequent non-'$ ' lines: cached output replaces them.
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('$ '):
                    i += 1
                continue
        else:
            pieces.append(line + '\n')
        i += 1

    raw = ''.join(pieces).rstrip('\n')
    inner = conv.convert(raw, full=False)
    style = (
        "background:#2E3436;color:#d4d4d4;"
        "border-radius:6px;padding:1em 1.2em;"
        "font-family:'Fira Mono','Cascadia Code','Consolas',monospace;"
        "line-height:1.4;margin:0.5em auto;"
        "white-space:pre;text-align:left;"
        "width:var(--code-max-width,75%);max-width:100%;"
        "font-size:var(--code-font-size,1.2em);"
        "overflow:auto;box-sizing:border-box;"
    )
    return f'<pre style="{style}">{inner}</pre>'


def expand_autorun_blocks(content, autorun_dir):
    """Replace each ```autorun``` fenced block with colorized HTML."""
    def repl(m):
        body = m.group(2)
        html = render_autorun_block(body, autorun_dir)
        if html is None:
            return m.group(0)
        return html

    return AUTORUN_BLOCK_RE.sub(repl, content)


def read_slides(filename):
    """Read and process the slides content."""
    filename = Path(filename)
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Expand <!-- antocuni-qr: URL --> comments into a QR-code link block
    content = QR_COMMENT_RE.sub(expand_qr_comment, content)

    # Replace ```autorun``` fenced blocks with colorized HTML, using the
    # raw output cached by autorun.py in the sibling 'autorun/' directory.
    autorun_dir = filename.parent / 'autorun'
    if autorun_dir.is_dir():
        content = expand_autorun_blocks(content, autorun_dir)

    # Apply the same indentation fix as in pyreveal.py
    content = content.replace('    ', '\t')
    return content


def generate_html(slides_content, title):
    """Generate the complete HTML with slides content."""
    return HTML_TEMPLATE.format(content=slides_content, title=title)


def build_presentation(input_file, output_file):
    """Build the presentation from input to output file."""
    try:
        slides_content = read_slides(input_file)
        title = extract_title(slides_content)
        html_content = generate_html(slides_content, title)

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


def start_server(directory, port=8000):
    """Start a local HTTP server serving `directory` in a background thread."""
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(directory), **kw
    )

    # Try a few ports if the default is busy
    httpd = None
    for p in range(port, port + 20):
        try:
            httpd = socketserver.ThreadingTCPServer(("", p), handler)
            port = p
            break
        except OSError:
            continue

    if httpd is None:
        print("Error: could not bind any port for the HTTP server", file=sys.stderr)
        return None

    httpd.daemon_threads = True
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    print(f"Serving '{directory}' at http://localhost:{port}/")
    return httpd


def watch_file(input_file, output_file):
    """Watch the input file for changes and rebuild automatically."""
    input_path = Path(input_file)
    output_path = Path(output_file)

    # Initial build
    if not build_presentation(input_path, output_path):
        return

    serve_dir = input_path.parent.resolve()
    httpd = start_server(serve_dir)

    print(f"Watching '{input_file}' for changes... (Press Ctrl+C to stop)")

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
    if httpd is not None:
        httpd.shutdown()


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
