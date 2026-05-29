#include "_list.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/talk/2026/05/spy-pycon-italy/autorun/build/src/_list.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/anaconda/spy/stdlib/_list.spy"
#endif

// constants and globals
static spy_StrObject SPY_g_str0 = SPY_STR_LITERAL(10, "ValueError");
static spy_StrObject SPY_g_str1 = SPY_STR_LITERAL(25, "slice step cannot be zero");
static spy_StrObject SPY_g_str2 = SPY_STR_LITERAL(45, "/home/antocuni/anaconda/spy/stdlib/_slice.spy");

// content of the module

#line SPY_LINE(399, 14)
int32_t spy__list$_py_adjust_indexes(int32_t length, int32_t start, int32_t stop, int32_t step) {
    int32_t val;
    #line SPY_LINE(405, 17)
    if (start < 0){
        start = start + length;
        if (start < 0){
            if (step < 0){
                start = -1;
            } else {
                start = 0;
            }
        }
    } else {
        #line SPY_LINE(412, 28)
        if (start >= length){
            if (step < 0){
                start = length - 1;
            } else {
                start = length;
            }
        }
    }
    #line SPY_LINE(418, 37)
    if (stop < 0){
        stop = stop + length;
        if (stop < 0){
            if (step < 0){
                stop = -1;
            } else {
                stop = 0;
            }
        }
    } else {
        #line SPY_LINE(425, 48)
        if (stop >= length){
            if (step < 0){
                stop = length - 1;
            } else {
                stop = length;
            }
        }
    }
    #line SPY_LINE(431, 57)
    val = 0;
    if (step < 0){
        if (stop < start){
            val = spy_operator$f64_to_i32(spy_operator$i32_div(start - stop - 1, -step)) + 1;
        }
    } else {
        #line SPY_LINE(436, 64)
        if (start < stop){
            val = spy_operator$f64_to_i32(spy_operator$i32_div(stop - start - 1, step)) + 1;
        }
    }
    #line SPY_LINE(439, 69)
    return val;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(442, 73)
spy__slice$tuple3 spy__list$_py_slice_unpack(int32_t length, spy__slice$Slice s) {
    int32_t _start;
    int32_t _stop;
    int32_t _step;
    spy__slice$Slice $v0;
    int32_t $v1;
    spy__slice$Slice $v2;
    int32_t $v3;
    spy__slice$Slice $v4;
    int32_t $v5;
    #line SPY_LINE(443, 84)
    #line SPY_LINE(444, 85)
    #line SPY_LINE(445, 86)
    #line SPY_LINE(446, 87)
    $v0 = s;
    #line SPY_LINE(446, 89)
    $v1 = $v0.step_is_none;
    #line SPY_LINE(446, 91)
    if (spy_operator$i32_to_bool($v1)){
        _step = 1;
    } else {
        _step = s.step;
    }
    if (_step == 0){
        spy_operator$raise(&SPY_g_str0 /* 'ValueError' */, &SPY_g_str1 /* 'slice step ca...' */, &SPY_g_str2 /* '/home/antocun...' */, 123);
    }
    $v2 = s;
    #line SPY_LINE(454, 101)
    $v3 = $v2.start_is_none;
    #line SPY_LINE(454, 103)
    if (spy_operator$i32_to_bool($v3)){
        if (_step < 0){
            _start = 2147483647;
        } else {
            _start = 0;
        }
    } else {
        #line SPY_LINE(460, 111)
        _start = s.start;
    }
    $v4 = s;
    #line SPY_LINE(462, 115)
    $v5 = $v4.stop_is_none;
    #line SPY_LINE(462, 117)
    if (spy_operator$i32_to_bool($v5)){
        if (_step < 0){
            _stop = -2147483648;
        } else {
            _stop = 2147483647;
        }
    } else {
        #line SPY_LINE(468, 125)
        _stop = s.stop;
    }
    return (spy__slice$tuple3){ _start, _stop, _step };
    abort(); /* reached the end of the function without a `return` */
}
