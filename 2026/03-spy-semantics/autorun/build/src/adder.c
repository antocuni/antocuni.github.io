#include "adder.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/posts/2026/03-spy-semantics/autorun/build/src/adder.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/pypy/misc/antocuni.github.io/blog/posts/2026/03-spy-semantics/autorun/adder.spy"
#endif

// constants and globals

// content of the module

int main(void) {
    spy_adder$main();
    return 0;
}
#line SPY_LINE(4, 18)
int32_t spy_adder$make_adder$add(int32_t x) {
    return x + 5;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(4, 23)
int32_t spy_adder$make_adder$add$1(int32_t x) {
    return x + 7;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(12, 28)
void spy_adder$main(void) {
    #line SPY_LINE(14, 30)
    spy_builtins$print_i32(spy_adder$make_adder$add(10));
    spy_builtins$print_i32(spy_adder$make_adder$add$1(10));
    spy_builtins$print_i32(spy_adder$make_adder$add$2(10));
    #line SPY_LINE(19, 34)
    spy_builtins$print_i32(spy_adder$make_adder$add(10));
}
#line SPY_LINE(4, 37)
int32_t spy_adder$make_adder$add$2(int32_t x) {
    return x + 9;
    abort(); /* reached the end of the function without a `return` */
}
