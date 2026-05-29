#include "_print.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/talk/2026/05/spy-pycon-italy/autorun/build/src/_print.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/anaconda/spy/stdlib/_print.spy"
#endif

// constants and globals
static spy_StrObject SPY_g_str0 = SPY_STR_LITERAL(1, "\x0a");

// content of the module

#line SPY_LINE(46, 14)
void spy__print$println__builtins$i32$p(int32_t x) {
    int32_t $v0;
    spy_StrObject * $v1;
    #line SPY_LINE(47, 18)
    $v0 = x;
    #line SPY_LINE(47, 20)
    $v1 = spy_builtins$i32$__str__($v0);
    #line SPY_LINE(47, 22)
    spy___spy__$_stdout_write($v1);
    spy___spy__$_stdout_write(&SPY_g_str0 /* '\n' */);
}
