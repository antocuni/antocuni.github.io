#ifndef SPY__LIST_H
#define SPY__LIST_H

#include <spy.h>

#ifdef __cplusplus
extern "C" {
#endif


// includes
#include "spy_structdefs.h"

// function declarations
int32_t spy__list$_py_adjust_indexes(int32_t length, int32_t start, int32_t stop, int32_t step);
spy__slice$tuple3 spy__list$_py_slice_unpack(int32_t length, spy__slice$Slice s);

// global variable declarations


#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // Header guard
