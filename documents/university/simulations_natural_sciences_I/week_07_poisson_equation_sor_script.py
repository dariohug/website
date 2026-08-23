#!/usr/bin/env python3
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt

# Number of grid points
N = 100

# Relaxation factor for SOR
omega = 1.9

# Define empty grid for voltage
U = np.zeros((N, N))

# Boundary conditions
R = np.ones_like(U) * omega / 4
R[0, :] = 0  # Top boundary
R[-1, :] = 0  # Bottom boundary
R[:, 0] = 0  # Left boundary
R[:, -1] = 0  # Right boundary

# "Stick" boundary condition in the center
center = N // 2
U[center, center] = 1000  # Voltage source in the center
R[center, center] = 0  # No relaxation at the center source

# Helper matrices
C = np.ones_like(U)  # For convolution results
M = np.ones_like(U)  # For updates in SOR method

# Checkerboard pattern (B for True is "Red" cells, ~B for "Black" cells)
B = np.ones_like(U, dtype=bool)
B[1::2, ::2] = False
B[::2, 1::2] = False
print(B)
# Count steps
nsteps = 0

# Convergence condition
diff = np.max(np.abs(M))

# Iteration loop for SOR method with convergence check
while diff >= 1e-3:
    print(f"Step {nsteps}, max change: {diff}")
    
    # Apply convolution for "Red" points
    ndimage.convolve(U, np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]), output=C, mode="constant", cval=0)
    M[B] = omega * C[B]  # Update for Red cells
    U[B] = U[B] + M[B]  # Apply the update
    
    # Apply convolution for "Black" points
    ndimage.convolve(U, np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]), output=C, mode="constant", cval=0)
    M[~B] = omega * C[~B]  # Update for Black cells
    U[~B] = U[~B] + M[~B]  # Apply the update
    
    # Update step count and calculate max difference
    nsteps += 1
    diff = np.max(np.abs(M))

# Plotting results
plt.figure(figsize=(10, 4))
min_val, max_val = U.min(), U.max()

plt.subplot(1, 2, 1)
# Set levels if there's not enough range in U
if min_val != max_val:
    levels = np.linspace(min_val, max_val, 50)
    plt.contourf(U, levels=levels, cmap="inferno")
else:
    plt.contourf(U, levels=[min_val, max_val + 1], cmap="inferno")

plt.title("SOR Method: Contour Plot")

plt.subplot(1, 2, 2)
plt.imshow(U, cmap="inferno")
plt.colorbar(label="Voltage (V)")
plt.title("SOR Method: Color Plot")


plt.show()
