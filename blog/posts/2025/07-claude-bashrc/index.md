---
draft: false
date: 2025-07-07
title: "Claude code modified my .bashrc without asking?"
categories:
  - Post
tags:
  - claude

---

# Claude code modified my .bashrc without asking?

!!! note "Note"
    This is not the classical post about running `claude` in
    YOLO mode and then complaining that it damaged the system. I have reasons
    to think that `claude` automatically modified my `.bashrc` without asking
    my permission and without notifying me of the change.

<!-- more -->

I'm not a huge fan of AI-assisted coding, but I occasionally use claude code.

Today I started `claude` for the first time after weeks, and it notified me
about automatically updating to the latest version (which I believe is
1.0.43). I didn't pay particular attention to the update, and then I did a
productive session of vibe coding which resulted into a nice
[SPy PR](https://github.com/spylang/spy/pull/194).

Later today I returned to my computer and noticed that my `~/.bashrc` (which I
keep in a git repo) had been modified. This is the diff:

```diff
diff --git a/dotfiles/bashrc b/dotfiles/bashrc
index 6e9fd68..6a1fb30 100644
--- a/dotfiles/bashrc
+++ b/dotfiles/bashrc
@@ -107,7 +107,6 @@ alias dmesg="dmesg --human"
 alias ddmesg="/bin/dmesg"

 alias xs='xdg-open'
-alias claude='claude-logging'

 #alias hg="/usr/bin/python -s -E `which hg`" # else hg it's awfully slow to start
 alias mcd='mount /mnt/cdrom'
```

So, apparently "someone" decided that I should alias `claude` to something
else. And I am 100% sure that I didn't do that change.

!!! note "What is `claude-logging`?"
    [claude-logging](https://github.com/antocuni/claude-logging/) is a little
    tool which I wrote some months ago, when `claude` didn't have a builtin
    logging mechanism yet. It uses `script` to record all the characters which
    have been sent to the terminal.  Nowadays there are probably better tools
    to achieve the same goal, but that's not the point of course.

## Investigating

At first, I checked the modification time of `~/.bashrc`:

```
❯ ls -l ~/.bashrc
lrwxrwxrwx 1 antocuni antocuni 34 apr 28  2021 /home/antocuni/.bashrc -> /home/antocuni/env/dotfiles/bashrc

❯ ls -l /home/antocuni/env/dotfiles/bashrc
-rw-rw-r-- 1 antocuni antocuni 8728 lug  7 17:59 /home/antocuni/env/dotfiles/bashrc
```

So, it was modified today at 17:59, which is exactly the time at which I
started `claude`. Suspicious.

Then, I tried to seach for the string `.bashrc` inside the `claude` minified
JS binary:

```
❯ cd /home/antocuni/.nvm/versions/node/v23.8.0/lib/node_modules/@anthropic-ai/claude-code/


❯ npx prettier cli.js | grep -n -C 10 bashrc
303354-    }
303355-  }
303356-  return A;
303357-}
303358-var t2Q = 1800000,
303359-  Cu1 = "\\";
303360-function yU0(A) {
303361-  let B = A.includes("zsh")
303362-    ? ".zshrc"
303363-    : A.includes("bash")
303364:      ? ".bashrc"
303365-      : ".profile";
303366-  return o2Q(i2Q(), B);
303367-}
303368-function e2Q(A, B) {
303369-  let Q = yU0(A),
303370-    D = Q.endsWith(".zshrc"),
303371-    I = "";
303372-  if (D)
303373-    I = `
303374-      echo "# Functions" >> $SNAPSHOT_FILE
--
339189-import { join as Gp } from "path";
339190-import { join as p01 } from "path";
339191-import { execFile as d_6 } from "child_process";
339192-import { homedir as Qw1 } from "os";
339193-import { join as N9A } from "path";
339194-var sf2 = /^\s*alias\s+claude=/;
339195-function Rk() {
339196-  let A = process.env.ZDOTDIR || Qw1();
339197-  return {
339198-    zsh: N9A(A, ".zshrc"),
339199:    bash: N9A(Qw1(), ".bashrc"),
339200-    fish: N9A(Qw1(), ".config/fish/config.fish"),
339201-  };
339202-}
339203-function ec(A) {
339204-  let B = !1;
339205-  return {
339206-    filtered: A.filter((D) => {
339207-      if (sf2.test(D)) return ((B = !0), !1);
339208-      return !0;
339209-    }),
```

I surely don't want to try to reverse engineer this code, but again it seems
very suspicious. Note in particular line 339194, which contains a regex to
find strings like `alias claude=`.

The final thing which I did was to revert my `.bashrc` to its original state,
and try to run `claude` again. This time, it didn't modify the file. Maybe the
logic is triggered only when there is an update?

## Conclusion

I don't know for sure whether `claude` modified my `.bashrc` during the
update, but I think that my investigation above shows that it's a very
reasonable hypothesis.

Personally, I find this completely unacceptable: it would be fine if claude
detected the alias and suggested an auto-fix, but modifying it automatically
*without telling me* crosses a line.
