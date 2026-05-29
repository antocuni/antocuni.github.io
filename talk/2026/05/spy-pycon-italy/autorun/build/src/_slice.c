#include "_slice.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/talk/2026/05/spy-pycon-italy/autorun/build/src/_slice.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/anaconda/spy/stdlib/_slice.spy"
#endif

// constants and globals
static spy_StrObject SPY_g_str0 = SPY_STR_LITERAL(10, "ValueError");
static spy_StrObject SPY_g_str1 = SPY_STR_LITERAL(25, "slice step cannot be zero");
static spy_StrObject SPY_g_str2 = SPY_STR_LITERAL(45, "/home/antocuni/anaconda/spy/stdlib/_slice.spy");
static spy_StrObject SPY_g_str3 = SPY_STR_LITERAL(10, "ValueError");
static spy_StrObject SPY_g_str4 = SPY_STR_LITERAL(29, "length should not be negative");
static spy_StrObject SPY_g_str5 = SPY_STR_LITERAL(45, "/home/antocuni/anaconda/spy/stdlib/_slice.spy");

// content of the module

#line SPY_LINE(165, 14)
bool spy__slice$tuple3$__eq__(spy__slice$tuple3 a, spy__slice$tuple3 b) {
    spy__slice$tuple3 $v0;
    int32_t $v1;
    spy__slice$tuple3 $v2;
    int32_t $v3;
    spy__slice$tuple3 $v4;
    int32_t $v5;
    spy__slice$tuple3 $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    spy__slice$tuple3 $v10;
    int32_t $v11;
    spy__slice$tuple3 $v12;
    int32_t $v13;
    bool $v14;
    #line SPY_LINE(36, 31)
    $v0 = a;
    #line SPY_LINE(36, 33)
    $v1 = $v0.start;
    #line SPY_LINE(36, 35)
    $v2 = b;
    #line SPY_LINE(36, 37)
    $v3 = $v2.start;
    #line SPY_LINE(171, 39)
    $v9 = $v1 == $v3;
    #line SPY_LINE(37, 41)
    if ($v9){
        #line SPY_LINE(37, 43)
        $v4 = a;
        #line SPY_LINE(37, 45)
        $v5 = $v4.stop;
        #line SPY_LINE(37, 47)
        $v6 = b;
        #line SPY_LINE(37, 49)
        $v7 = $v6.stop;
        #line SPY_LINE(37, 51)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(37, 54)
        $v8 = $v9;
    }
    #line SPY_LINE(38, 57)
    if ($v8){
        #line SPY_LINE(38, 59)
        $v10 = a;
        #line SPY_LINE(38, 61)
        $v11 = $v10.step;
        #line SPY_LINE(38, 63)
        $v12 = b;
        #line SPY_LINE(38, 65)
        $v13 = $v12.step;
        #line SPY_LINE(38, 67)
        $v14 = $v11 == $v13;
    } else {
        #line SPY_LINE(38, 70)
        $v14 = $v8;
    }
    #line SPY_LINE(165, 73)
    return $v14;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 77)
bool spy__slice$tuple3$__ne__(spy__slice$tuple3 a, spy__slice$tuple3 b) {
    spy__slice$tuple3 $v0;
    int32_t $v1;
    spy__slice$tuple3 $v2;
    int32_t $v3;
    spy__slice$tuple3 $v4;
    int32_t $v5;
    spy__slice$tuple3 $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    spy__slice$tuple3 $v10;
    int32_t $v11;
    spy__slice$tuple3 $v12;
    int32_t $v13;
    bool $v14;
    bool $v15;
    #line SPY_LINE(36, 95)
    $v0 = a;
    #line SPY_LINE(36, 97)
    $v1 = $v0.start;
    #line SPY_LINE(36, 99)
    $v2 = b;
    #line SPY_LINE(36, 101)
    $v3 = $v2.start;
    #line SPY_LINE(171, 103)
    $v9 = $v1 == $v3;
    #line SPY_LINE(37, 105)
    if ($v9){
        #line SPY_LINE(37, 107)
        $v4 = a;
        #line SPY_LINE(37, 109)
        $v5 = $v4.stop;
        #line SPY_LINE(37, 111)
        $v6 = b;
        #line SPY_LINE(37, 113)
        $v7 = $v6.stop;
        #line SPY_LINE(37, 115)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(37, 118)
        $v8 = $v9;
    }
    #line SPY_LINE(38, 121)
    if ($v8){
        #line SPY_LINE(38, 123)
        $v10 = a;
        #line SPY_LINE(38, 125)
        $v11 = $v10.step;
        #line SPY_LINE(38, 127)
        $v12 = b;
        #line SPY_LINE(38, 129)
        $v13 = $v12.step;
        #line SPY_LINE(38, 131)
        $v14 = $v11 == $v13;
    } else {
        #line SPY_LINE(38, 134)
        $v14 = $v8;
    }
    #line SPY_LINE(38, 137)
    $v15 = $v14;
    #line SPY_LINE(165, 139)
    return spy_operator$bool_not($v15);
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(118, 143)
spy__slice$tuple3 spy__slice$Slice$indices(spy__slice$Slice self, int32_t length) {
    int32_t _step;
    int32_t _lower;
    int32_t _upper;
    int32_t _start;
    int32_t _stop;
    spy__slice$Slice $v0;
    int32_t $v1;
    spy__slice$Slice $v2;
    int32_t $v3;
    spy__slice$Slice $v4;
    int32_t $v5;
    #line SPY_LINE(119, 156)
    _step = 1;
    $v0 = self;
    #line SPY_LINE(120, 159)
    $v1 = $v0.step_is_none;
    #line SPY_LINE(120, 161)
    if (spy_operator$bool_not(spy_operator$i32_to_bool($v1))){
        _step = self.step;
    }
    #line SPY_LINE(122, 165)
    if (_step == 0){
        spy_operator$raise(&SPY_g_str0 /* 'ValueError' */, &SPY_g_str1 /* 'slice step ca...' */, &SPY_g_str2 /* '/home/antocun...' */, 123);
    }
    if (length < 0){
        spy_operator$raise(&SPY_g_str3 /* 'ValueError' */, &SPY_g_str4 /* 'length should...' */, &SPY_g_str5 /* '/home/antocun...' */, 126);
    }
    #line SPY_LINE(129, 172)
    _lower = 0;
    if (_step < 0){
        _lower = -1;
    }
    #line SPY_LINE(132, 177)
    _upper = length;
    if (_step < 0){
        _upper = length - 1;
    }
    #line SPY_LINE(137, 182)
    _start = 0;
    $v2 = self;
    #line SPY_LINE(138, 185)
    $v3 = $v2.start_is_none;
    #line SPY_LINE(138, 187)
    if (spy_operator$i32_to_bool($v3)){
        if (_step < 0){
            _start = _upper;
        } else {
            _start = _lower;
        }
    } else {
        #line SPY_LINE(144, 195)
        _start = self.start;
        if (_start < 0){
            _start = spy_builtins$max(_start + length, _lower);
        } else {
            _start = spy_builtins$min(_start, _upper);
        }
    }
    _stop = 0;
    $v4 = self;
    #line SPY_LINE(152, 205)
    $v5 = $v4.stop_is_none;
    #line SPY_LINE(152, 207)
    if ($v5 != 0){
        if (_step < 0){
            _stop = _lower;
        } else {
            _stop = _upper;
        }
    } else {
        #line SPY_LINE(158, 215)
        _stop = self.stop;
        if (_stop < 0){
            _stop = spy_builtins$max(_stop + length, _lower);
        } else {
            _stop = spy_builtins$min(_stop, _upper);
        }
    }
    #line SPY_LINE(164, 223)
    return (spy__slice$tuple3){ _start, _stop, _step };
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 227)
bool spy__slice$Slice$__eq__(spy__slice$Slice a, spy__slice$Slice b) {
    spy__slice$Slice $v0;
    int32_t $v1;
    spy__slice$Slice $v2;
    int32_t $v3;
    spy__slice$Slice $v4;
    int32_t $v5;
    spy__slice$Slice $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    spy__slice$Slice $v10;
    int32_t $v11;
    spy__slice$Slice $v12;
    int32_t $v13;
    bool $v14;
    spy__slice$Slice $v15;
    int32_t $v16;
    spy__slice$Slice $v17;
    int32_t $v18;
    bool $v19;
    spy__slice$Slice $v20;
    int32_t $v21;
    spy__slice$Slice $v22;
    int32_t $v23;
    bool $v24;
    spy__slice$Slice $v25;
    int32_t $v26;
    spy__slice$Slice $v27;
    int32_t $v28;
    bool $v29;
    #line SPY_LINE(43, 259)
    $v0 = a;
    #line SPY_LINE(43, 261)
    $v1 = $v0.start;
    #line SPY_LINE(43, 263)
    $v2 = b;
    #line SPY_LINE(43, 265)
    $v3 = $v2.start;
    #line SPY_LINE(171, 267)
    $v9 = $v1 == $v3;
    #line SPY_LINE(44, 269)
    if ($v9){
        #line SPY_LINE(44, 271)
        $v4 = a;
        #line SPY_LINE(44, 273)
        $v5 = $v4.start_is_none;
        #line SPY_LINE(44, 275)
        $v6 = b;
        #line SPY_LINE(44, 277)
        $v7 = $v6.start_is_none;
        #line SPY_LINE(44, 279)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(44, 282)
        $v8 = $v9;
    }
    #line SPY_LINE(45, 285)
    if ($v8){
        #line SPY_LINE(45, 287)
        $v10 = a;
        #line SPY_LINE(45, 289)
        $v11 = $v10.stop;
        #line SPY_LINE(45, 291)
        $v12 = b;
        #line SPY_LINE(45, 293)
        $v13 = $v12.stop;
        #line SPY_LINE(45, 295)
        $v14 = $v11 == $v13;
    } else {
        #line SPY_LINE(45, 298)
        $v14 = $v8;
    }
    #line SPY_LINE(46, 301)
    if ($v14){
        #line SPY_LINE(46, 303)
        $v15 = a;
        #line SPY_LINE(46, 305)
        $v16 = $v15.stop_is_none;
        #line SPY_LINE(46, 307)
        $v17 = b;
        #line SPY_LINE(46, 309)
        $v18 = $v17.stop_is_none;
        #line SPY_LINE(46, 311)
        $v19 = $v16 == $v18;
    } else {
        #line SPY_LINE(46, 314)
        $v19 = $v14;
    }
    #line SPY_LINE(47, 317)
    if ($v19){
        #line SPY_LINE(47, 319)
        $v20 = a;
        #line SPY_LINE(47, 321)
        $v21 = $v20.step;
        #line SPY_LINE(47, 323)
        $v22 = b;
        #line SPY_LINE(47, 325)
        $v23 = $v22.step;
        #line SPY_LINE(47, 327)
        $v24 = $v21 == $v23;
    } else {
        #line SPY_LINE(47, 330)
        $v24 = $v19;
    }
    #line SPY_LINE(48, 333)
    if ($v24){
        #line SPY_LINE(48, 335)
        $v25 = a;
        #line SPY_LINE(48, 337)
        $v26 = $v25.step_is_none;
        #line SPY_LINE(48, 339)
        $v27 = b;
        #line SPY_LINE(48, 341)
        $v28 = $v27.step_is_none;
        #line SPY_LINE(48, 343)
        $v29 = $v26 == $v28;
    } else {
        #line SPY_LINE(48, 346)
        $v29 = $v24;
    }
    #line SPY_LINE(165, 349)
    return $v29;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 353)
bool spy__slice$Slice$__ne__(spy__slice$Slice a, spy__slice$Slice b) {
    spy__slice$Slice $v0;
    int32_t $v1;
    spy__slice$Slice $v2;
    int32_t $v3;
    spy__slice$Slice $v4;
    int32_t $v5;
    spy__slice$Slice $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    spy__slice$Slice $v10;
    int32_t $v11;
    spy__slice$Slice $v12;
    int32_t $v13;
    bool $v14;
    spy__slice$Slice $v15;
    int32_t $v16;
    spy__slice$Slice $v17;
    int32_t $v18;
    bool $v19;
    spy__slice$Slice $v20;
    int32_t $v21;
    spy__slice$Slice $v22;
    int32_t $v23;
    bool $v24;
    spy__slice$Slice $v25;
    int32_t $v26;
    spy__slice$Slice $v27;
    int32_t $v28;
    bool $v29;
    bool $v30;
    #line SPY_LINE(43, 386)
    $v0 = a;
    #line SPY_LINE(43, 388)
    $v1 = $v0.start;
    #line SPY_LINE(43, 390)
    $v2 = b;
    #line SPY_LINE(43, 392)
    $v3 = $v2.start;
    #line SPY_LINE(171, 394)
    $v9 = $v1 == $v3;
    #line SPY_LINE(44, 396)
    if ($v9){
        #line SPY_LINE(44, 398)
        $v4 = a;
        #line SPY_LINE(44, 400)
        $v5 = $v4.start_is_none;
        #line SPY_LINE(44, 402)
        $v6 = b;
        #line SPY_LINE(44, 404)
        $v7 = $v6.start_is_none;
        #line SPY_LINE(44, 406)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(44, 409)
        $v8 = $v9;
    }
    #line SPY_LINE(45, 412)
    if ($v8){
        #line SPY_LINE(45, 414)
        $v10 = a;
        #line SPY_LINE(45, 416)
        $v11 = $v10.stop;
        #line SPY_LINE(45, 418)
        $v12 = b;
        #line SPY_LINE(45, 420)
        $v13 = $v12.stop;
        #line SPY_LINE(45, 422)
        $v14 = $v11 == $v13;
    } else {
        #line SPY_LINE(45, 425)
        $v14 = $v8;
    }
    #line SPY_LINE(46, 428)
    if ($v14){
        #line SPY_LINE(46, 430)
        $v15 = a;
        #line SPY_LINE(46, 432)
        $v16 = $v15.stop_is_none;
        #line SPY_LINE(46, 434)
        $v17 = b;
        #line SPY_LINE(46, 436)
        $v18 = $v17.stop_is_none;
        #line SPY_LINE(46, 438)
        $v19 = $v16 == $v18;
    } else {
        #line SPY_LINE(46, 441)
        $v19 = $v14;
    }
    #line SPY_LINE(47, 444)
    if ($v19){
        #line SPY_LINE(47, 446)
        $v20 = a;
        #line SPY_LINE(47, 448)
        $v21 = $v20.step;
        #line SPY_LINE(47, 450)
        $v22 = b;
        #line SPY_LINE(47, 452)
        $v23 = $v22.step;
        #line SPY_LINE(47, 454)
        $v24 = $v21 == $v23;
    } else {
        #line SPY_LINE(47, 457)
        $v24 = $v19;
    }
    #line SPY_LINE(48, 460)
    if ($v24){
        #line SPY_LINE(48, 462)
        $v25 = a;
        #line SPY_LINE(48, 464)
        $v26 = $v25.step_is_none;
        #line SPY_LINE(48, 466)
        $v27 = b;
        #line SPY_LINE(48, 468)
        $v28 = $v27.step_is_none;
        #line SPY_LINE(48, 470)
        $v29 = $v26 == $v28;
    } else {
        #line SPY_LINE(48, 473)
        $v29 = $v24;
    }
    #line SPY_LINE(48, 476)
    $v30 = $v29;
    #line SPY_LINE(165, 478)
    return spy_operator$bool_not($v30);
    abort(); /* reached the end of the function without a `return` */
}
