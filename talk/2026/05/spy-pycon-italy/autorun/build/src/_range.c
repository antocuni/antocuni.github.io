#include "_range.h"
#ifdef SPY_DEBUG_C
#    define SPY_LINE(SPY, C) C "/home/antocuni/pypy/misc/antocuni.github.io/blog/talk/2026/05/spy-pycon-italy/autorun/build/src/_range.c"
#else
#    define SPY_LINE(SPY, C) SPY "/home/antocuni/anaconda/spy/stdlib/_range.spy"
#endif

// constants and globals

// content of the module

#line SPY_LINE(37, 14)
spy__range$range_iterator spy__range$range$__fastiter__(spy__range$range self) {
    spy__range$range $v0;
    int32_t $v1;
    spy__range$range $v2;
    int32_t $v3;
    spy__range$range $v4;
    int32_t $v5;
    #line SPY_LINE(38, 22)
    $v0 = self;
    #line SPY_LINE(38, 24)
    $v1 = $v0.start;
    #line SPY_LINE(38, 26)
    $v2 = self;
    #line SPY_LINE(38, 28)
    $v3 = $v2.stop;
    #line SPY_LINE(38, 30)
    $v4 = self;
    #line SPY_LINE(38, 32)
    $v5 = $v4.step;
    #line SPY_LINE(38, 34)
    return (spy__range$range_iterator){ $v1, $v3, $v5 };
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 38)
bool spy__range$range$__eq__(spy__range$range a, spy__range$range b) {
    spy__range$range $v0;
    int32_t $v1;
    spy__range$range $v2;
    int32_t $v3;
    spy__range$range $v4;
    int32_t $v5;
    spy__range$range $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    spy__range$range $v10;
    int32_t $v11;
    spy__range$range $v12;
    int32_t $v13;
    bool $v14;
    #line SPY_LINE(6, 55)
    $v0 = a;
    #line SPY_LINE(6, 57)
    $v1 = $v0.start;
    #line SPY_LINE(6, 59)
    $v2 = b;
    #line SPY_LINE(6, 61)
    $v3 = $v2.start;
    #line SPY_LINE(171, 63)
    $v9 = $v1 == $v3;
    #line SPY_LINE(7, 65)
    if ($v9){
        #line SPY_LINE(7, 67)
        $v4 = a;
        #line SPY_LINE(7, 69)
        $v5 = $v4.stop;
        #line SPY_LINE(7, 71)
        $v6 = b;
        #line SPY_LINE(7, 73)
        $v7 = $v6.stop;
        #line SPY_LINE(7, 75)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(7, 78)
        $v8 = $v9;
    }
    #line SPY_LINE(8, 81)
    if ($v8){
        #line SPY_LINE(8, 83)
        $v10 = a;
        #line SPY_LINE(8, 85)
        $v11 = $v10.step;
        #line SPY_LINE(8, 87)
        $v12 = b;
        #line SPY_LINE(8, 89)
        $v13 = $v12.step;
        #line SPY_LINE(8, 91)
        $v14 = $v11 == $v13;
    } else {
        #line SPY_LINE(8, 94)
        $v14 = $v8;
    }
    #line SPY_LINE(165, 97)
    return $v14;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 101)
bool spy__range$range$__ne__(spy__range$range a, spy__range$range b) {
    spy__range$range $v0;
    int32_t $v1;
    spy__range$range $v2;
    int32_t $v3;
    spy__range$range $v4;
    int32_t $v5;
    spy__range$range $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    spy__range$range $v10;
    int32_t $v11;
    spy__range$range $v12;
    int32_t $v13;
    bool $v14;
    bool $v15;
    #line SPY_LINE(6, 119)
    $v0 = a;
    #line SPY_LINE(6, 121)
    $v1 = $v0.start;
    #line SPY_LINE(6, 123)
    $v2 = b;
    #line SPY_LINE(6, 125)
    $v3 = $v2.start;
    #line SPY_LINE(171, 127)
    $v9 = $v1 == $v3;
    #line SPY_LINE(7, 129)
    if ($v9){
        #line SPY_LINE(7, 131)
        $v4 = a;
        #line SPY_LINE(7, 133)
        $v5 = $v4.stop;
        #line SPY_LINE(7, 135)
        $v6 = b;
        #line SPY_LINE(7, 137)
        $v7 = $v6.stop;
        #line SPY_LINE(7, 139)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(7, 142)
        $v8 = $v9;
    }
    #line SPY_LINE(8, 145)
    if ($v8){
        #line SPY_LINE(8, 147)
        $v10 = a;
        #line SPY_LINE(8, 149)
        $v11 = $v10.step;
        #line SPY_LINE(8, 151)
        $v12 = b;
        #line SPY_LINE(8, 153)
        $v13 = $v12.step;
        #line SPY_LINE(8, 155)
        $v14 = $v11 == $v13;
    } else {
        #line SPY_LINE(8, 158)
        $v14 = $v8;
    }
    #line SPY_LINE(8, 161)
    $v15 = $v14;
    #line SPY_LINE(165, 163)
    return spy_operator$bool_not($v15);
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(47, 167)
spy__range$range_iterator spy__range$range_iterator$__next__(spy__range$range_iterator self) {
    spy__range$range_iterator $v0;
    int32_t $v1;
    spy__range$range_iterator $v2;
    int32_t $v3;
    spy__range$range_iterator $v4;
    int32_t $v5;
    spy__range$range_iterator $v6;
    int32_t $v7;
    #line SPY_LINE(48, 177)
    $v0 = self;
    #line SPY_LINE(48, 179)
    $v1 = $v0.i;
    #line SPY_LINE(48, 181)
    $v2 = self;
    #line SPY_LINE(48, 183)
    $v3 = $v2.step;
    #line SPY_LINE(48, 185)
    $v4 = self;
    #line SPY_LINE(48, 187)
    $v5 = $v4.stop;
    #line SPY_LINE(48, 189)
    $v6 = self;
    #line SPY_LINE(48, 191)
    $v7 = $v6.step;
    #line SPY_LINE(48, 193)
    return (spy__range$range_iterator){ $v1 + $v3, $v5, $v7 };
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(50, 197)
int32_t spy__range$range_iterator$__item__(spy__range$range_iterator self) {
    return self.i;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(54, 202)
bool spy__range$range_iterator$__continue_iteration__(spy__range$range_iterator self) {
    spy__range$range_iterator $v0;
    int32_t $v1;
    spy__range$range_iterator $v2;
    int32_t $v3;
    spy__range$range_iterator $v4;
    int32_t $v5;
    spy__range$range_iterator $v6;
    int32_t $v7;
    spy__range$range_iterator $v8;
    int32_t $v9;
    #line SPY_LINE(55, 214)
    $v0 = self;
    #line SPY_LINE(55, 216)
    $v1 = $v0.step;
    #line SPY_LINE(55, 218)
    if ($v1 > 0){
        $v2 = self;
        #line SPY_LINE(56, 221)
        $v3 = $v2.i;
        #line SPY_LINE(56, 223)
        $v4 = self;
        #line SPY_LINE(56, 225)
        $v5 = $v4.stop;
        #line SPY_LINE(56, 227)
        return $v3 < $v5;
    } else {
        $v6 = self;
        #line SPY_LINE(58, 231)
        $v7 = $v6.i;
        #line SPY_LINE(58, 233)
        $v8 = self;
        #line SPY_LINE(58, 235)
        $v9 = $v8.stop;
        #line SPY_LINE(58, 237)
        return $v7 > $v9;
    }
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 242)
bool spy__range$range_iterator$__eq__(spy__range$range_iterator a, spy__range$range_iterator b) {
    spy__range$range_iterator $v0;
    int32_t $v1;
    spy__range$range_iterator $v2;
    int32_t $v3;
    spy__range$range_iterator $v4;
    int32_t $v5;
    spy__range$range_iterator $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    spy__range$range_iterator $v10;
    int32_t $v11;
    spy__range$range_iterator $v12;
    int32_t $v13;
    bool $v14;
    #line SPY_LINE(43, 259)
    $v0 = a;
    #line SPY_LINE(43, 261)
    $v1 = $v0.i;
    #line SPY_LINE(43, 263)
    $v2 = b;
    #line SPY_LINE(43, 265)
    $v3 = $v2.i;
    #line SPY_LINE(171, 267)
    $v9 = $v1 == $v3;
    #line SPY_LINE(44, 269)
    if ($v9){
        #line SPY_LINE(44, 271)
        $v4 = a;
        #line SPY_LINE(44, 273)
        $v5 = $v4.stop;
        #line SPY_LINE(44, 275)
        $v6 = b;
        #line SPY_LINE(44, 277)
        $v7 = $v6.stop;
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
        $v11 = $v10.step;
        #line SPY_LINE(45, 291)
        $v12 = b;
        #line SPY_LINE(45, 293)
        $v13 = $v12.step;
        #line SPY_LINE(45, 295)
        $v14 = $v11 == $v13;
    } else {
        #line SPY_LINE(45, 298)
        $v14 = $v8;
    }
    #line SPY_LINE(165, 301)
    return $v14;
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(165, 305)
bool spy__range$range_iterator$__ne__(spy__range$range_iterator a, spy__range$range_iterator b) {
    spy__range$range_iterator $v0;
    int32_t $v1;
    spy__range$range_iterator $v2;
    int32_t $v3;
    spy__range$range_iterator $v4;
    int32_t $v5;
    spy__range$range_iterator $v6;
    int32_t $v7;
    bool $v8;
    bool $v9;
    spy__range$range_iterator $v10;
    int32_t $v11;
    spy__range$range_iterator $v12;
    int32_t $v13;
    bool $v14;
    bool $v15;
    #line SPY_LINE(43, 323)
    $v0 = a;
    #line SPY_LINE(43, 325)
    $v1 = $v0.i;
    #line SPY_LINE(43, 327)
    $v2 = b;
    #line SPY_LINE(43, 329)
    $v3 = $v2.i;
    #line SPY_LINE(171, 331)
    $v9 = $v1 == $v3;
    #line SPY_LINE(44, 333)
    if ($v9){
        #line SPY_LINE(44, 335)
        $v4 = a;
        #line SPY_LINE(44, 337)
        $v5 = $v4.stop;
        #line SPY_LINE(44, 339)
        $v6 = b;
        #line SPY_LINE(44, 341)
        $v7 = $v6.stop;
        #line SPY_LINE(44, 343)
        $v8 = $v5 == $v7;
    } else {
        #line SPY_LINE(44, 346)
        $v8 = $v9;
    }
    #line SPY_LINE(45, 349)
    if ($v8){
        #line SPY_LINE(45, 351)
        $v10 = a;
        #line SPY_LINE(45, 353)
        $v11 = $v10.step;
        #line SPY_LINE(45, 355)
        $v12 = b;
        #line SPY_LINE(45, 357)
        $v13 = $v12.step;
        #line SPY_LINE(45, 359)
        $v14 = $v11 == $v13;
    } else {
        #line SPY_LINE(45, 362)
        $v14 = $v8;
    }
    #line SPY_LINE(45, 365)
    $v15 = $v14;
    #line SPY_LINE(165, 367)
    return spy_operator$bool_not($v15);
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(12, 371)
spy__range$range spy__range$range$__new__$impl1(int32_t n) {
    return (spy__range$range){ 0, n, 1 };
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(15, 376)
spy__range$range spy__range$range$__new__$impl2(int32_t a, int32_t b) {
    return (spy__range$range){ a, b, 1 };
    abort(); /* reached the end of the function without a `return` */
}
#line SPY_LINE(18, 381)
spy__range$range spy__range$range$__new__$impl3(int32_t a, int32_t b, int32_t c) {
    return (spy__range$range){ a, b, c };
    abort(); /* reached the end of the function without a `return` */
}
