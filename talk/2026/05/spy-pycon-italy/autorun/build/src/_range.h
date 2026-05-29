#ifndef SPY__RANGE_H
#define SPY__RANGE_H

#include <spy.h>

#ifdef __cplusplus
extern "C" {
#endif


// includes
#include "spy_structdefs.h"

// function declarations
spy__range$range_iterator spy__range$range$__fastiter__(spy__range$range self);
bool spy__range$range$__eq__(spy__range$range a, spy__range$range b);
bool spy__range$range$__ne__(spy__range$range a, spy__range$range b);
spy__range$range_iterator spy__range$range_iterator$__next__(spy__range$range_iterator self);
int32_t spy__range$range_iterator$__item__(spy__range$range_iterator self);
bool spy__range$range_iterator$__continue_iteration__(spy__range$range_iterator self);
bool spy__range$range_iterator$__eq__(spy__range$range_iterator a, spy__range$range_iterator b);
bool spy__range$range_iterator$__ne__(spy__range$range_iterator a, spy__range$range_iterator b);
spy__range$range spy__range$range$__new__$impl1(int32_t n);
spy__range$range spy__range$range$__new__$impl2(int32_t a, int32_t b);
spy__range$range spy__range$range$__new__$impl3(int32_t a, int32_t b, int32_t c);

// global variable declarations


#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // Header guard
