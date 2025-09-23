---
draft: true
date: 2025-09-23
title: "Tracing JITs in the real world @ CPython Core Dev Sprint"
categories:
  - Post
tags:
  - slides
  - cpython
  - pypy
  - jit
  - c-api
---

# Tracing JITs in the real world @ CPython Core Dev Sprint

<style>
.slide-container {
  border: 2px solid #ddd;
  border-radius: 8px;
  margin: 2em 0;
  background: #f9f9f9;
  max-width: 100%;
}

.slide {
  aspect-ratio: 16 / 9;
  box-sizing: border-box;
  padding: 2em;
  background: white;
  border-radius: 6px 6px 0 0;
  border-bottom: 2px solid #eee;
  display: block;
  width: 100%;
}

.slide h1, .slide h2, .slide h3 {
  margin-top: 0;
  color: #333;
}

.annotation {
  padding: 1.5em;
  background: #f9f9f9;
  color: #666;
}

.annotation h4 {
  margin-top: 0;
  color: #444;
  font-style: normal;
}
</style>

Last week I got to take part in the CPython Core Developer Sprint in
Cambridge, hosted by ARM and brilliantly
[organized by Diego Russo](https://www.linkedin.com/posts/diegor_yesterday-we-wrapped-up-thecpython-core-activity-7375230888177057792-GezI)
-- about ~50 core devs and guests were there, and I was excited to join as one
of the guests.

I had three main areas of focus:

  - **C API**: this was a follow up of what we discussed at the
    [C API summit at EuroPython](../07-europython-talks/index.md). The current
    C API is problematic, so we are exploring ideas for the development of
    [PyNI](https://github.com/py-ni) (Python Native Interface), whose design
    will be likely be heavily inspired by HPy. It's important to underline
    that this is just the beginning and the entire process will require
    multiple PEPs.

  - **fancycompleter** This is a
    [small PR](https://github.com/python/cpython/pull/130473) which I started
    months ago, to enable colorful tab completions within the Python REPL. I
    wrote the original version of
    [fancycompleter](https://github.com/pdbpp/fancycompleter) 15 years ago,
    but colorful completions works only in combination with PyREPL. Now
    PyREPL is part of the standard library and enabled by default, so we can
    finally upstream it. I hope to see it merged soon.

  - "**JIT stuff**": I spent a considerable amount of time talking to the
    people who are working on the CPython JIT (in particular Mark, Brandt,
    Savannah, Ken Jit and Diego). Knowledge transfer worked in both ways: I
    learnt a lot about the internal details of CPython's JIT, and conversely I
    shared with them some of the experience, pain points and gut feelings
    which I got by working many years on PyPy.

In particular, on the first day I presented a talk titled **Tracing JIT and real world Python** ([slides](../../../talk/2025/09/core-dev-sprint-pypy-jit/index.html) and [source code](https://github.com/antocuni/antocuni.github.io/tree/main/blog/talk/2025/09/core-dev-sprint-pypy-jit)).

What follows is an annotated version of the slides.

<!-- more -->

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
## Tracing JIT and real world Python

### aka: what we can learn from PyPy
</div>
<div class="annotation" markdown="1">

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
# Motivation

- CPython's JIT has a lot in common with PyPy

- "Optimize for PyPy" ==> my job for ~7 years

- Real world code != pyperformance

- Challenges & lesson learned
</div>
<div class="annotation" markdown="1">

CPython's new JIT and PyPy's JIT share fundamental similarities, as they're both
tracing JITs.

I spent ~7 years of my career optimizing existing code for PyPy at a
high-frequency trading firm, which makes me one of the few people in the world
with actual experience in optimizing real world Python code for a tracing JIT.

I expect that some of the challenges which I faced will still be valid also
for CPython, and I wanted to share my experience to make sure that CPython
core devs are aware of them.

One lesson which I learnt is that the set of benchmarks in `pyperformance` are
a good starting point, but they are not entierly representative of what you
find in the wild.

The main goal of the talk is not to present *solutions* to these problems,,
but to raise awareness that they exist.

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
# Assumption

- The JIT revolutionizes performance characteristics

- CPython perf will look like PyPy's

- ==> Some results are surprising
</div>
<div class="annotation" markdown="1">

Until now CPython's performance have been particularly predictable, there are
well estabilished "performance tricks" to make code faster, and generally
speaking you can mostly reason about the local speed of a give piece of code.

Adding a JIT completely changes how we reason about performance of a given
program, for two reasons:

  1. JITted code can be very fast if your code conforms to the heuristics
     applied by the JIT compiler

  2. The speed of a given piece might depend a lot on what happens "very far"
     from that code, and it becomes much harder to reason "locally" about
     speed

The end result is that modifiying a single line of code "here" can have a big
inpact on code which looks totally unrelated, for multiple reasons.  This
effect becomes bigger as the JIT becomes "smarter".

The CPython JIT is still pretty new and doesn’t give huge speedups yet. I
expect that as it gets faster, its performance will start looking more and
more like PyPy’s.

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
# Context

- High Frequency Trading firm (sport betting)

  * every ms counts

- Python 2.7

- Multi process system: stateful server + dispatcher + stateless workers (long running processes)

- "big" messages passed around
</div>
<div class="annotation" markdown="1">

Let me give you some context about where this experience comes from. I worked
at a high-frequency trading firm focused on sports betting, where every
millisecond of latency matters for profitability. We were using Python 2.7 in
a multi-process architecture with long-running processes - perfect for JIT
warmup.

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
## PyPy JIT 101

- Interpreter written in RPython

- RPython -> `*.c` -> gcc -> `./pypy`

- RPython -> "jit codegen" -> "jitcodes" (~RPython IR)

- RPython jitcodes ~= CPython microops

  * Slightly higher level than C

- Tracing means *executing jitcodes*

  * we have an interpreter for that, super slow
</div>
<div class="annotation" markdown="1">

I delivered this talk at the Core Dev Sprint: I expected my audience to be
familiar with CPython's JIT, and wanted to draw parallels with PyPy's one.

Since the audience of this blog is different, let me **briefly** explain
CPython's JIT first.

The explanation of both JITs are necessarily short, incomplete and highly
simplified.

#### CPython JIT 101 first

Python source code is turned into bytecode. Bytecode is a sequence of
"opcodes", and the CPython VM is an interpreter for those
opcodes. Historically, VM was written by hand, and the main loop consisted of
a big `switch` statement which executed the code corresponding to each opcode.

Nowadays things are different: the opcodes are written in a special DSL and
the main interpreter loop is automatically generated from this
DSL. Additionally, the DSL describes how each opcode can be decomposed into
multiple "microops".

When the interpreter detects a "hot loop", it starts the JIT. The JIT
retroactively looks at the opcodes which were executed in the last iteration
of the loop, and creates a "linear trace" which contains the equivalent
microops. This process is called **trace projection** and the result is an
unoptimized trace of microops.

Then, the JIT can produce an optimized trace, by reordering and removing
redundant microops. Finally, the optimized trace is turned into executable
code using the "copy & patch" technique.

#### PyPy JIT 101

CPython's Python interpreter is written in C, and then compiled into an
executable by `gcc` (or any other C compiler).

Similarly, PyPy's Python interpreter is written in RPython, and then compiled
into an executable by `rpython`.

Under the hood, `rpython` applies two separate transformations to the source
code:

  - it turns each function into C code, which is then fed to `gcc` to get the
    final executable

  - it turns each function into "jitcodes", which is a way to represent
    RPython's IR (internal representation). For each RPython function, the
    final `./pypy` executable contains its compiled representation (generated
    by GCC) AND its jitcode representation (embedded as static data into the
    executable).

In a way, RPython's jitcodes are equivalent to CPython's microops, as they are
a low-level represenation of the logic of each opcode.

When the interpreter detects a hot loop, it enters **trace recording** mode,
which is essentially an interpreter which executes the jitcodes: the result is
a linear unoptimized trace of all the jitcodes which were actually executed.

Similarly to CPython, PyPy then produces an optimized trace, which is then
sent to the JIT backend for actual native code generation.


</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 1: trace blockers

```python
def get_pi():
    """
    Compute an approximation of PI using the Leibniz series
    """
    tol = 0.0000001
    pi_approx = 0.0
    k = 0
    term = 1.0  # Initial term to enter the loop

    while abs(term) > tol:
        if k % 2 == 0:
            term = 1.0 / (2 * k + 1)
        else:
            term = -1 * 1.0 / (2 * k + 1)

        pi_approx = pi_approx + term
        k = k + 1


    return 4 * pi_approx
```

</div>
<div class="annotation" markdown="1">

Tracing JITs works by recording a trace of all microops which are
executed. The optimize can then reason about what happens in the trace and
remove unneeded operations.

However, sometimes we encounter some operation which is a black box from the
point of view of the tracer: we call them "trace blocker", because the tracing
JIT cannot see through them.  In the case of CPython, this happens for
example, whenever we call any function implemented in C (because it doesn't
have any correspondent "microop").

This is a simple function that computes `pi`, generated by ChatGPT.  Its
precise content is not important: what matters is that it's a nice purely
numerical loop that the PyPy JIT can optimize very well.

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">

### Problem 1: trace blockers

```python
def get_pi():
    """
    Compute an approximation of PI using the Leibniz series
    """
    tol = 0.0000001
    pi_approx = 0.0
    k = 0
    term = 1.0  # Initial term to enter the loop

    while abs(term) > tol:
        if k % 2 == 0:
            term = 1.0 / (2 * k + 1)
        else:
            term = -1 * 1.0 / (2 * k + 1)

        pi_approx = pi_approx + term
        k = k + 1
        hic_sunt_leones() # <<<<<<<<<<<< the JIT cannot enter here

    return 4 * pi_approx
```

</div>
<div class="annotation" markdown="1">

Same function as above, with a call to `hic_sunt_leones()`. This is actually
an **empty function** which does absolutely nothing, but annotated in a
special way so that the PyPy JIT cannot "enter" it, so it effectively behaves
as trace blocker.

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
## Hic sunt leones

```
def empty():
    pass      # the JIT cannot enter here

def hic_sunt_leones():
    pypyjit.residual_call(empty)
```

- Any call to non-traceable function

- C builtins, C extensions

- (for PyPy): RPython instructions not understood by the JIT
</div>
<div class="annotation" markdown="1">

In this example we use the special `pypyjit.residual_call` to simulate a trace
blocker, but in real life we get it whenever we have a call to any
non-traceable function, in particular with C extensions.

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
```
❯ python3.13 pi.py
2.1712 secs, pi = 3.1415928535897395

❯ pypy pi.py
0.0518 secs, pi = 3.1415928535897395

❯ # with "hic_sunt_leones()"
❯ pypy pi.py
1.1808 secs, pi = 3.1415928535897395
```
</div>
<div class="annotation" markdown="1">

The clean version runs 42x faster on PyPy than CPython - that's the JIT
working perfectly. But with just one untraceable function call added to the
loop, PyPy slows down to only 1.8x faster than CPython. That single line
destroyed most of the JIT's effectiveness!

This happens because after the call the optimizer no longer know whether its
assumptions about the world are still true, and thus must be much more
conservative.

I fear that for CPython, this will turn out to be a much bigger problem than
for PyPy, for two reasons:

The first is that it's virtually impossible to run Python code without using
any C extension nowadays (either directly or indirectly)

Moreover, by construction, PyPy's JIT can see much more than CPython's
JIT. Remember he slide about "jitcodes": any RPython function gets a
"jitcodes" equivalent, which means that the JIT can automatially trace inside
builtins and internals of the interpreter, whereas CPython can trace only inside pure python code.

For example, PyPy's JIT can trace through `range()`, `zip` and `enumerate()`
automatically. CPython's JIT currently cannot because they are implemented in
C. CPython *could* add special cases for these common functions, but the
general approach doesn't scale.

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 2: data driven control flow

```python
def fn(v=None, a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=None):
    "Random nonsense computation generated by ChatGPT"
    if v is None: v = 0
    if a is None: a = 1.25
    if b is None: b = -0.75
    [...]
    y = a * v + b
    if y < f: y = f
    [...]
    return y

def main():
    [...]
    for row in DATA:
        acc += fn(*row)
```
</div>
<div class="annotation" markdown="1">

The second big problem is what I call "data driven control flow". This example
has been autogenerated by ChatGPT and it's completely silly, but it's a good
representation of what happens in real life code.

In this example, `fn` takes 9 variables, each of them can be `None` or a
number. The function starts with a sequence of `if <var> is None: ...`. The
function is then called repeatedly in a loop.

One of the assumption of tracing JITs is that control flow tends to stay on
the "hot path", and that it's enough to optimize that to get good performance.

But in a case like this, each combination of `None`ness selects a different
path, and if we assume the data is evenly distributed, we find out that
**there is no hot path**.

Let's see what happens when we execute on CPython and PyPy:

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 2: data driven control flow

```
❯ python3.13 data_driven.py
0.1274 secs

❯ pypy --jit off data_driven.py
0.2953 secs

❯ pypy data_driven.py
1.6414 secs
```
</div>
<div class="annotation" markdown="1">

#### Annotation

PyPy without JIT is "only" 2.3x slower than CPython, but when we enable the
JIT, it becomes **much worse**. This happens becase of an exponential
explosion of code paths seen by the JIT.

In a normal compiler, an `if` statement is compiled as a diamond, and the
control flow merges together after each `if`:

```
        if a is None
          /   \
         /     \
      a = 0    pass
         \     /
          \   /
        if b is None
          /   \
         /     \
      b = 0    pass
         \     /
          \   /
           ...
```

After each `if`, the control flow "merges". A tracing JIT by definition
follows what's happening during a concrete execution, so it sees only a
concrete path in the control flow, with "guards" to ensure correctness:

```
        guard(a is None)
          /
         /
      a = 0
         \
          \
   guard(b not None)
          /
         /
      b = 0
         \
          \

```

When `guard(a is None)` fails enough times, we create a "bridge" and record
another linear trace, following again the *concrete control flow* that happens
now:

```
          guard(a is None) ----> FAIL (side exit)
            /                         \
           /                           \
        a = 0                          pass
           \                             \
            \                             \
    guard(b not None)              guard(b not None)
            /                             /
           /                             /
        b = 0                         b = 0
           \                             \
            \                             \
           ...                           ...

```

Note how `b = 0` is effectively duplicated now. By design, PyPy's JIT *never
merges execution flow*.

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
## Exponential tracing

- Every combination of "`None`ness" must be compiled separately

```
❯ PYPYLOG=jit-summary:- pypy data_driven.py
1.6387 secs
[a625ea04910] {jit-summary
...
Total # of loops:	11
Total # of bridges:	527
...
[a625ea507bc] jit-summary}
```
</div>
<div class="annotation" markdown="1">

Looking inside `PYPYLOG` confirms our theory: we get "exponential
tracing". The JIT has to compile separate optimized code for every unique
combination of which parameters are None and which aren't. With 9 parameters,
that could be up to 512 different combinations!

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
## Exponential tracing

- Mitigation: branchless code

```
if x < 0:
   x = 100
# ===>
x = (x < 0)*100 + (x >= 0)*x
```

- Ugly, unreadable, not always possible

- Never found a good solution

- Happens quite a lot

- *Fundamental problem of tracing JITs*?
</div>
<div class="annotation" markdown="1">

One possible mitigation is to rewrite conditional code to be "branchless" -
using arithmetic tricks instead of if statements. But this makes code ugly and
unreadable, and it's not always possible.

Despite years of working on this, never found a really good solution. This
pattern happens quite a lot, although often is more subtle: in this silly
example all the `if`s are nicely grouped together at the start, but in a long
trace they can be scattered in multiple places, and _any_ kind of control flow
contributes to the problem, not only `if`s. In Python, this includes any kind
of dynamic dispatch, exceptions, etc.

One possible solution for CPython's JIT is to try to merge (some) traces to
avoid or limit the exponentail explosion. However, it is worth underling that
tracing JITs shine precisely when they can optimize a long linear trace: if
you try to compile shorter traces, you might quickly end up in a situation
which is equivalent to the "trace blocker" problem described earlier.

I suspect this might be a fundamental limitation of tracing JITs.
</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 3: generators (and async?)

```python
def count_triples_loop(P):
    """
    Counts how many integer right triangles (Pythagorean triples) have perimeter <= P.
    """
    m_max = int(math.isqrt(2 * P))  # loose but safe upper bound for m
    count = 0
    for m in range(1, m_max + 1):
        for n in range(1, m_max + 1):
            if ((m - n) & 1) and math.gcd(m, n) == 1:
                p0 = 2 * m * (m + n)  # a+b+c
                if p0 > P:
                    continue
                count += P // p0
    return count
```
</div>
<div class="annotation" markdown="1">

#### Annotation

Compared to the other two problems, this is less serious, but it's worth
mentioning because of prevalence of `async` (and thus implicitly generators)
in modern Python.

Here's another silly function that counts Pythagorean triples using nested
loops. This is our baseline "good" version using plain loops.
</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 3: generators (and async?)

```python
def range_product(a, b):
    for i in range(*a):
        for j in range(*b):
            yield i, j

def count_triples_gen(P):
    m_max = int((math.isqrt(2 * P)))
    count = 0
    for m, n in range_product((1, m_max + 1), (1, m_max + 1)):
        if ((m - n) & 1) and math.gcd(m, n) == 1:
            p0 = 2 * m * (m + n)  # a+b+c
            if p0 > P:
                continue
            count += P // p0
    return count
```
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 3: generators (and async?)

```
class RangeProductIter:

    def __init__(self, a, b):
        self.i, self.n = a
        self.j, self.m = b

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        value = (self.i, self.j)
        self.j += 1
        if self.j >= self.m:
            self.j = 0
            self.i += 1
        return value
```
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 3: generators (and async?)

```
❯ python3.13 pythagorean.py
loop: 0.4560 secs (1x)
gen:  0.5884 secs (1.29x)
iter: 1.0126 secs (2.22x)

❯ pypy pythagorean.py
loop: 0.1199 secs (1x)
gen:  0.1550 secs (1.29x)
iter: 0.1264 secs (1.05x)
```

- Generators force to create a frame

- The JIT cannot see "through" generators

- In real code, much worse slowdowns
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
## Other misc problems

- Tooling, profilers

- Warmup

- Performance instability (link to paper?)

- Long tail of jitting

    ```
    for n in itertools.count():
       job = accept_job()
       do(job)
       if n > 12345:
           pypyjit.disable()
    ```
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
## Bonus slides

### (Avoid) allocations is all your need
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Task

- Compute baricenter of a series of triangles serialized according to a binary
  protocol

- Simulate protobuf, capnproto, etc.

```
struct Point {
    double x;
    double y;
};

struct Triangle {
    Point a;
    Point b;
    Point c;
};
```
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Bare loop

```
def read_loop():
    fmt = 'dddddd'
    size = struct.calcsize(fmt)
    tot_x = 0
    tot_y = 0
    n = 0
    with open('poly.bin', 'rb') as f:
        while True:
            buf = f.read(size)
            if not buf:
                break
            points = struct.unpack_from(fmt, buf)
            ax, ay, bx, by, cx, cy = points
            tot_x += (ax + bx + cx)
            tot_y += (ay + by + cy)
            n += 1

    print(n)
    x = tot_x/n
    y = tot_y/n
    return x, y
```
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Schema-aware protocol

```
class Triangle:
    def __init__(self, buf, offset):
        self.buf = buf
        self.offset = offset

    @property
    def a(self):
        return Point(self.buf, 0)

[...]

class Point:
    def __init__(self, buf, offset):
        self.buf = buf
        self.offset = offset

    @property
    def x(self):
        return struct.unpack_from('d', self.buf, self.offset)[0]
```
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Schema-aware protocol

```
        while True:
            buf = f.read(size)
            if not buf:
                break
            t = Triangle(buf, 0)
            tot_x += t.a.x + t.b.x + t.c.x
            tot_y += t.a.y + t.b.y + t.c.y
            n += 1
```
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
```
❯ python3.13 readpoly.py
read_loop:     0.5444 secs
read_proto:    3.0307 secs

❯ pypy readpoly.py
read_loop:     0.2945 secs
read_proto:    0.1183 secs
```
</div>
<div class="annotation" markdown="1">

#### Annotation

</div>
</div>
