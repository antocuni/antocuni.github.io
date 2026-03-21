#!/usr/bin/env -S uv run
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
import hashlib
import os
import pty
import re
import select
import subprocess
import time
from pathlib import Path

ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*m')


def run_in_pty(cmd: str, cwd, env) -> tuple[str, int]:
    """Run *cmd* inside a pseudo-TTY so programs emit ANSI colour codes."""
    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen(
        cmd, shell=True, cwd=cwd, env=env,
        stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
    )
    os.close(slave_fd)
    chunks: list[bytes] = []
    while True:
        try:
            r, _, _ = select.select([master_fd], [], [], 0.05)
        except (ValueError, OSError):
            break
        if r:
            try:
                chunks.append(os.read(master_fd, 4096))
            except OSError:
                break
        elif proc.poll() is not None:
            # Drain any remaining output
            try:
                while True:
                    chunks.append(os.read(master_fd, 4096))
            except OSError:
                pass
            break
    proc.wait()
    os.close(master_fd)
    raw = b''.join(chunks).decode('utf-8', errors='replace')
    raw = raw.replace('\r\n', '\n').replace('\r', '\n')
    return raw, proc.returncode

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Extra directories prepended to PATH when running autorun commands.
EXTRA_PATH = [
    '/home/antocuni/anaconda/spy/venv/bin',
]

_ENV = {
    **os.environ,
    'PATH': ':'.join(EXTRA_PATH) + ':' + os.environ.get('PATH', ''),
    'PAGER': 'cat',
    'GIT_PAGER': 'cat',
}



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


def process_md_file(md_path: Path, force: bool = False) -> bool:
    """Scan *md_path* and apply both transformations.

    Returns True if the file was modified (autorun output inserted).
    If *force* is True, existing output is discarded and all commands are
    re-run (used by --regen).
    """
    content = md_path.read_text()
    lines = content.splitlines(keepends=True)

    autorun_dir = md_path.parent / 'autorun'

    # --- pass 1: extract filename blocks (read-only w.r.t. the .md file) ---
    for _start, _end, _info, body_lines in parse_blocks(lines):
        if not body_lines:
            continue
        m = FILENAME_RE.match(body_lines[0])
        if not m:
            continue
        filename = m.group(1)
        autorun_dir.mkdir(exist_ok=True)
        out_path = autorun_dir / filename
        file_content = ''.join(body_lines[1:])
        if not out_path.exists() or out_path.read_text() != file_content:
            out_path.write_text(file_content)
            print(f'  wrote {out_path}')

    # --- pass 2: autorun blocks (may modify the .md file) ---
    # Iterate in reverse so that inserting lines doesn't shift earlier indices.
    blocks = list(parse_blocks(lines))
    modified = False

    for start, end, info, body_lines in reversed(blocks):
        if info not in ('autorun', 'autorun x'):
            continue
        if not body_lines:
            continue

        block_force = force or (info == 'autorun x')

        # "No output yet" means every non-empty line starts with '$ '.
        has_output = any(
            l.strip() and not l.strip().startswith('$ ')
            for l in body_lines
        )
        if has_output and not block_force:
            continue

        # When forcing a regen, strip existing output: keep only '$ cmd' lines.
        if has_output and block_force:
            body_lines = [l for l in body_lines if l.strip().startswith('$ ')]

        # Must contain at least one command line.
        cmd_lines = [l for l in body_lines if l.strip().startswith('$ ')]
        if not cmd_lines:
            continue

        autorun_dir.mkdir(exist_ok=True)
        cwd = autorun_dir

        # Rebuild the body: after each '$ cmd' line insert its output.
        new_body: list[str] = []
        for line in body_lines:
            stripped = line.rstrip('\n').rstrip('\r')
            if stripped.startswith('$ ') and new_body:
                new_body.append('\n')
            new_body.append(line)
            if not stripped.startswith('$ '):
                continue
            cmd = stripped[2:]
            print(f'  running ({cwd.name}/): {cmd}')
            try:
                raw_output, returncode = run_in_pty(cmd, cwd=cwd, env=_ENV)
            except Exception as exc:
                raw_output = f'ERROR: {exc}\n'
            # Strip the local absolute path prefix so it doesn't leak into
            # the rendered output (e.g. in error tracebacks).
            raw_output = raw_output.replace(str(md_path.parent) + '/', '/.../')
            # Save raw output (with ANSI codes) for the mkdocs plugin.
            raw_path = autorun_dir / hashlib.md5(cmd.encode()).hexdigest()
            raw_path.write_text(raw_output)
            output = ANSI_ESCAPE_RE.sub('', raw_output)
            output_lines = output.splitlines(keepends=True)
            if output_lines and not output_lines[-1].endswith('\n'):
                output_lines[-1] += '\n'
            new_body.extend(output_lines)

        # Replace the block body in-place (start+1 .. end are the body lines).
        lines[start + 1:end] = new_body
        if info == 'autorun x':
            lines[start] = lines[start].replace('autorun x', 'autorun', 1)
        modified = True

    if modified:
        md_path.write_text(''.join(lines))

    return modified


# ---------------------------------------------------------------------------
# Theme preview
# ---------------------------------------------------------------------------

def show_themes(md_path: Path) -> None:
    """Render all autorun blocks from *md_path* in every ansi2html theme and
    write an interactive HTML file next to the .md file."""
    from ansi2html import Ansi2HTMLConverter
    from ansi2html.style import SCHEME

    content = md_path.read_text()
    lines = content.splitlines(keepends=True)
    autorun_dir = md_path.parent / 'autorun'

    # Collect (cmd, raw_output) pairs per block.
    blocks_data: list[list[tuple[str, str]]] = []
    for _start, _end, info, body_lines in parse_blocks(lines):
        if info != 'autorun':
            continue
        entries: list[tuple[str, str]] = []
        for line in body_lines:
            stripped = line.strip()
            if not stripped.startswith('$ '):
                continue
            cmd = stripped[2:]
            raw_path = autorun_dir / hashlib.md5(cmd.encode()).hexdigest()
            raw_output = raw_path.read_text() if raw_path.exists() else \
                '(output not available — run autorun.py first)\n'
            entries.append((cmd, raw_output))
        if entries:
            blocks_data.append(entries)

    if not blocks_data:
        print('No autorun blocks with cached output found.')
        return

    themes = list(SCHEME.keys())
    default_theme = 'xterm' if 'xterm' in themes else themes[0]

    _TERM_BASE = (
        'border-radius:6px;padding:1em 1.2em;'
        'font-family:"Fira Mono","Cascadia Code","Consolas",monospace;'
        'font-size:.88em;line-height:1.5;margin:1em 0;overflow-x:auto;'
    )
    _PRE = 'margin:0;background:transparent;color:#d4d4d4;white-space:pre;'

    theme_divs: list[str] = []
    for theme in themes:
        bg = SCHEME[theme][0]
        conv = Ansi2HTMLConverter(inline=True, scheme=theme)
        block_htmls: list[str] = []
        for entries in blocks_data:
            parts: list[str] = []
            for cmd, raw_output in entries:
                combined = f'$ {cmd}\n{raw_output}'
                out_html = conv.convert(combined, full=False)
                parts.append(
                    f'<pre style="{_PRE}">{out_html}</pre>'
                )
            block_htmls.append(
                f'<div style="background:{bg};{_TERM_BASE}">'
                + '\n'.join(parts) + '</div>'
            )
        display = 'block' if theme == default_theme else 'none'
        theme_divs.append(
            f'<div id="theme-{theme}" class="theme-section" '
            f'style="display:{display}">\n'
            + '\n'.join(block_htmls)
            + '\n</div>'
        )

    options = '\n'.join(
        f'<option value="{t}"{"selected" if t == default_theme else ""}>{t}</option>'
        for t in themes
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>autorun theme preview — {md_path.name}</title>
  <style>
    body {{ font-family: sans-serif; padding: 2em; background: #f0f0f0; }}
    label {{ font-size: 1.1em; }}
    select {{ font-size: 1em; padding: .2em .6em; margin-left: .4em; }}
    code {{ font-size: .9em; }}
  </style>
</head>
<body>
  <h1>autorun theme preview</h1>
  <p>File: <code>{md_path}</code></p>
  <label>Theme:
    <select id="theme-select" onchange="switchTheme()">
{options}
    </select>
  </label>
  {''.join(theme_divs)}
  <script>
    var current = '{default_theme}';
    function switchTheme() {{
      document.getElementById('theme-' + current).style.display = 'none';
      current = document.getElementById('theme-select').value;
      document.getElementById('theme-' + current).style.display = 'block';
    }}
  </script>
</body>
</html>
"""
    output_path = md_path.parent / 'autorun-themes.html'
    output_path.write_text(html)
    print(f'Written: {output_path}')


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
        time.sleep(0.5)  # let Emacs re-register its inotify watch after saving
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
    parser.add_argument(
        '--regen',
        metavar='FILENAME',
        help='Force re-run of all autorun blocks in the given .md file, '
             'discarding any previously inserted output.',
    )
    parser.add_argument(
        '--show-themes',
        metavar='FILENAME',
        help='Render all autorun blocks from the given .md file in every '
             'available ansi2html theme and write an interactive HTML preview '
             'to autorun-themes.html next to the file.',
    )
    args = parser.parse_args()
    root = Path(__file__).parent

    if args.regen:
        md_path = Path(args.regen).resolve()
        print(f'Regenerating {md_path.relative_to(root)}')
        process_md_file(md_path, force=True)
    elif args.show_themes:
        md_path = Path(args.show_themes).resolve()
        show_themes(md_path)
    else:
        watch(root)
