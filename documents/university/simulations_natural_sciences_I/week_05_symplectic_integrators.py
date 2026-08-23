import numpy as np
import matplotlib.pyplot as plt

"""
Symplectic Integration

@autor:     Dario Hug
@date:      21.10.2024

Assignment: 
Use the Leap-Frog method to make a phase plot (p vs q) of the harmonic oscillator for different total energies. 
Compare the results with what you get using the Forward Euler method and the midpoint Runge-Kutta method. Make the same plot for a simple pendulum.

Method: 
We want to compare three different methods of ODE solving in two different tasks. The Methods are: LeapFrog, Forward Euler, RungeKutta, the tasks
are a harmonic oscilator and a simple pendulum. We compute position and momentum and use discrete Timesteps. 
    1. Harmonic Oscillator:
   - The equations for position (q) and momentum (p) are solved using the spring constant (K), mass (m). From these two we also compute omega. 
   - Three initial conditions are used, and the outcome is compared.
    2. Pendulum:
   - The equations for angular position (q) and angular momentum (p) are solved using the gravitational constant (G) and pendulum length (L).
   - Three initial conditions are tested, and the solutions are plotted for each method.

The results are displayed as phase space plots, comparing the accuricy and stability of the different numerical methods. Especially in the forward
euler method plot of the pendulum, it is visible that this method can diverge exponentially. 

Sources: 

        -- For efficient plotting, i took inspiration from a blog by GeeksForGeeks --
        @Link: https://www.geeksforgeeks.org/plot-multiple-plots-in-matplotlib/
"""

G = 9.81                        #Gravitational constant
K = 1.0                         #Spring Constant
m = 1.0                         #Mass
L = 1.0                         #Length of Pendulum
dt = 0.01                       #Timestep
t_max = 60                      #Maximum Time 
t = np.arange(0, t_max, dt)     #Time Array -> length = 6000

omega = np.sqrt(K/m)            #Angular Freq. --> rad/s

def leapfrog_method_oscilator(q0, p0, omega, t):
    q = np.zeros_like(t)
    p = np.zeros_like(t)

    q[0] = q0
    p[0] = p0

    for i in range(1, len(t)):
        q_half_step = q[i-1] + 0.5 * dt * (omega**2) * p[i-1]       # Half Drift 
        p[i] = p[i-1] - dt * q_half_step                            # Kick
        q[i] = q_half_step + 0.5 * dt * (omega**2) * p[i]           # Half Drift

    return q, p


def leapfrog_method_pendulum(q0, p0, G, L, t):
    q = np.zeros_like(t)
    p = np.zeros_like(t)

    p[0] = p0
    q[0] = q0

    for i in range(1, len(t)):
        p_half_step = p[i-1] - 0.5 * dt * (G/L) * np.sin(q[i-1])    # Half step Velocity update
        q[i] = q[i-1] + dt * p_half_step                            # Full Position update
        p[i] = p_half_step - 0.5 * dt * (G/L) * np.sin(q[i])        # Another half step Velocity update
    return q, p

def forward_euler_oscillator(q0, p0, omega, t):
    q = np.zeros_like(t)
    p = np.zeros_like(t)

    q[0] = q0
    p[0] = p0

    for i in range(1, len(t)):
        q[i] = q[i - 1] + dt * p[i - 1]
        p[i] = p[i - 1] - dt * (omega**2 * q[i - 1])
    return q, p

def forward_euler_pendulum(q0, p0, g, L, t):
    q = np.zeros_like(t)
    p = np.zeros_like(t)

    q[0] = q0
    p[0] = p0
    
    for i in range(1, len(t)):
        q[i] = q[i - 1] + dt * p[i - 1]
        p[i] = p[i - 1] - dt * (g / L * np.sin(q[i - 1]))
    return q, p

def runge_kutta_oscillator(q0, p0, omega, t):
    q = np.zeros_like(t)
    p = np.zeros_like(t)
    q[0] = q0
    p[0] = p0
    for i in range(1, len(t)):
        step_1_q = dt * p[i - 1]                                        #First step (euler)
        step_1_p = dt * (-omega**2 * q[i - 1])

        step_2_q = dt * (p[i - 1] + 0.5 * step_1_p)                     #Second step (improve Accuracy)
        step_2_p = dt * (-omega**2 * (q[i - 1] + 0.5 * step_1_q))

        q[i] = q[i - 1] + step_2_q                                      # Update with second Step
        p[i] = p[i - 1] + step_2_p  

    return q, p

def runge_kutta_pendulum(q0, p0, g, L, t):
    q = np.zeros_like(t)
    p = np.zeros_like(t)
    q[0] = q0
    p[0] = p0
    for i in range(1, len(t)):
        step_1_q = dt * p[i - 1]                                        #First step (euler)
        step_1_p = dt * (-g / L * np.sin(q[i - 1]))

        step_2_q = dt * (p[i - 1] + 0.5 * step_1_p)                     #Second step (improve Accuracy)
        step_2_p = dt * (-g / L * np.sin(q[i - 1] + 0.5 * step_1_q))

        q[i] = q[i - 1] + step_2_q                                      # Update with second Step
        p[i] = p[i - 1] + step_2_p              

    return q, p

def main():
    
    initial_conditions_oscillator = [(1.0, 0.0), (2.0, 0.0), (0.5, 0.0)]
    initial_conditions_pendulum = [(np.pi/4, 0.0), (2*np.pi/4, 0.0), (3*np.pi/4, 0.0)]

    methods = ['Leapfrog', 'Forward Euler', 'Midpoint RK2']
    systems = ['Harmonic Oscillator', 'Pendulum']


    fig, axs = plt.subplots(2, 3, figsize=(18, 12))

    for q0, p0 in initial_conditions_oscillator:        # Harmonic Oscilator 
        
        q_lf, p_lf = leapfrog_method_oscilator(q0, p0, omega, t)            # Leapfrog
        axs[0, 0].plot(q_lf, p_lf, label=f'q0={q0}, p0={p0}')
        
        q_fe, p_fe = forward_euler_oscillator(q0, p0, omega, t)             # Forward Euler
        axs[0, 1].plot(q_fe, p_fe, label=f'q0={q0}, p0={p0}')

        q_rk2, p_rk2 = runge_kutta_oscillator(q0, p0, omega, t)             # Runge Kunta
        axs[0, 2].plot(q_rk2, p_rk2, label=f'q0={q0}, p0={p0}')

    for q0, p0 in initial_conditions_pendulum:          #Pendulum 
        
        q_lf, p_lf = leapfrog_method_pendulum(q0, p0, G, L, t)          # Leapfrog
        axs[1, 0].plot(q_lf, p_lf, label=f'q0={q0}, p0={p0}')
        
        q_fe, p_fe = forward_euler_pendulum(q0, p0, G, L, t)            # Forward Euler
        axs[1, 1].plot(q_fe, p_fe, label=f'q0={q0}, p0={p0}')
        
        q_rk2, p_rk2 = runge_kutta_pendulum(q0, p0, G, L, t)            # Runge Kunta
        axs[1, 2].plot(q_rk2, p_rk2, label=f'q0={q0}, p0={p0}')

    for i in range(3):
        axs[0, i].set_title(f'{methods[i]} - {systems[0]}')
        axs[0, i].set_xlabel('q (Position)')
        axs[0, i].set_ylabel('p (Velocity)')
        axs[0, i].legend()
        
        axs[1, i].set_title(f'{methods[i]} - {systems[1]}')
        axs[1, i].set_xlabel('q (Angle)')
        axs[1, i].set_ylabel('p (Velocity)')
        axs[1, i].legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()