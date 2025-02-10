---
date: 2010-10-22 12:49:00
title: "PhD Thesis about PyPy's CLI JIT Backend"
author: "Antonio Cuni"
---

_Originally published on the [PyPy blog](https://pypy.org/posts/2010/10/phd-thesis-about-pypys-cli-jit-backend-969267841095296323.html)._

<html><body><p>Hi all,</p>
<p>few months ago I finished the PhD studies and now my <a class="reference external" href="https://codespeak.net/~antocuni/Cuni_PhD_Thesis.pdf">thesis</a> is available,
just in case someone does not have anything better to do than read it :-).</p>
<p>The title of the thesis is <strong>High performance implementation of Python for
CLI/.NET with JIT compiler generation for dynamic languages</strong>, and its mainly
based on my work on the CLI backend for the PyPy JIT (note that the CLI JIT
backend is currently broken on trunk, but it's still working in the <a class="reference external" href="https://codespeak.net/svn/pypy/branch/cli-jit/">cli-jit
branch</a>).</p>
<p>The thesis might be useful also for people that are not directly interested in
the CLI JIT backend, as it also contains general information about the inner
workings of PyPy which are independent from the backend: in particular,
chapters 5 and 6 explain how the JIT frontend works.</p>
<dl class="docutils">
<dt>Here is the summary of chapters:</dt>
<dd><ol class="first last arabic simple">
<li>Introduction</li>
<li>The problem</li>
<li>Enter PyPy</li>
<li>Characterization of the target platform</li>
<li>Tracing JITs in a nutshell</li>
<li>The PyPy JIT compiler generator</li>
<li>The CLI JIT backend</li>
<li>Benchmarks</li>
<li>Conclusion and Future Work</li>
</ol>
</dd>
</dl>
<p>cheers,
Anto</p></body></html>