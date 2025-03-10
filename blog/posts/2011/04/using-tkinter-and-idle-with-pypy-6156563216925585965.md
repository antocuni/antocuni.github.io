---
date: 2011-04-20 11:22:00
title: "Using Tkinter and IDLE with PyPy"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2011/04/using-tkinter-and-idle-with-pypy-6156563216925585965.html).


<html><body><p>We are pleased to announce that Tkinter, the GUI library based on TCL/TK, now
works with PyPy.<br>
Tkinter is composed of two parts:<br>

</p>
<!-- more -->
<blockquote>
<ul class="simple">
<li><tt class="docutils literal">_tkinter</tt>, a module written in C which interfaces with the TCL world</li>
<li><tt class="docutils literal">Tkinter</tt>, a pure Python package which wraps <tt class="docutils literal">_tkinter</tt> to expose the
pythonic API we are used to</li>
</ul>
</blockquote>
<div class="separator" style="clear: both; text-align: center;">
</div>
<div class="separator" style="clear: both; text-align: center;">
<a href="https://4.bp.blogspot.com/-MnwNRQAgGvU/Ta6zPmuA7MI/AAAAAAAAAMs/k1_boT54q-I/s1600/idle.png" style="clear: right; float: right; margin-bottom: 1em; margin-left: 1em;"><img border="0" height="264" src="https://4.bp.blogspot.com/-MnwNRQAgGvU/Ta6zPmuA7MI/AAAAAAAAAMs/k1_boT54q-I/s320/idle.png" width="320"></a></div>
The <a class="reference external" href="https://bitbucket.org/pypy/tkinter">PyPy version of _tkinter</a> reuses the C code of as found in CPython and
compile it through the PyPy C-API compatibility layer, <tt class="docutils literal">cpyext</tt>.  To make it
work with PyPy, we had to modify it slightly, in order to remove the
dependency on some API functions which are not supported by PyPy.  In particular, we
removed the dependency on the <tt class="docutils literal">PyOS_InputHook</tt> variable, which allows a nice
integration of Tkinter and the Python interactive prompt: the result is that,
unlike CPython, in PyPy Tk windows created at the interactive prompt are not
shown until we manually call the <tt class="docutils literal">mainloop</tt> method.  Apart from this
inconvenience, all the rest works fine.<br>
At the moment, <tt class="docutils literal">_tkinter</tt> is not distributed with PyPy because our build
system does not support automatic compilation of C extension.  Instead, it is
necessary to install it manually, either directly from <a class="reference external" href="https://bitbucket.org/pypy/tkinter">source</a> or by
easy_installing/pip installing <a class="reference external" href="https://pypi.python.org/pypi/tkinter-pypy/">tkinter-pypy</a> from PyPI.<br>
For everything to work correctly, you need a recent build of PyPy: the
following is a step-by-step guide to install <tt class="docutils literal">_tkinter</tt> in a PyPy nightly
build for Linux 64 bit; for other architectures, look at the <a class="reference external" href="https://buildbot.pypy.org/nightly/trunk/">nightly build
page</a>:<br>
<pre class="literal-block">$ wget https://buildbot.pypy.org/nightly/trunk/pypy-c-jit-43485-1615dfd7d8f1-linux64.tar.bz2

$ tar xfv pypy-c-jit-43485-1615dfd7d8f1-linux64.tar.bz2

$ cd pypy-c-jit-43485-1615dfd7d8f1-linux64/

$ wget https://peak.telecommunity.com/dist/ez_setup.py

$ ./bin/pypy ez_setup.py    # install setuptools

$ ./bin/easy_install tkinter-pypy
</pre>
Once you complete the steps above, you can start using <tt class="docutils literal">Tkinter</tt> from your
python programs.  In particular, you can use IDLE, the IDE which is part of
the Python standard library.  To start IDLE, type:<br>
<pre class="literal-block">$ ./bin/pypy -m idlelib.idle
</pre>
Have fun :-)</body></html>