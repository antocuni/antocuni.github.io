#include "_tuple.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/talk/2026/05/spy-pycon-italy/autorun/build/src/_tuple.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/anaconda/spy/stdlib/_tuple.spy"
#endif

// constants and globals

// content of the module

#line SPY_LINE(34, 14)
int32_t spy__tuple$tuple__builtins$i32_builtins$i32$_tup$__len__(spy__tuple$tuple__builtins$i32_builtins$i32$_tup self) {
    return 2;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 19)
bool spy__tuple$tuple__builtins$i32_builtins$i32$_tup$__eq__(spy__tuple$tuple__builtins$i32_builtins$i32$_tup a, spy__tuple$tuple__builtins$i32_builtins$i32$_tup b) {
    spy__tuple$tuple__builtins$i32_builtins$i32$_tup $v0;
    int32_t $v1;
    spy__tuple$tuple__builtins$i32_builtins$i32$_tup $v2;
    int32_t $v3;
    spy__tuple$tuple__builtins$i32_builtins$i32$_tup $v4;
    int32_t $v5;
    spy__tuple$tuple__builtins$i32_builtins$i32$_tup $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    #line SPY_LINE(31, 31)
    $v0 = a;
    #line SPY_LINE(31, 33)
    $v1 = $v0._item0;
    #line SPY_LINE(31, 35)
    $v2 = b;
    #line SPY_LINE(31, 37)
    $v3 = $v2._item0;
    #line SPY_LINE(171, 39)
    $v9 = $v1 == $v3;
    #line SPY_LINE(31, 41)
    if ($v9){
        #line SPY_LINE(31, 43)
        $v4 = a;
        #line SPY_LINE(31, 45)
        $v5 = $v4._item1;
        #line SPY_LINE(31, 47)
        $v6 = b;
        #line SPY_LINE(31, 49)
        $v7 = $v6._item1;
        #line SPY_LINE(31, 51)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(31, 54)
        $v8 = $v9;
    }
    #line SPY_LINE(165, 57)
    return $v8;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 61)
bool spy__tuple$tuple__builtins$i32_builtins$i32$_tup$__ne__(spy__tuple$tuple__builtins$i32_builtins$i32$_tup a, spy__tuple$tuple__builtins$i32_builtins$i32$_tup b) {
    spy__tuple$tuple__builtins$i32_builtins$i32$_tup $v0;
    int32_t $v1;
    spy__tuple$tuple__builtins$i32_builtins$i32$_tup $v2;
    int32_t $v3;
    spy__tuple$tuple__builtins$i32_builtins$i32$_tup $v4;
    int32_t $v5;
    spy__tuple$tuple__builtins$i32_builtins$i32$_tup $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    bool $v10;
    #line SPY_LINE(31, 74)
    $v0 = a;
    #line SPY_LINE(31, 76)
    $v1 = $v0._item0;
    #line SPY_LINE(31, 78)
    $v2 = b;
    #line SPY_LINE(31, 80)
    $v3 = $v2._item0;
    #line SPY_LINE(171, 82)
    $v9 = $v1 == $v3;
    #line SPY_LINE(31, 84)
    if ($v9){
        #line SPY_LINE(31, 86)
        $v4 = a;
        #line SPY_LINE(31, 88)
        $v5 = $v4._item1;
        #line SPY_LINE(31, 90)
        $v6 = b;
        #line SPY_LINE(31, 92)
        $v7 = $v6._item1;
        #line SPY_LINE(31, 94)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(31, 97)
        $v8 = $v9;
    }
    #line SPY_LINE(31, 100)
    $v10 = $v8;
    #line SPY_LINE(165, 102)
    return spy_operator$bool_not($v10);
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(47, 106)
int32_t spy__tuple$tuple__builtins$i32_builtins$i32$_tup$__getitem__$get(spy__tuple$tuple__builtins$i32_builtins$i32$_tup self) {
    #line SPY_LINE(49, 108)
    return self._item0;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(47, 112)
int32_t spy__tuple$tuple__builtins$i32_builtins$i32$_tup$__getitem__$get$1(spy__tuple$tuple__builtins$i32_builtins$i32$_tup self) {
    #line SPY_LINE(49, 114)
    return self._item1;
    abort(); /* reached the end of the function without a `return` */
}
