---
date: 2010-08-02 14:55:00
title: "Using virtualenv with PyPy"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2010/08/using-virtualenv-with-pypy-7238942727709530503.html).


<html><body><p>Thanks to the work that was recently done on the <a class="reference external" href="https://codespeak.net/pipermail/pypy-svn/2010-June/041686.html">sys-prefix</a> branch, it is
now possible to use <a class="reference external" href="https://pypi.python.org/pypi/virtualenv">virtualenv</a> with PyPy.
</p>
<!-- more -->

<p>To try it, you need:</p>
<blockquote>
<ul class="simple">
<li>a recent version of PyPy: PyPy 1.3 does not contain the necessary logic to
work with virtualenv, so you need a more recent PyPy from subversion
trunk. You can either <a class="reference external" href="https://codespeak.net/pypy/dist/pypy/doc/getting-started-python.html#translating-the-pypy-python-interpreter">build it by yourself</a> or download one of our
precompiled <a class="reference external" href="https://buildbot.pypy.org/nightly/trunk/">nightly builds</a></li>
<li>a copy of <a class="reference external" href="https://bitbucket.org/antocuni/virtualenv-pypy/">virtualenv-pypy</a>: this is a fork of virtualenv that contains
all the patches needed to work with PyPy, and hopefully will be <a class="reference external" href="https://bitbucket.org/ianb/virtualenv/issue/53/virtualenv-with-pypy">merged
back</a> at some point.  It should be totally compatible with the official
version of virtualenv, so it is safe to use it even to create non-PyPy
environments.  If you notice some weird behavior that does not happen with
the standard virtualenv, please let us know.</li>
</ul>
</blockquote>
<p>The directory layout has been redesigned in a way that it is possible to use
virtualenv to install a PyPy both from a precompiled tarball or from an svn
checkout:</p>
<pre class="literal-block">
# from a tarball
$ virtualenv -p /opt/pypy-c-jit-76426-linux/bin/pypy my-pypy-env

# from the svn checkout
$ virtualenv -p /path/to/pypy-trunk/pypy/translator/goal/pypy-c my-pypy-env
</pre>
<p>Once the environment has been created, you can enter it as usual. Note that
<tt class="docutils literal">bin/python</tt> is now a symlink to <tt class="docutils literal">bin/pypy</tt>.</p>
<p>Enjoy it :-)</p></body></html>