import math
import time


def count_triples_loop(P):
    """
    Counts how many integer right triangles (Pythagorean triples) have perimeter <= P.
    """
    m_max = int(math.isqrt(2 * P))  # loose but safe upper bound for m
    count = 0
    for m in range(1, m_max + 1):
        for n in range(1, m_max + 1):
            if ((m - n) & 1) and math.gcd(m, n) == 1:
                p0 = 2 * m * (m + n)  # a+b+c
                if p0 > P:
                    continue
                count += P // p0
    return count


def range_product(a, b):
    for i in range(*a):
        for j in range(*b):
            yield i, j

def count_triples_gen(P):
    m_max = int((math.isqrt(2 * P)))
    count = 0
    for m, n in range_product((1, m_max + 1), (1, m_max + 1)):
        if ((m - n) & 1) and math.gcd(m, n) == 1:
            p0 = 2 * m * (m + n)  # a+b+c
            if p0 > P:
                continue
            count += P // p0
    return count



class RangeProductIter:

    def __init__(self, a, b):
        self.i, self.n = a
        self.j, self.m = b

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        value = (self.i, self.j)
        self.j += 1
        if self.j >= self.m:
            self.j = 0
            self.i += 1
        return value

def count_triples_iter(P):
    m_max = int((math.isqrt(2 * P)))
    count = 0
    for m, n in RangeProductIter((1, m_max + 1), (1, m_max + 1)):
        if ((m - n) & 1) and math.gcd(m, n) == 1:
            p0 = 2 * m * (m + n)  # a+b+c
            if p0 > P:
                continue
            count += P // p0
    return count


def main():
    N = 10000000

    a = time.time()
    res = count_triples_loop(N)
    b = time.time()
    loop = b-a
    print(f'loop: {loop:.4f} secs (1x)    ({res})')

    a = time.time()
    res = count_triples_gen(N)
    b = time.time()
    gen = b-a
    print(f'gen:  {gen:.4f} secs ({gen/loop:.2f}x) ({res})')

    a = time.time()
    res = count_triples_iter(N)
    b = time.time()
    it = b-a
    print(f'iter: {it:.4f} secs ({it/loop:.2f}x) ({res})')


if __name__ == '__main__':
    main()
