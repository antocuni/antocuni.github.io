---
draft: true
date: 2026-03-22
title: "My first OSS commit turns 20 today"
categories:
  - Post
tags:
  - oss
  - pypy
  - spy

---

# My first OSS commit turns 20 today

Around ~1 year ago I realized that it was almost 20 years since I started to contribute
to Open Source. It's easy to remember, because I started to work on PyPy as part of my
Master Thesis and I graduated in 2006.

So, I did a bit of archeology to find the [first commit](https://github.com/pypy/pypy/commit/1a086d45d9):

```autorun
$ cd ~/pypy/pypy && git show --name-only 1a086d45d9
commit 1a086d45d9
Author: Antonio Cuni <anto.cuni@gmail.com>
Date:   Wed Mar 22 14:01:42 2006 +0000

    Initial commit of the CLI backend

pypy/translator/cli/__init__.py
pypy/translator/cli/conftest.py
pypy/translator/cli/cts.py
pypy/translator/cli/function.py
pypy/translator/cli/gencli.py
pypy/translator/cli/ilgenerator.py
pypy/translator/cli/test/__init__.py
pypy/translator/cli/test/compile.py
pypy/translator/cli/test/runtest.py
pypy/translator/cli/test/test_flow.py
```

<!-- more -->
