#include "hello.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/posts/2026/03-spy-semantics/autorun/build/src/hello.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/pypy/misc/antocuni.github.io/blog/posts/2026/03-spy-semantics/autorun/hello.spy"
#endif

// constants and globals
static spy_Str SPY_g_str0 = {12, 0, "Hello world!"};

// content of the module

int main(void) {
    spy_hello$main();
    return 0;
}
#line SPY_LINE(1, 18)
void spy_hello$main(void) {
    spy_builtins$print_str(&SPY_g_str0 /* 'Hello world!' */);
}
