---
draft: true
date: 2026-05-01
title: "Why Python Is Slow: Talking about SPy on the Behind the Commit Podcast"
categories:
  - Post
tags:
  - spy
og:
  description: ""
  image: "og.jpg"
  author: "Antonio Cuni"

---

# Why Python Is Slow: Talking about SPy on the Behind the Commit Podcast

During EuroPython 2025 I had the pleasure to talk to [Mia Bajić](https://miabajic.dev/) for her podcast [Behind The Commit](https://www.youtube.com/@BehindtheCommit).

In the chat we mainly talk about Python performance and how SPy tries to improve them.

Now the full episode is live: you can [watch it on Youtube](https://www.youtube.com/watch?v=CV2tYMPmMWc&t=708s) or [listen on Spotify](https://open.spotify.com/episode/52oMn2JxF9JlwwE0tx1vjF?si=xGGoEcvUQBK2SH2XLV2EOw)

<!-- more -->

## One year of progress in SPy

Almost one year passed since then and it was fun to watch it knowing what happened since
then.  In particular, during the interview I often reply things like "this is not done
yet", "this will be implemented", etc., but many of the things we talked about **were
implemented** in the meantime, so this becomes a very good summary of what happened in
the last year of SPy.

Here is a list of quotes, with the relevant links.

---

[`00:52`](https://youtu.be/CV2tYMPmMWc?si=HXJAT6NXbOLf6ncR&t=52)

> _Mia_: Why is Python so slow?
>
> _Anto_: Oh, that's exactly the talk which I just gave

Here we are talking about my EuroPython talk *Myths and fairy tales around Python performance*: [video](https://www.youtube.com/watch?v=X3QbMaEIpt0) and [slides](https://antocuni.eu/talk/2025/07/europython-myths-and-fairy-tales/).

---

[`08:52`](https://youtu.be/CV2tYMPmMWc?si=7fGc2Wgc2tXI9DV_&t=532)

> _Mia_: Can you use decorators in SPy?
>
> _Anto_: Not yet

Now decorators are supported! [PR 225](https://github.com/spylang/spy/pull/225) was
merged on Sep 10, a just a few weeks after the interview.

---

[`10:32`](https://youtu.be/CV2tYMPmMWc?si=lPM7FjWV7RZJuA8Q&t=632)

> What is the current roadmap of SPy?

We we have a (very rough) roadmap which is visible [here](https://github.com/spylang/spy/blob/main/ROADMAP.md)

---

[`11:25`](https://youtu.be/CV2tYMPmMWc?si=lPM7FjWV7RZJuA8Q&t=685)

> So what I have so far is that this low-level core is mostly done or very in a very
> good shape and now I can start building my own abstractions, which means for example
> that I don't have list type in SPy.

This has been a long-running joke about the state of SPy, because I used to say "I don't
even have lists and dicts!".  The point is that I wanted to have enough low-level
features to be able to implement
[`list`](https://github.com/spylang/spy/blob/main/stdlib/_list.spy) and
[`dict`](https://github.com/spylang/spy/blob/main/stdlib/_dict.spy) directly in SPy. Now
we have both!

---

[`21:38`](https://youtu.be/CV2tYMPmMWc?si=lPM7FjWV7RZJuA8Q&t=1298)

> Currently SPy is a garbage-uncollected language

That's no longer the case! We have a proper GC since [PR
390](https://github.com/spylang/spy/pull/390). This is still suboptimal and I plan to
integrate better GCs in the future. but for now it's good enouogh.

---

[`24:54`](https://youtu.be/CV2tYMPmMWc?si=lPM7FjWV7RZJuA8Q&t=1494)

> Documentation is inexistent

[Here it is](https://spylang.github.io/docs/dev/)! We went from "inexistent" to
"scarce", I call it progress! :)

This is entirely merit of members of the SPy community who did all the hard work, in
particular (Jeff Glass)[https://github.com/JeffersGlass] and [Kanin
Kearpimy](https://github.com/kanin-kearpimy).

---

[`25:01`](https://youtu.be/CV2tYMPmMWc?si=lPM7FjWV7RZJuA8Q&t=1501)

> I plan to write a series of blog post to explain the motivation and
> technicalities of SPy

Readers of this blog already know about these:

- [Inside SPy, part 1: Motivations and Goals](https://antocuni.eu/2025/10/29/inside-spy-part-1-motivations-and-goals/)

- [Inside SPy, part 2: Language Semantics](https://antocuni.eu/2026/03/25/inside-spy-part-2-language-semantics/)
