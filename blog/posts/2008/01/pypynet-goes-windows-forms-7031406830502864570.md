---
date: 2008-01-19 22:23:00
title: "PyPy.NET goes Windows Forms"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2008/01/pypynet-goes-windows-forms-7031406830502864570.html).


<html><body><a href="https://4.bp.blogspot.com/_4gR6Ggu8oHQ/R5J41OiHR7I/AAAAAAAAACo/u8jr08QiCmo/s1600-h/winform.png"><img alt="" border="0" id="BLOGGER_PHOTO_ID_5157317379122218930" src="https://4.bp.blogspot.com/_4gR6Ggu8oHQ/R5J41OiHR7I/AAAAAAAAACo/u8jr08QiCmo/s320/winform.png" style="float: right; margin: 0 0 10px 10px; cursor: pointer; cursor: hand;"></a>
<p>After having spent the last few days on understanding PyPy's JIT,
today I went back hacking the <cite>clr module</cite>.  As a result, it is now
possible to import and use external assemblies from <a class="reference" href="https://codespeak.net/pypy/dist/pypy/doc/getting-started.html#translating-using-the-cli-backend">pypy-cli</a>,
including <a class="reference" href="https://en.wikipedia.org/wiki/Windows_Forms">Windows Forms</a>
</p>
<!-- more -->

<p>Here is a screenshot of the result you get by typing the following at
the <a class="reference" href="https://codespeak.net/pypy/dist/pypy/doc/getting-started.html#translating-using-the-cli-backend">pypy-cli</a> interactive prompt:</p>
<pre class="literal-block">
&gt;&gt;&gt;&gt; import clr
&gt;&gt;&gt;&gt; clr.AddReferenceByPartialName("System.Windows.Forms")
&gt;&gt;&gt;&gt; clr.AddReferenceByPartialName("System.Drawing")
&gt;&gt;&gt;&gt; from System.Windows.Forms import Application, Form, Label
&gt;&gt;&gt;&gt; from System.Drawing import Point
&gt;&gt;&gt;&gt;
&gt;&gt;&gt;&gt; frm = Form()
&gt;&gt;&gt;&gt; frm.Text = "The first pypy-cli Windows Forms app ever"
&gt;&gt;&gt;&gt; lbl = Label()
&gt;&gt;&gt;&gt; lbl.Text = "Hello World!"
&gt;&gt;&gt;&gt; lbl.AutoSize = True
&gt;&gt;&gt;&gt; lbl.Location = Point(100, 100)
&gt;&gt;&gt;&gt; frm.Controls.Add(lbl)
&gt;&gt;&gt;&gt; Application.Run(frm)
</pre>
<p>Unfortunately at the moment you can't do much more than this, because
we still miss support for delegates and so it's not possibile to
handle events. Still, it's a step in the right direction :-).</p></body></html>