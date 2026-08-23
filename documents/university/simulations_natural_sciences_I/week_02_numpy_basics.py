import numpy as np

# integer arrays
ai = np.array([1, 2])
bi = np.array([3, 4])

# element wise operations
s = ai + bi
p = ai * bi

# float arrays
a = np.array([1, 2], dtype=float)
b = np.array([3.0, 4])

a = np.array([[1, 1], [1, 1]], dtype=float)
b = np.array([[1, 0], [0, 1]], dtype=float)

# matrix product
a_mat_b = np.matmul(a, b)

# element wise product
ab = a * b

x = np.linspace(0, 2, 3)
y = np.linspace(0, -2, 3)

X, Y = np.meshgrid(x, y)
Z = X + 1j * Y

