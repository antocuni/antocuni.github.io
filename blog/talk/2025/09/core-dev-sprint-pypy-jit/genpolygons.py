"""
struct Point {
    double x;
    double y;
};

struct Triangle {
    Point a;
    Point b;
    Point c;
};
"""

import struct
import random

def main():
    N = 1000000

    with open('poly.bin', 'wb') as f:
        for i in range(N):
            ps = [random.random() for _ in range(6)]
            fmt = 'dddddd'
            data = struct.pack(fmt, *ps)
            f.write(data)



if __name__ == '__main__':
    main()
