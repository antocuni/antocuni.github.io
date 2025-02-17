---
date: 2019-12-18 13:38:00
title: "HPy kick-off sprint report"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - hpy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2019/12/hpy-kick-off-sprint-report-1840829336092490938.html).


<html><body><p>Recently Antonio, Armin and Ronan had a small internal sprint in the beautiful
city of Gdańsk to kick-off the development of HPy. Here is a brief report of
what was accomplished during the sprint.
</p>
<!-- more -->

<div class="section" id="what-is-hpy">
<h2>What is HPy?</h2>
<p>The TL;DR answer is "a better way to write C extensions for Python".</p>
<p>The idea of HPy was born during EuroPython 2019 in Basel, where there was an
informal meeting which included core developers of PyPy, CPython (Victor
Stinner and Mark Shannon) and Cython (Stefan Behnel). The ideas were later also
discussed with Tim Felgentreff of <a class="reference external" href="https://github.com/graalvm/graalpython">GraalPython</a>, to make sure they would also be
applicable to this very different implementation, Windel Bouwman of <a class="reference external" href="https://github.com/RustPython/RustPython">RustPython</a>
is following the project as well.</p>
<p>All of us agreed that the current design of the CPython C API is problematic
for various reasons and, in particular, because it is too tied to the current
internal design of CPython.  The end result is that:</p>

<ul class="simple">
<li>alternative implementations of Python (such as PyPy, but not only) have a
<a class="reference external" href="/posts/2018/09/inside-cpyext-why-emulating-cpython-c-8083064623681286567.html">hard time</a> loading and executing existing C extensions;</li>
<li>CPython itself is unable to change some of its internal implementation
details without breaking the world. For example, as of today it would be
impossible to switch from using reference counting to using a real GC,
which in turns make it hard for example to remove the GIL, as <a class="reference external" href="https://pythoncapi.readthedocs.io/gilectomy.html">gilectomy</a>
attempted.</li>
</ul>

<p>HPy tries to address these issues by following two major design guidelines:</p>
<ol class="arabic simple">
<li>objects are referenced and passed around using opaque handles, which are
similar to e.g., file descriptors in spirit. Multiple, different handles
can point to the same underlying object, handles can be duplicated and
each handle must be released independently of any other duplicate.</li>
<li>The internal data structures and C-level layout of objects are not
visible nor accessible using the API, so each implementation if free to
use what fits best.</li>
</ol>
<p>The other major design goal of HPy is to allow incremental transition and
porting, so existing modules can migrate their codebase one method at a time.
Moreover, Cython is considering to optionally generate HPy code, so extension
module written in Cython would be able to benefit from HPy automatically.</p>
<p>More details can be found in the README of the official <a class="reference external" href="https://github.com/pyhandle/hpy">HPy repository</a>.</p>
</div>
<div class="section" id="target-abi">
<h2>Target ABI</h2>
<p>When compiling an HPy extension you can choose one of two different target ABIs:</p>

<ul class="simple">
<li><strong>HPy/CPython ABI</strong>: in this case, <tt class="docutils literal">hpy.h</tt> contains a set of macros and
static inline functions. At compilation time this translates the HPy API
into the standard C-API. The compiled module will have no performance
penalty, and it will have a "standard" filename like
<tt class="docutils literal"><span class="pre">foo.cpython-37m-x86_64-linux-gnu.so</span></tt>.</li>
<li><strong>Universal HPy ABI</strong>: as the name implies, extension modules compiled
this way are "universal" and can be loaded unmodified by multiple Python
interpreters and versions.  Moreover, it will be possible to dynamically
enable a special debug mode which will make it easy to find e.g., open
handles or memory leaks, <strong>without having to recompile the extension</strong>.</li>
</ul>

<p>Universal modules can <strong>also</strong> be loaded on CPython, thanks to the
<tt class="docutils literal">hpy_universal</tt> module which is under development. An extra layer of
indirection enables loading extensions compiled with the universal ABI. Users
of <tt class="docutils literal">hpy_universal</tt> will face a small performance penalty compared to the ones
using the HPy/CPython ABI.</p>
<p>This setup gives several benefits:</p>

<ul class="simple">
<li>Extension developers can use the extra debug features given by the
Universal ABI with no need to use a special debug version of Python.</li>
<li>Projects which need the maximum level of performance can compile their
extension for each relevant version of CPython, as they are doing now.</li>
<li>Projects for which runtime speed is less important will have the choice of
distributing a single binary which will work on any version and
implementation of Python.</li>
</ul>

</div>
<div class="section" id="a-simple-example">
<h2>A simple example</h2>
<p>The HPy repo contains a <a class="reference external" href="https://github.com/pyhandle/hpy/blob/master/proof-of-concept/pof.c">proof of concept</a> module. Here is a simplified
version which illustrates what a HPy module looks like:</p>
<pre class="code C literal-block">
<span class="comment preproc">#include</span> <span class="comment preprocfile">"hpy.h"</span><span class="comment preproc">
</span>
<span class="name">HPy_DEF_METH_VARARGS</span><span class="punctuation">(</span><span class="name">add_ints</span><span class="punctuation">)</span>
<span class="keyword">static</span> <span class="name">HPy</span> <span class="name">add_ints_impl</span><span class="punctuation">(</span><span class="name">HPyContext</span> <span class="name">ctx</span><span class="punctuation">,</span> <span class="name">HPy</span> <span class="name">self</span><span class="punctuation">,</span> <span class="name">HPy</span> <span class="operator">*</span><span class="name">args</span><span class="punctuation">,</span> <span class="name">HPy_ssize_t</span> <span class="name">nargs</span><span class="punctuation">)</span>
<span class="punctuation">{</span>
    <span class="keyword type">long</span> <span class="name">a</span><span class="punctuation">,</span> <span class="name">b</span><span class="punctuation">;</span>
    <span class="keyword">if</span> <span class="punctuation">(</span><span class="operator">!</span><span class="name">HPyArg_Parse</span><span class="punctuation">(</span><span class="name">ctx</span><span class="punctuation">,</span> <span class="name">args</span><span class="punctuation">,</span> <span class="name">nargs</span><span class="punctuation">,</span> <span class="literal string">"ll"</span><span class="punctuation">,</span> <span class="operator">&amp;</span><span class="name">a</span><span class="punctuation">,</span> <span class="operator">&amp;</span><span class="name">b</span><span class="punctuation">))</span>
        <span class="keyword">return</span> <span class="name">HPy_NULL</span><span class="punctuation">;</span>
    <span class="keyword">return</span> <span class="name function">HPyLong_FromLong</span><span class="punctuation">(</span><span class="name">ctx</span><span class="punctuation">,</span> <span class="name">a</span><span class="operator">+</span><span class="name">b</span><span class="punctuation">);</span>
<span class="punctuation">}</span>


<span class="keyword">static</span> <span class="name">HPyMethodDef</span> <span class="name">PofMethods</span><span class="punctuation">[]</span> <span class="operator">=</span> <span class="punctuation">{</span>
    <span class="punctuation">{</span><span class="literal string">"add_ints"</span><span class="punctuation">,</span> <span class="name">add_ints</span><span class="punctuation">,</span> <span class="name">HPy_METH_VARARGS</span><span class="punctuation">,</span> <span class="literal string">""</span><span class="punctuation">},</span>
    <span class="punctuation">{</span><span class="name builtin">NULL</span><span class="punctuation">,</span> <span class="name builtin">NULL</span><span class="punctuation">,</span> <span class="literal number integer">0</span><span class="punctuation">,</span> <span class="name builtin">NULL</span><span class="punctuation">}</span>
<span class="punctuation">};</span>

<span class="keyword">static</span> <span class="name">HPyModuleDef</span> <span class="name">moduledef</span> <span class="operator">=</span> <span class="punctuation">{</span>
    <span class="name">HPyModuleDef_HEAD_INIT</span><span class="punctuation">,</span>
    <span class="punctuation">.</span><span class="name">m_name</span> <span class="operator">=</span> <span class="literal string">"pof"</span><span class="punctuation">,</span>
    <span class="punctuation">.</span><span class="name">m_doc</span> <span class="operator">=</span> <span class="literal string">"HPy Proof of Concept"</span><span class="punctuation">,</span>
    <span class="punctuation">.</span><span class="name">m_size</span> <span class="operator">=</span> <span class="operator">-</span><span class="literal number integer">1</span><span class="punctuation">,</span>
    <span class="punctuation">.</span><span class="name">m_methods</span> <span class="operator">=</span> <span class="name">PofMethods</span>
<span class="punctuation">};</span>


<span class="name">HPy_MODINIT</span><span class="punctuation">(</span><span class="name">pof</span><span class="punctuation">)</span>
<span class="keyword">static</span> <span class="name">HPy</span> <span class="name">init_pof_impl</span><span class="punctuation">(</span><span class="name">HPyContext</span> <span class="name">ctx</span><span class="punctuation">)</span>
<span class="punctuation">{</span>
    <span class="name">HPy</span> <span class="name">m</span><span class="punctuation">;</span>
    <span class="name">m</span> <span class="operator">=</span> <span class="name">HPyModule_Create</span><span class="punctuation">(</span><span class="name">ctx</span><span class="punctuation">,</span> <span class="operator">&amp;</span><span class="name">moduledef</span><span class="punctuation">);</span>
    <span class="keyword">if</span> <span class="punctuation">(</span><span class="name">HPy_IsNull</span><span class="punctuation">(</span><span class="name">m</span><span class="punctuation">))</span>
        <span class="keyword">return</span> <span class="name">HPy_NULL</span><span class="punctuation">;</span>
    <span class="keyword">return</span> <span class="name">m</span><span class="punctuation">;</span>
<span class="punctuation">}</span>
</pre>
<p>People who are familiar with the current C-API will surely notice many
similarities. The biggest differences are:</p>

<ul class="simple">
<li>Instead of <tt class="docutils literal">PyObject *</tt>, objects have the type <tt class="docutils literal">HPy</tt>, which as
explained above represents a handle.</li>
<li>You need to explicitly pass an <tt class="docutils literal">HPyContext</tt> around: the intent is
primary to be future-proof and make it easier to implement things like
sub- interpreters.</li>
<li><tt class="docutils literal">HPy_METH_VARARGS</tt> is implemented differently than CPython's
<tt class="docutils literal">METH_VARARGS</tt>: in particular, these methods receive an array of <tt class="docutils literal">HPy</tt>
and its length, instead of a fully constructed tuple: passing a tuple
makes sense on CPython where you have it anyway, but it might be an
unnecessary burden for alternate implementations.  Note that this is
similar to the new <a class="reference external" href="https://www.python.org/dev/peps/pep-0580/">METH_FASTCALL</a> which was introduced in CPython.</li>
<li>HPy relies a lot on C macros, which most of the time are needed to support
the HPy/CPython ABI compilation mode. For example, <tt class="docutils literal">HPy_DEF_METH_VARARGS</tt>
expands into a trampoline which has the correct C signature that CPython
expects (i.e., <tt class="docutils literal">PyObject <span class="pre">(*)(PyObject</span> *self, *PyObject *args)</tt>) and
which calls <tt class="docutils literal">add_ints_impl</tt>.</li>
</ul>

</div>
<div class="section" id="sprint-report-and-current-status">
<h2>Sprint report and current status</h2>
<p>After this long preamble, here is a rough list of what we accomplished during
the week-long sprint and the days immediatly after.</p>
<p>On the HPy side, we kicked-off the code in the repo: at the moment of writing
the layout of the directories is a bit messy because we moved things around
several times, but we identified several main sections:</p>

<ol class="arabic">
<li><p class="first">A specification of the API which serves both as documentation and as an
input for parts of the projects which are automatically
generated. Currently, this lives in <a class="reference external" href="https://github.com/pyhandle/hpy/blob/9aa8a2738af3fd2eda69d4773b319d10a9a5373f/tools/public_api.h">public_api.h</a>.</p>
</li>
<li><p class="first">A set of header files which can be used to compile extension modules:
depending on whether the flag <tt class="docutils literal"><span class="pre">-DHPY_UNIVERSAL_ABI</span></tt> is passed to the
compiler, the extension can target the <a class="reference external" href="https://github.com/pyhandle/hpy/blob/9aa8a2738af3fd2eda69d4773b319d10a9a5373f/hpy-api/hpy_devel/include/cpython/hpy.h">HPy/CPython ABI</a> or the <a class="reference external" href="https://github.com/pyhandle/hpy/blob/9aa8a2738af3fd2eda69d4773b319d10a9a5373f/hpy-api/hpy_devel/include/universal/hpy.h">HPy
Universal ABI</a></p>
</li>
<li><p class="first">A <a class="reference external" href="https://github.com/pyhandle/hpy/tree/9aa8a2738af3fd2eda69d4773b319d10a9a5373f/cpython-universal/src">CPython extension module</a> called <tt class="docutils literal">hpy_universal</tt> which makes it
possible to import universal modules on CPython</p>
</li>
<li><p class="first">A set of <a class="reference external" href="https://github.com/pyhandle/hpy/tree/9aa8a2738af3fd2eda69d4773b319d10a9a5373f/test">tests</a> which are independent of the implementation and are meant
to be an "executable specification" of the semantics.  Currently, these
tests are run against three different implementations of the HPy API:</p>

<ul class="simple">
<li>the headers which implements the "HPy/CPython ABI"</li>
<li>the <tt class="docutils literal">hpy_universal</tt> module for CPython</li>
<li>the <tt class="docutils literal">hpy_universal</tt> module for PyPy (these tests are run in the PyPy repo)</li>
</ul>

</li>
</ol>

<p>Moreover, we started a <a class="reference external" href="https://foss.heptapod.net/pypy/pypy/-/tree/branch/hpy/pypy/module/hpy_universal/">PyPy branch</a> in which to implement the
<tt class="docutils literal">hpy_univeral</tt> module: at the moment of writing PyPy can pass all the HPy
tests apart the ones which allow conversion to and from <tt class="docutils literal">PyObject *</tt>.
Among the other things, this means that it is already possible to load the
very same binary module in both CPython and PyPy, which is impressive on its
own :).</p>
<p>Finally, we wanted a real-life use case to show how to port a module to HPy
and to do benchmarks.  After some searching, we choose <a class="reference external" href="https://github.com/esnme/ultrajson">ultrajson</a>, for the
following reasons:</p>

<ul class="simple">
<li>it is a real-world extension module which was written with performance in
mind</li>
<li>when parsing a JSON file it does a lot of calls to the Python API to
construct the various parts of the result message</li>
<li>it uses only a small subset of the Python API</li>
</ul>

<p>This repo contains the <a class="reference external" href="https://github.com/pyhandle/ultrajson-hpy">HPy port of ultrajson</a>. This <a class="reference external" href="https://github.com/pyhandle/ultrajson-hpy/commit/efb35807afa8cf57db5df6a3dfd4b64c289fe907">commit</a> shows an example
of what the porting looks like.</p>
<p><tt class="docutils literal">ujson_hpy</tt> is also a very good example of incremental migration: so far
only <tt class="docutils literal">ujson.loads</tt> is implemented using the HPy API, while <tt class="docutils literal">ujson.dumps</tt>
is still implemented using the old C-API, and both can coexist nicely in the
same compiled module.</p>
</div>
<div class="section" id="benchmarks">
<h2>Benchmarks</h2>
<p>Once we have a fully working <tt class="docutils literal">ujson_hpy</tt> module, we can finally run
benchmarks!  We tested several different versions of the module:</p>

<ul class="simple">
<li><tt class="docutils literal">ujson</tt>: this is the vanilla implementation of ultrajson using the
C-API. On PyPy this is executed by the infamous <tt class="docutils literal">cpyext</tt> compatibility
layer, so we expect it to be much slower than on CPython</li>
<li><tt class="docutils literal">ujson_hpy</tt>: our HPy port compiled to target the HPy/CPython ABI. We
expect it to be as fast as <tt class="docutils literal">ujson</tt></li>
<li><tt class="docutils literal">ujson_hpy_universal</tt>: same as above but compiled to target the
Universal HPy ABI. We expect it to be slightly slower than <tt class="docutils literal">ujson</tt> on
CPython, and much faster on PyPy.</li>
</ul>

<p>Finally, we also ran the benchmark using the builtin <tt class="docutils literal">json</tt> module. This is
not really relevant to HPy, but it might still be an interesting as a
reference data point.</p>
<p>The <a class="reference external" href="https://github.com/pyhandle/ultrajson-hpy/blob/hpy/benchmark/main.py">benchmark</a> is very simple and consists of parsing a <a class="reference external" href="https://github.com/pyhandle/ultrajson-hpy/blob/hpy/benchmark/download_data.sh">big JSON file</a> 100
times. Here is the average time per iteration (in milliseconds) using the
various versions of the module, CPython 3.7 and the latest version of the hpy
PyPy branch:</p>
<table border="1" class="docutils">
<colgroup>
<col width="55%">
<col width="24%">
<col width="21%">
</colgroup>
<tbody valign="top">
<tr><td> </td>
<td>CPython</td>
<td>PyPy</td>
</tr>
<tr><td>ujson</td>
<td>154.32</td>
<td>633.97</td>
</tr>
<tr><td>ujson_hpy</td>
<td>152.19</td>
<td> </td>
</tr>
<tr><td>ujson_hpy_universal</td>
<td>168.78</td>
<td>207.68</td>
</tr>
<tr><td>json</td>
<td>224.59</td>
<td>135.43</td>
</tr>
</tbody>
</table>
<p>As expected, the benchmark proves that when targeting the HPy/CPython ABI, HPy
doesn't impose any performance penalty on CPython. The universal version is
~10% slower on CPython, but gives an impressive 3x speedup on PyPy! It it
worth noting that the PyPy hpy module is not fully optimized yet, and we
expect to be able to reach the same performance as CPython for this particular
example (or even more, thanks to our better GC).</p>
<p>All in all, not a bad result for two weeks of intense hacking :)</p>
<p>It is also worth noting than PyPy's builtin <tt class="docutils literal">json</tt> module does <strong>really</strong>
well in this benchmark, thanks to the recent optimizations that were described
in an <a class="reference external" href="/posts/2019/10/pypys-new-json-parser-492911724084305501.html">earlier blog post</a>.</p>
</div>
<div class="section" id="conclusion-and-future-directions">
<h2>Conclusion and future directions</h2>
<p>We think we can be very satisfied about what we have got so far. The
development of HPy is quite new, but these early results seem to indicate that
we are on the right track to bring Python extensions into the future.</p>
<p>At the moment, we can anticipate some of the next steps in the development of
HPy:</p>

<ul class="simple">
<li>Think about a proper API design: what we have done so far has
been a "dumb" translation of the API we needed to run <tt class="docutils literal">ujson</tt>. However,
one of the declared goal of HPy is to improve the design of the API. There
will be a trade-off between the desire of having a clean, fresh new API
and the need to be not too different than the old one, to make porting
easier.  Finding the sweet spot will not be easy!</li>
<li>Implement the "debug" mode, which will help developers to find
bugs such as leaking handles or using invalid handles.</li>
<li>Instruct Cython to emit HPy code on request.</li>
<li>Eventually, we will also want to try to port parts of <tt class="docutils literal">numpy</tt> to HPy to
finally solve the long-standing problem of sub-optimal <tt class="docutils literal">numpy</tt>
performance in PyPy.</li>
</ul>

<p>Stay tuned!</p>

</div></body></html>