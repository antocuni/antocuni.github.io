"""Custom Plugin for antocuni.eu."""

import hashlib
import logging
import re
import warnings
from pathlib import Path

from ansi2html import Ansi2HTMLConverter
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


# Matches a fenced autorun block (``` or ~~~, any length >= 3).
AUTORUN_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,}|~{3,})autorun[ \t]*\n(?P<body>.*?)^(?P=fence)[ \t]*$',
    re.MULTILINE | re.DOTALL,
)

_ANSI_CONV = Ansi2HTMLConverter(inline=True, scheme='dracula')

# ---------------------------------------------------------------------------
# Terminal HTML helpers
# ---------------------------------------------------------------------------

_TERMINAL_STYLE = (
    'background:#2E3436;'
    'border-radius:6px;'
    'padding:1em 1.2em;'
    'font-family:"Fira Mono","Cascadia Code","Consolas",monospace;'
    'font-size:.88em;'
    'line-height:1.5;'
    'margin:1em 0;'
    'overflow-x:auto;'
)
_PRE_STYLE = 'margin:0;background:transparent;color:#d4d4d4;white-space:pre;'


def _ansi_to_html(text: str) -> str:
    """Convert ANSI-coloured text to HTML with inline styles."""
    return _ANSI_CONV.convert(text, full=False)


def _build_terminal_html(entries: list[tuple[str, str]]) -> str:
    """Build a terminal-like HTML block from (cmd, raw_output) pairs."""
    parts = [f'<div style="{_TERMINAL_STYLE}">']
    for cmd, raw_output in entries:
        combined = f'$ {cmd}\n{raw_output}'
        parts.append(f'<pre style="{_PRE_STYLE}">{_ansi_to_html(combined)}</pre>')
    parts.append('</div>')
    return '\n'.join(parts)


def _replace_autorun_block(match: re.Match, autorun_dir: Path) -> str:
    """Replace one autorun fenced block with terminal HTML."""
    body = match.group('body')
    entries: list[tuple[str, str]] = []

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith('$ '):
            continue
        cmd = stripped[2:]
        raw_path = autorun_dir / hashlib.md5(cmd.encode()).hexdigest()
        if raw_path.exists():
            raw_output = raw_path.read_text()
        else:
            # Fall back to whatever stripped text is in the block.
            raw_output = '(output not available — run autorun.py first)\n'
        entries.append((cmd, raw_output))

    if not entries:
        return match.group(0)  # nothing to do, leave block as-is

    return _build_terminal_html(entries)


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------

class MyPlugin(BasePlugin):

    config_scheme = (
        ('silent', config_options.Type(bool, default=True)),
    )

    def on_startup(self, command, dirty):
        """Suppress redirects warnings."""

        print('hello from mkdocs_antocuni')

        # Create a custom filter to suppress redirects warnings
        class RedirectsFilter(logging.Filter):
            def filter(self, record):
                return not (record.levelno == logging.WARNING and
                           'redirects plugin:' in record.getMessage())

        # Add the filter to all existing loggers and the root logger
        for name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(name)
            logger.addFilter(RedirectsFilter())

        # Also add to root logger
        logging.getLogger().addFilter(RedirectsFilter())

    def on_page_markdown(self, markdown, page, config, files):
        """Replace autorun fenced blocks with terminal HTML."""
        autorun_dir = Path(page.file.abs_src_path).parent / 'autorun'
        if not autorun_dir.is_dir():
            return markdown

        return AUTORUN_BLOCK_RE.sub(
            lambda m: _replace_autorun_block(m, autorun_dir),
            markdown,
        )
