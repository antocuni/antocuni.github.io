#ifndef SPY__SLICE_H
#define SPY__SLICE_H

#include <spy.h>

#ifdef __cplusplus
extern "C" {
#endif


// includes
#include "spy_structdefs.h"

// function declarations
bool spy__slice$tuple3$__eq__(spy__slice$tuple3 a, spy__slice$tuple3 b);
bool spy__slice$tuple3$__ne__(spy__slice$tuple3 a, spy__slice$tuple3 b);
spy__slice$tuple3 spy__slice$Slice$indices(spy__slice$Slice self, int32_t length);
bool spy__slice$Slice$__eq__(spy__slice$Slice a, spy__slice$Slice b);
bool spy__slice$Slice$__ne__(spy__slice$Slice a, spy__slice$Slice b);

// global variable declarations


#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // Header guard
