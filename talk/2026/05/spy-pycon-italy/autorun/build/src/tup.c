#include "tup.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/talk/2026/05/spy-pycon-italy/autorun/build/src/tup.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/pypy/misc/antocuni.github.io/blog/talk/2026/05/spy-pycon-italy/autorun/tup.spy"
#endif

// constants and globals

// content of the module

int main(void) {
    spy_tup$main();
    return 0;
}
#line SPY_LINE(1, 18)
spy__tuple$tuple__builtins$i32_builtins$i32$_tup spy_tup$get_point(void) {
    return (spy__tuple$tuple__builtins$i32_builtins$i32$_tup){ 10, 20 };
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(4, 23)
void spy_tup$main(void) {
    int32_t x;
    int32_t y;
    #line SPY_LINE(5, 27)
    {
        spy__tuple$tuple__builtins$i32_builtins$i32$_tup tmp = spy_tup$get_point();
        x = tmp._item0;
        y = tmp._item1;
    }
    #line SPY_LINE(6, 33)
    spy__print$println__builtins$i32$p(x);
    spy__print$println__builtins$i32$p(y);
}
