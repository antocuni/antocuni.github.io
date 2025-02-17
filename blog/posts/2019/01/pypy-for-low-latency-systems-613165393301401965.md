---
date: 2019-01-03 14:21:00
title: "PyPy for low-latency systems"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - gc
  - sponsors
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2019/01/pypy-for-low-latency-systems-613165393301401965.html).


<html><body><h1 class="title">
PyPy for low-latency systems</h1>
Recently I have merged the gc-disable branch, introducing a couple of features
which are useful when you need to respond to certain events with the lowest
possible latency.  This work has been kindly sponsored by <a class="reference external" href="https://www.gambitresearch.com/">Gambit Research</a>
(which, by the way, is a very cool and geeky place where to <a class="reference external" href="https://www.gambitresearch.com/jobs.html">work</a>, in case you
are interested).  Note also that this is a very specialized use case, so these
features might not be useful for the average PyPy user, unless you have the
same problems as described here.
<br>
<!-- more -->

<br>
The PyPy VM manages memory using a generational, moving Garbage Collector.
Periodically, the GC scans the whole heap to find unreachable objects and
frees the corresponding memory.  Although at a first look this strategy might
sound expensive, in practice the total cost of memory management is far less
than e.g. on CPython, which is based on reference counting.  While maybe
counter-intuitive, the main advantage of a non-refcount strategy is
that allocation is very fast (especially compared to malloc-based allocators),
and deallocation of objects which die young is basically for free. More
information about the PyPy GC is available <a class="reference external" href="https://pypy.readthedocs.io/en/latest/gc_info.html#incminimark">here</a>.<br>
<br>
As we said, the total cost of memory managment is less on PyPy than on
CPython, and it's one of the reasons why PyPy is so fast.  However, one big
disadvantage is that while on CPython the cost of memory management is spread
all over the execution of the program, on PyPy it is concentrated into GC
runs, causing observable pauses which interrupt the execution of the user
program.<br>
To avoid excessively long pauses, the PyPy GC has been using an <a class="reference external" href="/posts/2013/10/incremental-garbage-collector-in-pypy-8956893523842234676.html">incremental
strategy</a> since 2013. The GC runs as a series of "steps", letting the user
program to progress between each step.<br>
<br>
The following chart shows the behavior of a real-world, long-running process:<br>
<div class="separator" style="clear: both; text-align: center;">
<a href="https://3.bp.blogspot.com/-44yKwUVK3BE/XC4X9XL4BII/AAAAAAAABbE/XdTCIoyA-eYxvxIgJhFHaKnzxjhoWStHQCEwYBhgL/s1600/gc-timing.png" style="margin-right: 1em;"><img border="0" height="246" src="https://3.bp.blogspot.com/-44yKwUVK3BE/XC4X9XL4BII/AAAAAAAABbE/XdTCIoyA-eYxvxIgJhFHaKnzxjhoWStHQCEwYBhgL/s640/gc-timing.png" width="640"></a></div>
<br>
<br>
The orange line shows the total memory used by the program, which
increases linearly while the program progresses. Every ~5 minutes, the GC
kicks in and the memory usage drops from ~5.2GB to ~2.8GB (this ratio is controlled
by the <a class="reference external" href="https://pypy.readthedocs.io/en/latest/gc_info.html#environment-variables">PYPY_GC_MAJOR_COLLECT</a> env variable).<br>
The purple line shows aggregated data about the GC timing: the whole
collection takes ~1400 individual steps over the course of ~1 minute: each
point represent the <strong>maximum</strong> time a single step took during the past 10
seconds. Most steps take ~10-20 ms, although we see a horrible peak of ~100 ms
towards the end. We have not investigated yet what it is caused by, but we
suspect it is related to the deallocation of raw objects.<br>
<br>
These multi-millesecond pauses are a problem for systems where it is important
to respond to certain events with a latency which is both low and consistent.
If the GC kicks in at the wrong time, it might causes unacceptable pauses during
the collection cycle.<br>
<br>
Let's look again at our real-world example. This is a system which
continuously monitors an external stream; when a certain event occurs, we want
to take an action. The following chart shows the maximum time it takes to
complete one of such actions, aggregated every minute:<br>
<br>
<div class="separator" style="clear: both; text-align: center;">
<a href="https://4.bp.blogspot.com/-FO9uFHSqZzU/XC4YC8LZUpI/AAAAAAAABa8/B8ZOrEgbVJUHoO65wxvCMVpvciO_d_0TwCLcBGAs/s1600/normal-max.png" style="margin-right: 1em;"><img border="0" height="240" src="https://4.bp.blogspot.com/-FO9uFHSqZzU/XC4YC8LZUpI/AAAAAAAABa8/B8ZOrEgbVJUHoO65wxvCMVpvciO_d_0TwCLcBGAs/s640/normal-max.png" width="640"></a></div>
<br>
You can clearly see that the baseline response time is around ~20-30
ms. However, we can also see periodic spikes around ~50-100 ms, with peaks up
to ~350-450 ms! After a bit of investigation, we concluded that most (although
not all) of the spikes were caused by the GC kicking in at the wrong time.<br>
<br>
The work I did in the <tt class="docutils literal"><span class="pre">gc-disable</span></tt> branch aims to fix this problem by
introducing <a class="reference external" href="https://pypy.readthedocs.io/en/latest/gc_info.html#semi-manual-gc-management">two new features</a> to the <tt class="docutils literal">gc</tt> module:<br>
<blockquote>
<ul class="simple">
<li><tt class="docutils literal">gc.disable()</tt>, which previously only inhibited the execution of
finalizers without actually touching the GC, now disables the GC major
collections. After a call to it, you will see the memory usage grow
indefinitely.</li>
<li><tt class="docutils literal">gc.collect_step()</tt> is a new function which you can use to manually
execute a single incremental GC collection step.</li>
</ul>
</blockquote>
It is worth to specify that <tt class="docutils literal">gc.disable()</tt> disables <strong>only</strong> the major
collections, while minor collections still runs.  Moreover, thanks to the
JIT's virtuals, many objects with a short and predictable lifetime are not
allocated at all. The end result is that most objects with short lifetime are
still collected as usual, so the impact of <tt class="docutils literal">gc.disable()</tt> on memory growth
is not as bad as it could sound.<br>
<br>
Combining these two functions, it is possible to take control of the GC to
make sure it runs only when it is acceptable to do so.  For an example of
usage, you can look at the implementation of a <a class="reference external" href="https://github.com/antocuni/pypytools/blob/master/pypytools/gc/custom.py">custom GC</a> inside <a class="reference external" href="https://pypi.org/project/pypytools/">pypytools</a>.
The peculiarity is that it also defines a "<tt class="docutils literal">with <span class="pre">nogc():"</span></tt> context manager
which you can use to mark performance-critical sections where the GC is not
allowed to run.<br>
<br>
The following chart compares the behavior of the default PyPy GC and the new
custom GC, after a careful placing of <tt class="docutils literal">nogc()</tt> sections:<br>
<br>
<div class="separator" style="clear: both; text-align: center;">
<a href="https://1.bp.blogspot.com/-bGqs0WrOEBk/XC4YJN0uZfI/AAAAAAAABbA/4EXOASvy830IKBoTFtrnmY22Vyd_api-ACLcBGAs/s1600/nogc-max.png" style="margin-right: 1em;"><img border="0" height="242" src="https://1.bp.blogspot.com/-bGqs0WrOEBk/XC4YJN0uZfI/AAAAAAAABbA/4EXOASvy830IKBoTFtrnmY22Vyd_api-ACLcBGAs/s640/nogc-max.png" width="640"></a></div>
<br>
The yellow line is the same as before, while the purple line shows the new
system: almost all spikes have gone, and the baseline performance is about 10%
better. There is still one spike towards the end, but after some investigation
we concluded that it was <strong>not</strong> caused by the GC.<br>
<br>
Note that this does <strong>not</strong> mean that the whole program became magically
faster: we simply moved the GC pauses in some other place which is <strong>not</strong>
shown in the graph: in this specific use case this technique was useful
because it allowed us to shift the GC work in places where pauses are more
acceptable.<br>
<br>
All in all, a pretty big success, I think.  These functionalities are already
available in the nightly builds of PyPy, and will be included in the next
release: take this as a New Year present :)<br>
<br>
Antonio Cuni and the PyPy team</body></html>
