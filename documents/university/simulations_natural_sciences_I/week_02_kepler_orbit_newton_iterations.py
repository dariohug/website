import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

''' 
Keppler Orbits

@autor:     Dario Hug
@date:      25.09.2024

Assignment: 
Plot (and/or animate) the elliptical orbit of a planet around the sun by repeatedly solving Kepler's equation 
with Newton's method (or the bisection method), as explained in the lecture!

Method: 
Kepler's Equation: M = E - e sin(E)
Solve the equation repeatedly and animate the rotation using matplot.animation
'''

def init():
    ax.set_xlim(-1.5, 1.5)  
    ax.set_ylim(-1.5, 1.5)
    return ln,

def fKepler(E, M, e):                           # E = eccentric anomaly,    M = mean anomaly,   e = eccentricity
    return E - e * np.sin(E) - M

def fKeplerDerivation(E, e):                    # Derivation of fKepler if we derive to E
    return 1 - e * np.cos(E)

# Modify the newtonMethod to track iterations
def newtonMethod(fOriginal, fPrime, M, e, Estart):
    E = Estart
    tol = 1e-6
    max_iter = 100
    iterations = []  # Store the iterations
    while max_iter > 0:
        delta_E = -fOriginal(E, M, e) / fPrime(E, e)
        E += delta_E

        iterations.append(E)  # Store the current estimate

        if abs(delta_E) < tol:
            return E, iterations  # Return both the estimate and iterations 
        
        max_iter -= 1
    
    return E, iterations  # Ensure this returns both values


def update(frame):
    M = frame
    E, _ = newtonMethod(fKepler, fKeplerDerivation, M, e, M)

    x = a * np.cos(E)
    y = a * np.sqrt(1 - e**2) * np.sin(E)
    
    xdata.append(x)
    ydata.append(y)
    
    ln.set_data(xdata, ydata)
    return ln,

# Constants for the orbit
e = 0.5
a = 1.0

xdata, ydata = [], []

fig, ax = plt.subplots()
ax.plot(a * e, 0, 'yo', markersize=12)
ln, = plt.plot(xdata, ydata, 'ro', label="Sun and Planet's orbit")

ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 128),
                    init_func=init, blit=True, interval=50, repeat=False)
ani.save("orbit.mp4", writer="ffmpeg", dpi=250)

# New Parts Start Here
def animate_newton_method(M_initial, e):
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ln_newton, = ax2.plot([], [], 'bo-', animated=True)  # Blue line for iterations
    ax2.set_xlim(-0.7, 0.7)
    ax2.set_ylim(-0.5, 0.5)
    ax2.axhline(0, color='gray', lw=0.5, ls='--')  # Horizontal line at y=0
    ax2.axvline(0, color='gray', lw=0.5, ls='--')  # Vertical line at x=0
    ax2.set_title("Newton's Method Convergence")
    ax2.set_xlabel('E')
    ax2.set_ylabel('f(E)')

    # Get iterations for the first frame
    final_E, iterations_newton = newtonMethod(fKepler, fKeplerDerivation, M_initial, e, M_initial)


    # Update function for Newton's method animation
    def update_newton(frame):
        if frame < len(iterations_newton):
            E_current = iterations_newton[frame]
            f_current = fKepler(E_current, M_initial, e)
            
            # Update the line for the current guess
            ln_newton.set_data(iterations_newton[:frame+1], [fKepler(iteration, M_initial, e) for iteration in iterations_newton[:frame+1]])  # Current point
            return ln_newton,

    # Create the animation for the Newton's method steps
    ani_newton = FuncAnimation(fig2, update_newton, frames=len(iterations_newton), blit=True, interval=1000, repeat=False)
    ani_newton.save("newton_convergence.mp4", writer="ffmpeg", dpi=250)

# Call the new function to show the Newton's method animation
M_initial = 0  # You can choose any mean anomaly for the demonstration
animate_newton_method(M_initial, e)

plt.show()
