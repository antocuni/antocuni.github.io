---
date: 2010-12-14 16:45:00
title: "PyPy migrates to Mercurial"
author: "Antonio Cuni"
categories:
  - Post

tags:
  - pypy
---

!!! note ""
    Originally published on the [PyPy blog](https://pypy.org/posts/2010/12/pypy-migrates-to-mercurial-3308736161543832134.html).


<html><body><p>The assiduous readers of this blog surely remember that during the last
<a class="reference external" href="/posts/2010/10/dusseldorf-sprint-report-2010-371223200425847723.html">Düsseldorf sprint</a> in October, we started the process for migrating our main
development repository from Subversion to Mercurial.  Today, after more than
two months, the process has finally been completed :-).
</p>
<!-- more -->

<p>The new official PyPy repository is hosted on <a class="reference external" href="https://bitbucket.org/pypy/pypy">BitBucket</a>.</p>
<p>The migration has been painful because the SVN history of PyPy was a mess and
none of the existing conversion tools could handle it correctly.  This was
partly because PyPy started when subversion was still at version 0.9 when some
best-practices were still to be established, and partly because we probably
managed to invent all the possible ways to do branches (and even some of the
impossible ones: there is at least one commit which you cannot do with the
plain SVN client but you have to speak to the server by yourself :-)).</p>
<p>The actual conversion was possible thanks to the enormous work done by Ronny
Pfannschmidt and his <a class="reference external" href="https://bitbucket.org/RonnyPfannschmidt/hackbeil">hackbeil</a> tool. I would like to personally thank Ronny
for his patience to handle all the various requests we asked for.</p>
<p>We hope that PyPy development becomes even more approachable now, at least from
a version control point of view.</p></body></html>