---
date: 2008-04-01 11:19:00
title: "Trying to get PyPy to run on Python 3.0"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2008/04/trying-to-get-pypy-to-run-on-python-30-5082015544752137606.html).


<html><body><p>As you surely know, Python 3.0 is coming; recently, they released
Python 3.0 alpha 3, and the final version is expected around
September.
</p>
<!-- more -->

<p>As suggested by the migration guide (in the PEP 3000), we started by applying
2to3 to our standard interpreter, which is written in RPython (though
we should call it RPython 2.4 now, as opposed to RPython 3.0 -- see
below).</p>
<p>Converting was not seamless, but most of the resulting bugs were due to the
new dict views, str/unicode changes and the missing "reduce" built-in.
After forking and refactoring both our interpreter and the 2to3 script,
the Python interpreter runs on Python 3.0 alpha 3!</p>
<p>Next step was to run 2to3 over the whole translation toolchain,
i.e. the part of PyPy which takes care of analyzing the interpreter in
order to produce efficient executables; after the good results we got
with the standard interpreter, we were confident that it would have
been relatively easy to run 2to3 over it: unfortunately, it was not
:-(.</p>
<p>After letting 2to3 run for days and days uninterrupted, we decided to
kill it: we assume that the toolchain is simply too complex to be
converted in a reasonable amount of time.</p>
<p>So, we needed to think something else; THE great idea we had was to
turn everything upside-down: if we can't port PyPy to Py3k, we can
always port Py3k to PyPy!</p>
<p>Under the hood, the 2to3 conversion tool operates as a graph
transformer: it takes the graph of your program (in the form of Python
2.x source file) and returns a transformed graph of the same program
(in the form of Python 3.0 source file).  Since the entire translation
toolchain of PyPy is based on graph transformations, we could reuse it
to modify the behaviour of the 2to3 tool.  We wrote a general
graph-inverter algorithm which, as the name suggests, takes a graph
transformation and build the inverse transformation; then, we applied
the graph inverter to 2to3, getting something that we called 3to2: it
is important to underline that <strong>3to2 was built by automatically
analysing 2to3 and reversing its operation with only the help of a few
manual hints</strong>. For this reason and because we are not keeping generated
files under version control, we do not need to maintain this new tool in
the Subversion repository.</p>
<p>Once we built 3to2, it was relatively easy to pipe its result to our
interpreter, getting something that can run Python 3.0 programs.</p>
<p>Performance-wise, this approach has the problem of being slower at
import time, because it needs to run (automatically) 3to2 every time
the source is modified; in the future, we plan to apply our JIT
techniques also to this part of the interpreter, trying to mitigate the
slowdown until it is not noticeable anymore to the final user.</p>
<p>In the next weeks, we will work on the transformation (and probably publish
the technique as a research paper, with a title like "Automatic Program
Reversion on Intermediate Languages").</p>
<p><strong>UPDATE:</strong> In case anybody didn't guess or didn't spot the acronym: The above
was an April Fool's joke. Nearly nothing of it is true.</p></body></html>