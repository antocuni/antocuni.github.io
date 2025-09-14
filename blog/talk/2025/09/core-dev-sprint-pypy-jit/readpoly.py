import time
import struct

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

def read_loop():
    fmt = 'dddddd'
    size = struct.calcsize(fmt)
    tot_x = 0
    tot_y = 0
    n = 0
    with open('poly.bin', 'rb') as f:
        while True:
            buf = f.read(size)
            if not buf:
                break
            points = struct.unpack_from(fmt, buf)
            ax, ay, bx, by, cx, cy = points
            tot_x += (ax + bx + cx)
            tot_y += (ay + by + cy)
            n += 1

    print(n)
    x = tot_x/n
    y = tot_y/n
    return x, y

def read_proto():
    fmt = 'dddddd'
    size = struct.calcsize(fmt)

    tot_x = 0
    tot_y = 0
    n = 0
    with open('poly.bin', 'rb') as f:
        while True:
            buf = f.read(size)
            if not buf:
                break
            t = Triangle(buf, 0)
            tot_x += t.a.x + t.b.x + t.c.x
            tot_y += t.a.y + t.b.y + t.c.y
            n += 1

    x = tot_x/n
    y = tot_y/n
    return x, y



class Triangle:
    def __init__(self, buf, offset):
        self.buf = buf
        self.offset = offset

    @property
    def a(self):
        return Point(self.buf, 0)

    @property
    def b(self):
        return Point(self.buf, 16)

    @property
    def c(self):
        return Point(self.buf, 32)


class Point:
    def __init__(self, buf, offset):
        self.buf = buf
        self.offset = offset

    @property
    def x(self):
        return struct.unpack_from('d', self.buf, self.offset)[0]

    @property
    def y(self):
        return struct.unpack_from('d', self.buf, self.offset+8)[0]





def main():
    a = time.time()
    x, y = read_loop()
    b = time.time()
    print(f'bare loop: {b-a:.4f} secs ({x}, {y})')

    a = time.time()
    x, y = read_proto()
    b = time.time()
    print(f'protocol : {b-a:.4f} secs ({x}, {y})')


if __name__ == '__main__':
    main()
