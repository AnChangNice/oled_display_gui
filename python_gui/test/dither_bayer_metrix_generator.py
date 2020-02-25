import numpy as np


def bayer_recursive(Mn):
    n, _ = Mn.shape
    Mn2 = np.zeros((2*n, 2*n), dtype='uint8')

    Mn2[:n, :n] = 4 * Mn
    Mn2[:n, n:] = 4 * Mn + 2
    Mn2[n:, :n] = 4 * Mn + 3
    Mn2[n:, n:] = 4 * Mn + 1

    return Mn2

M2 = np.array([[0, 2], [3, 1]])

M4 = bayer_recursive(M2)
print(M4)

M8 = bayer_recursive(M4)
print(M8)

M16 = bayer_recursive(M8)
print(M16)