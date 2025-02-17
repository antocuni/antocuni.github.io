---
date: 2008-01-19 10:50:00
title: "Improve .NET Integration"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2008/01/improve-net-integration-2239651503641931440.html).


<html><body><p>A while ago Amit Regmi, a student from Canada, started working on the
<a class="reference" href="https://codespeak.net/viewvc/pypy/branch/clr-module-improvements/?pathrev=50773">clr module improvements</a> branch as a university project.
</p>
<!-- more -->

<p>During the sprint Carl Friedrich, Paul and me worked more on it and
brought it to a mergeable state.</p>
<p>It adds a lot of new features to the <a class="reference" href="https://codespeak.net/pypy/dist/pypy/doc/clr-module.html">clr module</a>, which is the
module that allows integration between <a class="reference" href="https://codespeak.net/pypy/dist/pypy/doc/getting-started.html#translating-using-the-cli-backend">pypy-cli</a> (aka PyPy.NET) and
the surrounding .NET environment:</p>
<blockquote>
<ul class="simple">
<li>full support to generic classes;</li>
<li>a new importer hook, allowing things like <tt class="docutils literal"><span class="pre">from</span> <span class="pre">System</span> <span class="pre">import</span>
<span class="pre">Math</span></tt> and so on;</li>
<li>.NET classes that implements <tt class="docutils literal"><span class="pre">IEnumerator</span></tt> are treated
as Python iterators; e.g. it's is possile to iterate over them
with a <tt class="docutils literal"><span class="pre">for</span></tt> loop.</li>
</ul>
</blockquote>
<p>This is an example of a pypy-cli session:</p>
<pre class="literal-block">
&gt;&gt;&gt;&gt; from System import Math
&gt;&gt;&gt;&gt; Math.Abs(-42)
42
&gt;&gt;&gt;&gt; from System.Collections.Generic import List
&gt;&gt;&gt;&gt; mylist = List[int]()
&gt;&gt;&gt;&gt; mylist.Add(42)
&gt;&gt;&gt;&gt; mylist.Add(43)
&gt;&gt;&gt;&gt; mylist.Add("foo")
Traceback (most recent call last):
  File "&lt;console&gt;", line 1, in &lt;interactive&gt;
TypeError: No overloads for Add could match
&gt;&gt;&gt;&gt; mylist[0]
42
&gt;&gt;&gt;&gt; for item in mylist: print item
42
43
</pre>
<p>This is still to be considered an alpha version; there are few known
bugs and probably a lot of unknown ones :-), so don't expect it to
work in every occasion. Still, it's a considerable step towards real
world :-).</p></body></html>