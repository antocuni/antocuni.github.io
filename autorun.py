#!/usr/bin/env python3
"""
autorun.py - Monitor blog/**/*.md and process special fenced code blocks.

USAGE
-----
    python autorun.py          # watch mode: process files as they change
    python autorun.py --help   # show this help

BLOCK TYPES
-----------

1. FILENAME BLOCKS
   Any fenced block whose first line is a comment of the form:

       # filename: hello.spy

   The rest of the block content is written to:
       <md_dir>/examples/<filename>

   The examples/ directory is created if it doesn't exist.  The file is only
   (re)written when its content has actually changed.

   Example:

       ```python
       # filename: hello.spy

       def main() -> None:
           print("Hello world!")
       ```

2. AUTORUN BLOCKS
   Fenced blocks with the info string "autorun".  Each line starting with
   "$ " is treated as a shell command.  The command is run with cwd set to
   the examples/ directory (sibling of the .md file) and its output is
   inserted immediately after the "$ ..." line.

   Commands are only run when the block contains NO output yet, i.e. every
   non-empty line starts with "$ ".  Once output has been inserted the block
   is left untouched on subsequent runs.

   ANSI escape sequences are stripped from the output automatically.

   Single command:

       ```autorun
       $ spy hello.spy
       ```

   After processing:

       ```autorun
       $ spy hello.spy
       Hello world!
       ```

   Multiple commands (blank lines between sections are fine):

       ```autorun
       $ spy build hello.spy
       [debug] build/hello

       $ ./build/hello
       Hello world!
       ```

EXTRA PATH
----------
Edit the EXTRA_PATH list near the top of this file to prepend directories to
PATH when running autorun commands.
"""

import argparse
import os
import re
ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*m')
import subprocess
from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Extra directories prepended to PATH when running autorun commands.
EXTRA_PATH = [
    '/home/antocuni/anaconda/spy/venv/bin',
]

_ENV = {**os.environ, 'PATH': ':'.join(EXTRA_PATH) + ':' + os.environ.get('PATH', '')}



# ---------------------------------------------------------------------------
# Fenced-block parser
# ---------------------------------------------------------------------------

FENCE_RE = re.compile(r'^(`{3,}|~{3,})(.*)')


def parse_blocks(lines: list[str]):
    """Yield (start, end, info, body_lines) for every fenced block.

    start / end are 0-based indices into *lines*.  start points to the
    opening fence line, end to the closing fence line.
    body_lines is the list of lines between the two fence lines (no fence
    lines included).
    """
    i = 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if m:
            fence_char = m.group(1)[0]
            fence_len = len(m.group(1))
            info = m.group(2).strip()
            start = i
            i += 1
            body: list[str] = []
            while i < len(lines):
                close = re.match(
                    rf'^{re.escape(fence_char)}{{{fence_len},}}\s*$', lines[i]
                )
                if close:
                    yield start, i, info, body
                    i += 1
                    break
                body.append(lines[i])
                i += 1
            else:
                # unclosed fence – just skip
                pass
        else:
            i += 1


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------

FILENAME_RE = re.compile(r'^#\s*filename:\s*(\S+)')


def process_md_file(md_path: Path) -> bool:
    """Scan *md_path* and apply both transformations.

    Returns True if the file was modified (autorun output inserted).
    """
    content = md_path.read_text()
    lines = content.splitlines(keepends=True)

    examples_dir = md_path.parent / 'examples'

    # --- pass 1: extract filename blocks (read-only w.r.t. the .md file) ---
    for _start, _end, _info, body_lines in parse_blocks(lines):
        if not body_lines:
            continue
        m = FILENAME_RE.match(body_lines[0])
        if not m:
            continue
        filename = m.group(1)
        examples_dir.mkdir(exist_ok=True)
        out_path = examples_dir / filename
        file_content = ''.join(body_lines[1:])
        if not out_path.exists() or out_path.read_text() != file_content:
            out_path.write_text(file_content)
            print(f'  wrote {out_path}')

    # --- pass 2: autorun blocks (may modify the .md file) ---
    # Iterate in reverse so that inserting lines doesn't shift earlier indices.
    blocks = list(parse_blocks(lines))
    modified = False

    for start, end, info, body_lines in reversed(blocks):
        if info != 'autorun':
            continue
        if not body_lines:
            continue

        # "No output yet" means every non-empty line starts with '$ '.
        has_output = any(
            l.strip() and not l.strip().startswith('$ ')
            for l in body_lines
        )
        if has_output:
            continue

        # Must contain at least one command line.
        cmd_lines = [l for l in body_lines if l.strip().startswith('$ ')]
        if not cmd_lines:
            continue

        cwd = examples_dir if examples_dir.is_dir() else md_path.parent

        # Rebuild the body: after each '$ cmd' line insert its output.
        new_body: list[str] = []
        for line in body_lines:
            new_body.append(line)
            stripped = line.rstrip('\n').rstrip('\r')
            if not stripped.startswith('$ '):
                continue
            cmd = stripped[2:]
            print(f'  running ({cwd.name}/): {cmd}')
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=cwd,
                    env=_ENV,
                )
                output = result.stdout
                if result.returncode != 0 and result.stderr:
                    output += result.stderr
                output = ANSI_ESCAPE_RE.sub('', output)
            except Exception as exc:
                output = f'ERROR: {exc}\n'
            output_lines = output.splitlines(keepends=True)
            if output_lines and not output_lines[-1].endswith('\n'):
                output_lines[-1] += '\n'
            new_body.extend(output_lines)

        # Replace the block body in-place (start+1 .. end are the body lines).
        lines[start + 1:end] = new_body
        modified = True

    if modified:
        md_path.write_text(''.join(lines))

    return modified


# ---------------------------------------------------------------------------
# Watcher
# ---------------------------------------------------------------------------

class MarkdownHandler(FileSystemEventHandler):
    def __init__(self, root: Path) -> None:
        self.root = root
        # Tracks paths we just wrote ourselves so we can ignore the
        # inotify event that our own write triggers.
        self._own_writes: set[str] = set()

    def on_modified(self, event: FileSystemEvent) -> None:
        self._handle(event.src_path)

    def on_created(self, event: FileSystemEvent) -> None:
        self._handle(event.src_path)

    def _handle(self, src_path: str) -> None:
        p = Path(src_path)
        if not src_path.endswith('.md') or p.name.startswith('.#'):
            return
        if src_path in self._own_writes:
            self._own_writes.discard(src_path)
            return
        md_path = Path(src_path)
        print(f'Processing {md_path.relative_to(self.root)}')
        modified = process_md_file(md_path)
        if modified:
            self._own_writes.add(src_path)


def watch(root: Path) -> None:
    handler = MarkdownHandler(root)
    observer = Observer()
    blog_dir = root / 'blog'
    observer.schedule(handler, str(blog_dir), recursive=True)
    observer.start()
    print(f'Watching {blog_dir}  (Ctrl-C to stop)')
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.parse_args()   # only --help for now; exits on -h/--help
    root = Path(__file__).parent
    watch(root)
