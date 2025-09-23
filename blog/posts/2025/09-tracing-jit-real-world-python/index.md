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
}

.slide {
  padding: 2em;
  background: white;
  border-radius: 6px 6px 0 0;
  border-bottom: 2px solid #eee;
}

.slide h1, .slide h2, .slide h3 {
  margin-top: 0;
  color: #333;
}

.annotation {
  padding: 1.5em;
  background: #f9f9f9;
  font-style: italic;
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

#### Annotation

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

#### Annotation

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

#### Annotation

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

#### Annotation

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

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 1: trace blockers



```python [1-100]
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

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 1: trace blockers



```python [18]
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
        hic_sunt_leones() # the JIT cannot enter here

    return 4 * pi_approx
```
</div>
<div class="annotation" markdown="1">

#### Annotation

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

#### Annotation

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

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 2: data driven control flow

```
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

#### Annotation

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

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
## Exponential tracing

- Every combination of "`None`ness" must be compiled separately

```
❯ PYPYLOG=jit-summary:- pypy jit_explosion.py
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

#### Annotation

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

#### Annotation

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 3: generators (and async?)

```
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

</div>
</div>

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">
### Problem 3: generators (and async?)

```
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
