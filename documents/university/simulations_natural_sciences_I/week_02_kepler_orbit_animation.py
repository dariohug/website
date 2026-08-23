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
Solve the Kepller equation repeatedly and animate the rotation using matplot.animation. The dots further appart resembles
a higher speed by the planet. The speed of the planet increases if its distance to the sun is small. 
'''

def init():
    ax.set_xlim(-2.0, 1.0)  
    ax.set_ylim(-1.5, 1.5)
    return ln,

def fKepler(E, M, e):                           # E = eccentric anomaly,    M = mean anomaly,   e = eccentricity
    return E - e * np.sin(E) - M

def fKeplerDerivation(E, e):                    # Derivation of fKepler if we derive to E
    return 1 - e * np.cos(E)

def newtonMethod(fOriginal, fPrime, M, e, Estart):
    E = Estart
    tol = 1e-6
    max_iter = 100
    while max_iter > 0:
        delta_E = -fOriginal(E, M, e) / fPrime(E, e)
        E += delta_E

        if abs(delta_E) < tol:
            return E 
        
        max_iter -= 1
    raise Warning("Maximum of Iterations Exceeded, Result would not be in tolerance range") 

def update(frame):
    M = frame
    E = newtonMethod(fKepler, fKeplerDerivation, M, e, M)

    x = a * np.cos(E) - a * e
    y = a * np.sqrt(1 - e**2) * np.sin(E)
    
    xdata.append(x)
    ydata.append(y)
    
    ln.set_data(xdata, ydata)
    return ln,

# Constants for the orbit
e = 0.5                         #Changes Form of ellipse (eccentricity)
a = 1.0                         #Changes distance to sun 


linSpace = np.linspace(0, 2*np.pi, 128) #Frames of the Animation used as mean Anomaly 

xdata, ydata = [], []

fig, ax = plt.subplots()
ax.plot(0, 0, 'yo', markersize=12)
ln, = plt.plot(xdata, ydata, 'ro'); ax.set_title("Sun and Planet's orbit")

orbitAnimation = FuncAnimation(fig, update, frames=linSpace,
                    init_func=init, blit=True, interval=50, repeat=False)
orbitAnimation.save("Sun_and_Orbit.mp4", writer="ffmpeg", dpi=250)

plt.show()