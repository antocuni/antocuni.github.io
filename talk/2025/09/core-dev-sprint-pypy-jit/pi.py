import time
import pypyjit

def empty():
    # the JIT cannot enter here
    pass

def hic_sunt_leones():
    pypyjit.residual_call(empty)

def get_pi():
    """
    Compute an approximation of PI using the Leibniz series
    """
    tol = 0.0000001
    pi_approx = 0.0
    k = 0
    term = 1.0  # Initial term to enter the loop
    n = 0

    while abs(term) > tol:
        if k % 2 == 0:
            term = 1.0 / (2 * k + 1)
        else:
            term = -1.0 / (2 * k + 1)

        pi_approx = pi_approx + term

        if term > 0:
            n += 1

        k = k + 1
        hic_sunt_leones()

    return 4 * pi_approx


if __name__ == '__main__':
    get_pi() # warmup
    a = time.time()
    pi = get_pi()
    b = time.time()
    print(f'{b-a:.4f} secs, pi = {pi}')
