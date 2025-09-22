---
draft: true
date: 2025-09-23
title: "Tracing JIT and real world Python"
categories:
  - Post
tags:
  - mkdocs

---

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

# Tracing JIT and real world Python

Last week I participated to the annual CPython core dev sprint in Cambridge.

One the first day I presented a talk titled "Tracing JIT and real world
Python". This is an annotated version of the slides.

<!-- more -->

<div class="slide-container" markdown="1">
<div class="slide" markdown="1">

# Motivation

- CPython's JIT has a lot in common with PyPy

- "Optimize for PyPy" ==> my job for ~7 years

- Real world code != pyperformance

- Challenges & lesson learned

</div>
<div class="annotation" markdown="1">

#### My commentary on this slide

You can write your annotations here. This slide introduces the motivation for the talk. The key point is that optimizing for PyPy over 7 years has given me insights that are now relevant to CPython's new JIT implementation.

</div>
</div>
