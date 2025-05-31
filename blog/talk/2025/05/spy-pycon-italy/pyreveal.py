import js
import pyodide
#from pyodide.ffi import to_js

TEMPLATE = """
<div class="reveal">
  <div class="slides">
    <section data-markdown>
      <textarea data-template>
        {content}
      </textarea>
    </section>
  </div>
</div>
"""

class PyReveal:
    #VERSION = '4.5.0'
    VERSION = '5.1.0'
    BASE = f'https://cdn.jsdelivr.net/npm/reveal.js@{VERSION}'  # CDN
    #BASE = f'/cdn/reveal.js'  # offline localhost

    def __init__(self, filename, post_init_cb=None):
        self.filename = filename
        self.post_init_cb = post_init_cb
        self.urls = []
        self.scripts_loaded = 0
        self.scripts_total = 0
        #
        # https://www.jsdelivr.com/package/npm/reveal.js?tab=files
        self.add('/dist/reveal.min.js')
        self.add('/dist/reset.min.css')
        self.add('/dist/reveal.min.css')
        self.add('/dist/theme/white.min.css') # XXX add the option to change it
        #
        # highlight plugin: XXX add the option to change the style
        self.add('/plugin/highlight/highlight.min.js')
        self.add('/plugin/highlight/zenburn.min.css')
        #
        # markdown plugin
        self.add('/plugin/markdown/markdown.min.js')
        self.add('/plugin/notes/notes.js')

    def add(self, path):
        assert path.startswith('/')
        self.urls.append(self.BASE + path)

    def render_head(self):
        for url in self.urls:
            if url.endswith('.css'):
                self.add_style(url)
            elif url.endswith('.js'):
                self.scripts_total += 1
                self.add_script(url)
            else:
                raise ValueError(f'unknown type: {path}')

        elem = js.document.createElement("script")
        #elem.text = "pyrender_onload();"
        elem.text = "console.log('onload end');"
        elem.onload = lambda ev: print('onload onload')
        js.document.head.appendChild(elem)

    def add_style(self, url):
        elem = js.document.createElement("link")
        elem.rel = "stylesheet"
        elem.href = url
        js.document.head.appendChild(elem)

    def add_script(self, url):
        elem = js.document.createElement("script")
        elem.src = url
        elem.onload = lambda ev: self.onload_maybe()
        js.document.head.appendChild(elem)

    def show(self):
        self.render_head()

    def onload_maybe(self):
        # this is a hack... this is called once for all <script> tags. When
        # the last <script> has been fully loaded, we proceed.
        self.scripts_loaded += 1
        if self.scripts_loaded != self.scripts_total:
            return

        with open(self.filename) as f:
            content = f.read()

        # hack hack hack to fix indentation problems in revealjs
        content = content.replace('    ', '\t')
        #content = 'hello'

        slides = TEMPLATE.format(content=content)
        js.document.body.insertAdjacentHTML("beforeend", slides)

        options = js.Object()
        options.plugins = list_to_js([
            js.RevealMarkdown,
            js.RevealHighlight,
            js.RevealNotes,
        ])
        options.hash = True  # so that every slide has its own URL

        js.Reveal.initialize(options)
        if self.post_init_cb:
            self.post_init_cb()

def list_to_js(lst):
    """
    It seems that pyodide.ffi.to_js doesn't work in micropython, this is a
    workaround
    """
    res = js.Array()
    for item in lst:
        res.push(item)
    return res

def show(filename, post_init_cb=None):
    pyr = PyReveal(filename, post_init_cb)
    pyr.show()
