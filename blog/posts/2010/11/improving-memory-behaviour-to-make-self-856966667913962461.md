---
date: 2010-11-26 12:51:00
title: "Improving Memory Behaviour to Make Self-Hosted PyPy Translations Practical"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2010/11/improving-memory-behaviour-to-make-self-856966667913962461.html).


<html><body><p>In our <a class="reference external" href="/posts/2010/11/snake-which-bites-its-tail-pypy-jitting-5161284681004717142.html">previous blog post</a>, we talked about how fast PyPy can translate
itself compared to CPython.  However, the price to pay for the 2x speedup was
an huge amount of memory: actually, it was so huge that a standard <tt class="docutils literal"><span class="pre">-Ojit</span></tt>
compilation could not be completed on 32-bit because it required more than the
4 GB of RAM that are addressable on that platform.  On 64-bit, it consumed
8.3 GB of RAM instead of the 2.3 GB needed by CPython.
</p>
<!-- more -->

<p>This behavior was mainly caused by the JIT, because at the time we wrote the
blog post the generated assembler was kept alive forever, together with some
big data structure needed to execute it.</p>
<p>In the past two weeks Anto and Armin attacked the issue in the <tt class="docutils literal"><span class="pre">jit-free</span></tt>
branch, which has been recently <a class="reference external" href="https://codespeak.net/pipermail/pypy-svn/2010-November/045019.html">merged</a> to trunk.  The branch solves several
issues. The main idea of the branch is that if a
loop has not been executed for a certain amount of time (controlled by the new
<tt class="docutils literal">loop_longevity</tt> JIT parameter) we consider it "old" and no longer needed,
thus we deallocate it.</p>
<p>(In the process of doing this, we also discovered and fixed an
oversight in the implementation of generators, which led to generators being
freed only very slowly.)</p>
<p>To understand the freeing of loops some more, let's look at how many loops are
actually created during a translation.
The purple line in the following graph shows how many loops (and bridges) are
alive at any point in time with an infinite longevity, which is equivalent to
the situation we had before the <tt class="docutils literal"><span class="pre">jit-free</span></tt> branch.  By contrast, the blue
line shows the number of loops that you get in the current trunk: the
difference is evident, as now we never have more than 10000 loops alive, while
previously we got up to about 37000 ones.  The time on the X axis is expressed
in "Giga Ticks", where a tick is the value read out of the <a class="reference external" href="https://en.wikipedia.org/wiki/Time_Stamp_Counter">Time Stamp Counter</a>
of the CPU.</p>

<a href="https://3.bp.blogspot.com/_4gR6Ggu8oHQ/TO-wIZWQVmI/AAAAAAAAAKs/J4PKLIFxxOc/s1600/loop-longevity-64-gcdelta.png"><img alt="" border="0" id="BLOGGER_PHOTO_ID_5543843324606043746" src="https://3.bp.blogspot.com/_4gR6Ggu8oHQ/TO-wIZWQVmI/AAAAAAAAAKs/J4PKLIFxxOc/s600/loop-longevity-64-gcdelta.png" style="cursor: pointer; cursor: hand; width: 600px; height: 306px;"></a>

<p>The grey vertical bars represent the beginning of each phase of the
translation:</p>
<ul class="simple">
<li><tt class="docutils literal">annotate</tt> performs control flow graph construction and type inference.</li>
<li><tt class="docutils literal">rtype</tt> lowers the abstraction level of the control flow graphs with types to that of C.</li>
<li><tt class="docutils literal">pyjitpl</tt> constructs the JIT.</li>
<li><tt class="docutils literal">backendopt</tt> optimizes the control flow graphs.</li>
<li><tt class="docutils literal">stackcheckinsertion</tt> finds the places in the call graph that can overflow the C stack and inserts checks that raise an exception instead.</li>
<li><tt class="docutils literal">database_c</tt> produces a database of all the objects the C code will have to know about.</li>
<li><tt class="docutils literal">source_c</tt> produces the C source code.</li>
<li><tt class="docutils literal">compile_c</tt> calls the compiler to produce the executable.</li>
</ul>
<p>You can nicely see, how the number of alive graphs drops shortly after the
beginning of a new phase.</p>
<p>Those two fixes, freeing loops and generators, improve the memory usage greatly:
now, translating PyPy
on PyPy on 32-bit consumes 2 GB of RAM, while on CPython it consumes 1.1 GB.
This result can even be improved somewhat, because we are not actually freeing
the assembler code itself, but
only the large data structures around it; we can consider it as a residual
memory leak of around 150 MB in this case.  This will be fixed in the
<a class="reference external" href="https://codespeak.net/svn/pypy/branch/jit-free-asm/">jit-free-asm</a> branch.</p>
<p>The following graph shows the memory usage in more detail:</p>
<blockquote>
<ul class="simple">
<li>the blue line (<strong>cpython-scaled</strong>) shows the total amount of RAM that the
OS allocates for CPython.  Note that the X axis (the time) has been
scaled down so that it spans as much as the PyPy one, to ease the
comparison. Actually, CPython took more than twice as much time as PyPy to
complete the translation</li>
<li>the red line (<strong>VmRss</strong>) shows the total amount of RAM that the
OS allocates for PyPy: it includes both the memory directly handled by
our GC and the "raw memory" that we need to allocate for other tasks, such
as the assembly code generated by the JIT</li>
<li>the brown line (<strong>gc-before</strong>) shows how much memory is used by the GC
before each major collection</li>
<li>the yellow line (<strong>gc-after</strong>) shows how much memory is used by the GC
after each major collection: this represent the amount of memory which is
actually needed to hold our Python objects.  The difference between
gc-before and gc-after (the <em>GC delta</em>) is the amout of memory that the GC
uses before triggering a new major collection</li>
</ul>
</blockquote>

<a href="https://1.bp.blogspot.com/_4gR6Ggu8oHQ/TO-wX3gomAI/AAAAAAAAAK0/sQhn6oMjWdY/s1600/memory-32.png"><img alt="" border="0" id="BLOGGER_PHOTO_ID_5543843590400677890" src="https://1.bp.blogspot.com/_4gR6Ggu8oHQ/TO-wX3gomAI/AAAAAAAAAK0/sQhn6oMjWdY/s600/memory-32.png" style="cursor: pointer; cursor: hand; width: 600px; height: 306px;"></a>

<p>By comparing <strong>gc-after</strong> and <strong>cpython-scaled</strong>, we can see that PyPy
uses mostly the same amount of memory as CPython for storing the application
objects (due to reference counting the memory usage in CPython is always very
close to the actually necessary memory).  The extra memory
used by PyPy is due to the GC delta, to the machine code generated by the JIT
and probably to some other external effect (such as e.g. <a class="reference external" href="https://en.wikipedia.org/wiki/Memory_fragmentation">Memory
Fragmentation</a>).</p>
<p>Note that the GC delta can be set arbitrarly low (another recent addition --
the default value depends on the actual RAM on your computer; it probably
works to translate if your computer has precisely 2 GB, because in this
case the GC delta and thus the total memory usage will be somewhat
lower than reported here), but the cost is to have more
frequent major collections and thus a higher run-time overhead.  The same is
true for the memory needed by the JIT, which can be reduced by telling the JIT
to compile less often or to discard old loops more frequently.  As often
happens in computer science, there is a trade-off between space and time, and
currently for this particular example PyPy runs twice as fast as CPython by
doubling the memory usage. We hope to improve even more on this trade-off.</p>
<p>On 64-bit, things are even better as shown by the the following graph:</p>

<a href="https://1.bp.blogspot.com/_4gR6Ggu8oHQ/TO-whfBmjLI/AAAAAAAAAK8/eUOmx59dA80/s1600/memory-64-gcdelta.png"><img alt="" border="0" id="BLOGGER_PHOTO_ID_5543843755626761394" src="https://1.bp.blogspot.com/_4gR6Ggu8oHQ/TO-whfBmjLI/AAAAAAAAAK8/eUOmx59dA80/s600/memory-64-gcdelta.png" style="cursor: pointer; cursor: hand; width: 600px; height: 306px;"></a>

<p>The general shape of the lines is similar to the 32-bit graph. However, the
relative difference to CPython is much better: we need about 3 GB of RAM, just
24% more than the 2.4 GB needed by CPython.  And we are still more than 2x
faster!</p>
<p>The memory saving is due (partly?) to the vtable ptr optimization, which is
enabled by default on 64-bit because it has no speed penalty (see
<a class="reference external" href="/posts/2009/10/gc-improvements-6174120095428192954.html">Unifying the vtable ptr with the GC header</a>).</p>
<p>The net result of our work is that now translating PyPy on PyPy is practical
and takes less than 30 minutes.  It's impressive how quickly you get used to
translation taking half the time -- now we cannot use CPython any more for that
because it feels too slow :-).</p></body></html>