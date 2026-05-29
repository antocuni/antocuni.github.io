#ifndef SPY_SPY_STRUCTDEFS_H
#define SPY_SPY_STRUCTDEFS_H

#include <spy.h>

#ifdef __cplusplus
extern "C" {
#endif

// includes

// forward type declarations
typedef struct spy__slice$tuple3 spy__slice$tuple3; /* _slice::tuple3 */
typedef struct spy__slice$Slice spy__slice$Slice; /* slice */
typedef struct spy__range$range spy__range$range; /* range */
typedef struct spy__range$range_iterator spy__range$range_iterator; /* _range::range_iterator */
typedef struct spy__tuple$tuple__builtins$i32_builtins$i32$_tup spy__tuple$tuple__builtins$i32_builtins$i32$_tup; /* tuple[i32, i32] */

// struct definitions
// struct spy_posix$TerminalSize: skipping because it's tagged as builtin
struct spy__slice$tuple3 {
    int32_t start;
    int32_t stop;
    int32_t step;
};

struct spy__slice$Slice {
    int32_t start;
    int32_t start_is_none;
    int32_t stop;
    int32_t stop_is_none;
    int32_t step;
    int32_t step_is_none;
};

struct spy__range$range {
    int32_t start;
    int32_t stop;
    int32_t step;
};

struct spy__range$range_iterator {
    int32_t i;
    int32_t stop;
    int32_t step;
};

struct spy__tuple$tuple__builtins$i32_builtins$i32$_tup {
    int32_t _item0;
    int32_t _item1;
};


// ptr accessors


#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // Header guard
