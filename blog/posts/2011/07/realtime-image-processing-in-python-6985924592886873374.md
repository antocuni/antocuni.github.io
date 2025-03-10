---
date: 2011-07-07 16:24:00
title: "Realtime image processing in Python"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2011/07/realtime-image-processing-in-python-6985924592886873374.html).


<html><body><p>Image processing is notoriously a CPU intensive task.  To do it in realtime,
you need to implement your algorithm in a fast language, hence trying to do it
in Python is foolish: Python is clearly not fast enough for this task. Is it?
:-)<br>
Actually, it turns out that the PyPy JIT compiler produces code which is fast
enough to do realtime video processing using two simple algorithms implemented
by Håkan Ardö.<br>
<tt class="docutils literal">sobel.py</tt> implements a classical way of locating edges in images, the
<a class="reference external" href="https://en.wikipedia.org/wiki/Sobel_operator">Sobel operator</a>. It is an approximation of the magnitude of the <a class="reference external" href="https://en.wikipedia.org/wiki/Image_gradient">image
gradient</a>. The processing time is spend on two <a class="reference external" href="https://en.wikipedia.org/wiki/Convolution">convolutions</a> between the
image and 3x3-kernels.<br>
<tt class="docutils literal">magnify.py</tt> implements a pixel coordinate transformation that rearranges
the pixels in the image to form a magnifying effect in the center.
It consists of a single loop over the pixels in the output image copying
pixels from the input image.<br>
You can try by yourself by downloading the appropriate demo:<br>

</p>
<!-- more -->
<blockquote>
<ul class="simple">
<li><a class="reference external" href="https://wyvern.cs.uni-duesseldorf.de/%7Eantocuni/pypy-image-demo.tar.bz2">pypy-image-demo.tar.bz2</a>: this archive contains only the source code,
use this is you have PyPy already installed</li>
<li><a class="reference external" href="https://wyvern.cs.uni-duesseldorf.de/%7Eantocuni/pypy-image-demo-full.tar.bz2">pypy-image-demo-full.tar.bz2</a>: this archive contains both the source
code and prebuilt PyPy binaries for linux 32 and 64 bits</li>
</ul>
</blockquote>
To run the demo, you need to have <tt class="docutils literal">mplayer</tt> installed on your system.  The
demo has been tested only on linux, it might (or not) work also on other
systems:<br>
<pre class="literal-block">$ pypy pypy-image-demo/sobel.py

$ pypy pypy-image-demo/magnify.py
</pre>
By default, the two demos uses an example AVI file.  To have more fun, you can
use your webcam by passing the appropriate mplayer parameters to the scripts,
e.g:<br>
<pre class="literal-block">$ pypy demo/sobel.py tv://
</pre>
By default magnify.py uses <a class="reference external" href="https://en.wikipedia.org/wiki/Nearest-neighbor_interpolation">nearest-neighbor interpolation</a>.  By adding the
option -b, <a class="reference external" href="https://en.wikipedia.org/wiki/Bilinear_interpolation">bilinear interpolation</a> will be used instead, which gives
smoother result:<br>
<pre class="literal-block">$ pypy demo/magnify.py -b
</pre>
There is only a single implementation of the algorithm in
<tt class="docutils literal">magnify.py</tt>. The two different interpolation methods are implemented by
subclassing the class used to represent images and embed the
interpolation within the pixel access method. PyPy is able to achieve good
performance with this kind of abstractions because it can inline
the pixel access method and specialize the implementation of the algorithm.
In C++ that kind of pixel access method would be virtual and you'll need to use
templates to get the same effect without incurring in runtime overhead.<br>
<div class="separator" style="clear: both; text-align: center;">




</div>
The <a class="reference external" href="https://www.youtube.com/watch?v=5DtlBC_Zbq4">video</a> above shows PyPy and CPython running <tt class="docutils literal">sobel.py</tt> side by
side (PyPy taking input from the webcam, CPython from the test
file). Alternatively, to have a feeling on how much PyPy is faster than
CPython, try to run the demo with the latter.  These are the the average fps
(frames per second) that I get on my machine (Ubuntu 64 bit, Intel i7 920, 4GB
RAM) when processing the default <tt class="docutils literal">test.avi</tt> video and using the prebuilt
PyPy binary found in the <a class="reference external" href="https://wyvern.cs.uni-duesseldorf.de/%7Eantocuni/pypy-image-demo-full.tar.bz2">full</a> tarball alinked above.  For <tt class="docutils literal">sobel.py</tt>:<br>
<blockquote>
<ul class="simple">
<li>PyPy: ~47.23 fps</li>
<li>CPython: ~0.08 fps</li>
</ul>
</blockquote>
For <tt class="docutils literal">magnify.py</tt>:<br>
<blockquote>
<ul class="simple">
<li>PyPy: ~26.92 fps</li>
<li>CPython: ~1.78 fps</li>
</ul>
</blockquote>
This means that on <tt class="docutils literal">sobel.py</tt>, PyPy is <b>590 times faster</b>.  On
<tt class="docutils literal">magnify.py</tt> the difference is much less evident and the speedup is "only"
15x.<br>
It must be noted that this is an extreme example of what PyPy can do.  In
particular, you cannot expect (yet :-)) PyPy to be fast enough to run an
arbitrary video processing algorithm in real time, but the demo still proves
that PyPy has the potential to get there.</body></html>