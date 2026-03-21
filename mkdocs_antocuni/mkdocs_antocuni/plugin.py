"""Custom Plugin for antocuni.eu."""

import hashlib
import logging
import re
import shutil
import warnings
from pathlib import Path, PurePosixPath

from ansi2html import Ansi2HTMLConverter
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


# Matches a fenced autorun block (``` or ~~~, any length >= 3).
AUTORUN_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,}|~{3,})autorun[ \t]*\n(?P<body>.*?)^(?P=fence)[ \t]*$',
    re.MULTILINE | re.DOTALL,
)

POPUP_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,}|~{3,})antocuni-popup[ \t]*\n(?P<body>.*?)^(?P=fence)[ \t]*$',
    re.MULTILINE | re.DOTALL,
)

_ANSI_CONV = Ansi2HTMLConverter(inline=True, scheme='dracula')

# ---------------------------------------------------------------------------
# Terminal HTML helpers
# ---------------------------------------------------------------------------

_OUTER_STYLE = (
    'background:#2E3436;'
    'border-radius:6px;'
    'padding:1em 1.2em;'
    'margin:1em 0;'
)
# Reset styles that .md-typeset pre and .md-typeset code would otherwise apply.
_PRE_STYLE = 'margin:0;color:var(--md-code-fg-color);direction:ltr;'
_CODE_STYLE = (
    'background:transparent;'
    'color:#d4d4d4;'
    'padding:0;'
    'border-radius:0;'
    'word-break:normal;'
    'white-space:pre;'
    'overflow-x:auto;'
    'display:block;'
)


def _ansi_to_html(text: str) -> str:
    """Convert ANSI-coloured text to HTML with inline styles."""
    return _ANSI_CONV.convert(text, full=False)


def _build_terminal_html(entries: list[tuple[str, str]]) -> str:
    """Build a terminal-like HTML block from (cmd, raw_output) pairs."""
    sections = [f'$ {cmd}\n{raw_output}' for cmd, raw_output in entries]
    combined = '\n'.join(sections)  # blank line between each cmd+output section
    # Use pre>code so that .md-typeset code { font-size:.85em } applies
    # naturally, giving the exact same size as regular fenced code blocks.
    return (
        f'<div style="{_OUTER_STYLE}">'
        f'<pre style="{_PRE_STYLE}">'
        f'<code style="{_CODE_STYLE}">{_ansi_to_html(combined)}</code>'
        f'</pre>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Popup HTML helpers
# ---------------------------------------------------------------------------

# Counter to generate unique IDs for multiple popups on the same page.
_popup_counter = 0

_POPUP_PLACEHOLDER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"'
    ' viewBox="0 0 400 200">'
    '<rect width="400" height="200" fill="#e0e0e0" rx="8"/>'
    '<text x="200" y="105" text-anchor="middle" fill="#888"'
    ' font-family="sans-serif" font-size="16">(image not available)</text>'
    '</svg>'
)


def _replace_popup_block(match: re.Match, page_src_dir: Path,
                         site_asset_prefix: str) -> str:
    """Replace one antocuni-popup fenced block with popup HTML.

    ``site_asset_prefix`` is the URL prefix (from site root) for assets that
    sit next to the source .md file, e.g. "/posts/2026/03-spy-semantics/".
    """
    global _popup_counter
    _popup_counter += 1
    popup_id = f'antocuni-popup-{_popup_counter}'

    body = match.group('body')
    img_path = ''
    url = ''
    for line in body.splitlines():
        line = line.strip()
        if line.startswith('img:'):
            img_path = line[len('img:'):].strip()
        elif line.startswith('url:'):
            url = line[len('url:'):].strip()

    # Build absolute site URLs for both the image and the iframe src
    img_site_url = site_asset_prefix + img_path
    iframe_url = site_asset_prefix + url

    # Check if the image file exists on disk
    img_abs = page_src_dir / img_path
    if img_path and img_abs.exists():
        img_tag = f'<img src="{img_site_url}" class="off-glb" style="max-width:100%;cursor:pointer;">'
    else:
        img_tag = _POPUP_PLACEHOLDER_SVG

    open_js = (
        f"var el=document.getElementById('{popup_id}');"
        f"el.style.display='flex';"
        f"document.body.style.overflow='hidden';"
    )
    close_js = (
        f"var el=document.getElementById('{popup_id}');"
        f"el.style.display='none';"
        f"document.body.style.overflow='';"
    )

    return (
        f'<div class="antocuni-popup-wrapper">'
        f'<div onclick="{open_js}"'
        f' style="cursor:pointer;text-align:center;">'
        f'{img_tag}'
        f'<div style="font-size:0.85em;color:#888;margin-top:4px;">'
        f'click to expand</div>'
        f'</div>'
        f'<div id="{popup_id}" style="display:none;position:fixed;inset:0;'
        f'background:rgba(0,0,0,0.8);z-index:9999;'
        f'align-items:center;justify-content:center;'
        f'overflow:hidden;touch-action:none;"'
        f' onclick="{close_js}">'
        f'<div style="position:relative;width:92vw;height:92vh;'
        f'max-height:calc(100dvh - 4vh);background:white;'
        f'border-radius:8px;overflow:hidden;"'
        f' onclick="event.stopPropagation()">'
        f'<button onclick="{close_js}"'
        f' style="position:absolute;top:8px;right:12px;z-index:10000;'
        f'font-size:1.5em;background:none;border:none;cursor:pointer;color:#333;">'
        f'&times;</button>'
        f'<iframe src="{iframe_url}" style="width:100%;height:100%;border:none;"></iframe>'
        f'</div>'
        f'</div>'
        f'</div>'
    )


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
        # Files referenced by antocuni-popup blocks that need to be copied
        # to the built site. List of (src_abs_path, site_relative_path).
        self._popup_assets = []

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
        """Replace custom fenced blocks with HTML."""
        page_src_dir = Path(page.file.abs_src_path).parent

        # autorun blocks
        autorun_dir = page_src_dir / 'autorun'
        if autorun_dir.is_dir():
            markdown = AUTORUN_BLOCK_RE.sub(
                lambda m: _replace_autorun_block(m, autorun_dir),
                markdown,
            )

        # antocuni-popup blocks
        # page.file.src_path is e.g. "posts/2026/03-spy-semantics/index.md"
        # Assets next to the .md are served from the parent directory in the
        # built site, so we build an absolute URL prefix like
        # "/posts/2026/03-spy-semantics/".
        src_rel_dir = str(PurePosixPath(page.file.src_path).parent)
        site_asset_prefix = '/' + src_rel_dir + '/'

        # Collect asset files referenced by popup blocks so we can copy them
        # in on_post_build.
        for m in POPUP_BLOCK_RE.finditer(markdown):
            for line in m.group('body').splitlines():
                line = line.strip()
                for prefix in ('img:', 'url:'):
                    if line.startswith(prefix):
                        rel = line[len(prefix):].strip()
                        abs_path = page_src_dir / rel
                        site_rel = src_rel_dir + '/' + rel
                        self._popup_assets.append((abs_path, site_rel))

        markdown = POPUP_BLOCK_RE.sub(
            lambda m: _replace_popup_block(m, page_src_dir, site_asset_prefix),
            markdown,
        )
        return markdown

    def on_post_build(self, config):
        """Copy popup asset files that mkdocs doesn't know about."""
        site_dir = Path(config['site_dir'])
        for src_abs, site_rel in self._popup_assets:
            if src_abs.exists():
                dest = site_dir / site_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_abs, dest)
