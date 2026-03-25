"""Custom Plugin for antocuni.eu."""

import hashlib
import logging
import re
import shutil
import subprocess
import warnings
from pathlib import Path, PurePosixPath

from ansi2html import Ansi2HTMLConverter
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


# Matches a fenced autorun block (``` or ~~~, any length >= 3).
AUTORUN_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,}|~{3,})autorun(?P<opts>[^\n]*)\n(?P<body>.*?)^(?P=fence)[ \t]*$',
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


def _parse_autorun_opts(opts_str: str):
    """Parse output-range and lineno from the autorun info string."""
    tokens = opts_str.split()
    output_range = None
    lineno = False
    for tok in tokens:
        if tok.startswith('output-range='):
            parts = tok[len('output-range='):].split('-')
            start = int(parts[0])
            end = int(parts[1]) if parts[1] else None
            output_range = (start, end)
        elif tok == 'lineno':
            lineno = True
    return output_range, lineno


def _apply_output_opts(text: str, output_range, lineno: bool) -> str:
    """Apply output-range and lineno filtering to output text."""
    if not output_range and not lineno:
        return text

    lines = text.splitlines(keepends=True)
    total = len(lines)

    if output_range:
        start, end = output_range
        if end is None:
            end = total
        else:
            end = min(end, total)
        selected = lines[start - 1:end]
        max_lineno = end
    else:
        start = 1
        end = total
        selected = lines
        max_lineno = total

    result = []
    if output_range and start > 1:
        result.append('[...]\n')

    if lineno:
        width = len(str(max_lineno))
        for i, line in enumerate(selected, start=start):
            if line.endswith('\n'):
                result.append(f'{i:{width}d} | {line}')
            else:
                result.append(f'{i:{width}d} | {line}\n')
    else:
        result.extend(selected)

    if output_range and end < total:
        result.append('[...]\n')

    return ''.join(result)


def _replace_autorun_block(match: re.Match, autorun_dir: Path) -> str:
    """Replace one autorun fenced block with terminal HTML."""
    body = match.group('body')
    output_range, lineno = _parse_autorun_opts(match.group('opts'))
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
        raw_output = _apply_output_opts(raw_output, output_range, lineno)
        entries.append((cmd, raw_output))

    if not entries:
        return match.group(0)  # nothing to do, leave block as-is

    return _build_terminal_html(entries)


# ---------------------------------------------------------------------------
# SPy playground helpers
# ---------------------------------------------------------------------------

_PLAYGROUND_BASE_URL_DEFAULT = 'https://spylang.github.io/spy/'
_CREATE_SNIPPET_PY = Path(
    '/home/antocuni/anaconda/spy/playground/create_snippet.py'
)

_TITLE_IN_INFO_RE = re.compile(r'\btitle=(?:"([^"]+)"|\'([^\']+)\'|(\S+))')

# Matches python blocks that carry the autowrite attribute.
_PLAYGROUND_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,}|~{3,})python\s+(?P<attrs>[^\n]*\bautowrite\b[^\n]*)\n'
    r'(?P<body>.*?)'
    r'^(?P=fence)[ \t]*$',
    re.MULTILINE | re.DOTALL,
)


def _playground_url(spy_file: Path, base_url: str) -> str:
    result = subprocess.run(
        ['python', str(_CREATE_SNIPPET_PY), str(spy_file),
         '--url', base_url],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _process_playground_blocks(markdown, autorun_dir, redirect_list, base_url):
    """Replace python+autowrite blocks with code block + Try yourself link."""
    def replace(match):
        fence = match.group('fence')
        attrs = match.group('attrs')
        body = match.group('body')

        tm = _TITLE_IN_INFO_RE.search(attrs)
        if not tm:
            return match.group(0)
        filename = tm.group(1) or tm.group(2) or tm.group(3)

        clean_attrs = re.sub(r'\s*\bautowrite\b', '', attrs).strip()
        new_fence = f'{fence}python {clean_attrs}' if clean_attrs else f'{fence}python'

        spy_file = autorun_dir / filename
        if spy_file.exists():
            try:
                pg_url = _playground_url(spy_file, base_url)
            except subprocess.CalledProcessError:
                pg_url = None
        else:
            pg_url = None

        if pg_url:
            redirect_list.append((filename, pg_url))
            link = (
                f'\n<p style="text-align:right;margin-top:-0.8em;font-size:0.85em;">'
                f'<a href="go/{filename}/" target="_blank">▶ Try it yourself</a>'
                f'</p>\n'
            )
        else:
            link = ''

        return f'{new_fence}\n{body}{fence}\n{link}'

    return _PLAYGROUND_BLOCK_RE.sub(replace, markdown)


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------

class MyPlugin(BasePlugin):

    config_scheme = (
        ('silent', config_options.Type(bool, default=True)),
    )

    def on_env(self, env, config, files):
        """Store the files collection for asset URL resolution."""
        self._files = files

    def on_startup(self, command, dirty):
        """Suppress redirects warnings."""
        # Files referenced by antocuni-popup blocks that need to be copied
        # to the built site. List of (src_abs_path, site_relative_path).
        self._popup_assets = []
        self._files = None

        # Playground redirects: list of (page_dest_dir, filename, playground_url).
        self._playground_redirects = []

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

        # spy blocks: highlight as Python
        markdown = re.sub(r'^(`{3,}|~{3,})spy\b', r'\1python', markdown,
                          flags=re.MULTILINE)

        # For pages with playground_links: inject "Try yourself" links and
        # record redirects, then strip autowrite.  For all other pages: just strip.
        antocuni_meta = page.meta.get('antocuni', {})
        if antocuni_meta.get('playground_links'):
            page_dest_dir = str(PurePosixPath(page.file.dest_uri).parent)
            base_url = antocuni_meta.get('playground_base_url',
                                         _PLAYGROUND_BASE_URL_DEFAULT)
            redirect_list: list[tuple[str, str]] = []
            markdown = _process_playground_blocks(
                markdown, page_src_dir / 'autorun', redirect_list, base_url,
            )
            for filename, pg_url in redirect_list:
                self._playground_redirects.append((page_dest_dir, filename, pg_url))

        # Strip any remaining 'autowrite' attributes (pages other than the
        # playground post, or blocks where the spy file was missing).
        markdown = re.sub(
            r'^((?:`{3,}|~{3,})[^\n]*?)\s*\bautowrite\b[^\S\n]*',
            r'\1',
            markdown,
            flags=re.MULTILINE,
        )

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

    def on_post_page(self, output, page, config):
        """Inject og: meta tags into the page <head>."""
        og_meta = dict(page.meta.get('og') or {})
        og_meta.setdefault('title', page.title)
        if not og_meta:
            return output
        def _meta_tag(key, value):
            if key == 'author':
                return f'<meta name="author" content="{value}">'
            return f'<meta property="og:{key}" content="{value}">'

        image = og_meta.get('image')
        if image and not image.startswith(('http://', 'https://')):
            abs_image = Path(page.file.abs_src_path).parent / image
            if not abs_image.exists():
                raise FileNotFoundError(
                    f'og.image not found: {abs_image} (in {page.file.src_path})'
                )
            img_src_path = str(PurePosixPath(page.file.src_path).parent / image)
            img_file = self._files.get_file_from_path(img_src_path)
            if img_file is None:
                raise FileNotFoundError(
                    f'og.image not found in mkdocs files: {img_src_path}'
                )
            site_url = config.get('site_url', '').rstrip('/')
            dest_uri = img_file.dest_uri.removeprefix('./')
            og_meta['image'] = f'{site_url}/{dest_uri}'

        og_tags = '\n'.join(_meta_tag(k, v) for k, v in og_meta.items())

        twitter_map = {'title': 'title', 'description': 'description', 'image': 'image'}
        twitter_card = 'summary_large_image' if og_meta.get('image') else 'summary'
        twitter_tags = f'<meta name="twitter:card" content="{twitter_card}">\n'
        twitter_tags += '\n'.join(
            f'<meta name="twitter:{tw_key}" content="{og_meta[og_key]}">'
            for og_key, tw_key in twitter_map.items()
            if og_key in og_meta
        )

        return output.replace('</head>', f'{og_tags}\n{twitter_tags}\n</head>', 1)

    def on_post_build(self, config):
        """Copy popup assets and write playground redirect pages."""
        site_dir = Path(config['site_dir'])
        for src_abs, site_rel in self._popup_assets:
            if src_abs.exists():
                dest = site_dir / site_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_abs, dest)

        for page_dest_dir, filename, pg_url in self._playground_redirects:
            redirect_html = (
                '<!DOCTYPE html>\n'
                '<html>\n'
                '<head>\n'
                f'<meta http-equiv="refresh" content="0; url={pg_url}">\n'
                f'<link rel="canonical" href="{pg_url}">\n'
                '</head>\n'
                '<body></body>\n'
                '</html>\n'
            )
            dest = site_dir / page_dest_dir / 'go' / filename / 'index.html'
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(redirect_html)
        self._playground_redirects.clear()
