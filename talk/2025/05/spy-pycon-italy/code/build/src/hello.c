#include "hello.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/talks/2025/05/spy-pycon-italy/code/build/src/hello.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/pypy/misc/antocuni.github.io/blog/talks/2025/05/spy-pycon-italy/code/hello.spy"
#endif

// constants and globals
static spy_Str SPY_g_str0 = {11, "Hello world"};

// content of the module

int main(void) {
    spy_hello$main();
    return 0;
}
#line SPY_LINE(3, 18)
int32_t spy_hello$add(int32_t x, int32_t y) {
    return x + y;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(6, 23)
void spy_hello$main(void) {
    spy_builtins$print_str(&SPY_g_str0 /* 'Hello world' */);
    spy_builtins$print_i32(spy_hello$add(40, 2));
}
