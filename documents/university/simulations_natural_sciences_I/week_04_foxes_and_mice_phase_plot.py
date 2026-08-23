import numpy as np
import matplotlib.pyplot as plt

"""
Foxes and Mice

@autor:     Dario Hug
@date:      09.10.2024

Assignment: 
Make a phase plot of the fox-mouse population comparing the behaviour for different time-step sizes and for the two methods, 
Forward-Euler and Midpoint. Use different starting values. How does the phase plot look when starting close to the fixed point? 
How does it look when further from the fixed point? 


Method: 
Simulate the population dynamics of foxes and mice using the Lotka-Volterra equation. The system models the interaction between foxes 
and mice using differential equations. Two numreical methods to solve the ODE's are used: the Forward Euler method, which updates population values based 
on current rates of change, and the Midpont method, which refines the update by estimating intermediate values. For both methods, 
multiple time-step sizes are applied, and the system is solved for several iterations. The resulting predator-prey relationships are 
visualized in phase plots that reveal population oscillazions. The outputs show the stability and accuracy of each method for different 
initial populations and time steps.
"""

def lotka_volterra(x, y):
    prey_growth_rate = 1.0
    predation_rate = 0.1
    predator_death_rate = 1.5
    predator_reproduction_rate = 0.075

    dxdt = prey_growth_rate * x - predation_rate * x * y
    dydt = - predator_death_rate * y + predator_reproduction_rate * x * y 
    return dxdt, dydt

def forward_euler(x0, y0, h, steps):
    x_vals, y_vals = [x0], [y0]
    x, y = x0, y0
    while steps > 0 :
        dxdt, dydt = lotka_volterra(x, y)
        x += h * dxdt
        y += h * dydt
        x_vals.append(x)
        y_vals.append(y)
        steps -= 1
    return np.array(x_vals), np.array(y_vals)

def midpoint_method(x0, y0, h, steps):
    x_vals, y_vals = [x0], [y0]
    x, y = x0, y0
    while steps > 0:
        dxdt1, dydt1 = lotka_volterra(x, y)
        x_mid = x + h/2 * dxdt1
        y_mid = y + h/2 * dydt1
        dxdt2, dydt2 = lotka_volterra(x_mid, y_mid)
        x += h * dxdt2
        y += h * dydt2
        x_vals.append(x)
        y_vals.append(y)
        steps -= 1
    return np.array(x_vals), np.array(y_vals)


def main():
    # We set our time stps 
    steps = 1000
    h_small = 0.01
    h_large = 0.03

    # We set our initial conditions
    x0_near_fp = 10   
    y0_near_fp = 5    
    x0_far_fp = 40    
    y0_far_fp = 20   


    # Near the fixed point
    x_fe_near_small, y_fe_near_small = forward_euler(x0_near_fp, y0_near_fp, h_small, steps)
    x_mp_near_small, y_mp_near_small = midpoint_method(x0_near_fp, y0_near_fp, h_small, steps)

    x_fe_near_large, y_fe_near_large = forward_euler(x0_near_fp, y0_near_fp, h_large, steps)
    x_mp_near_large, y_mp_near_large = midpoint_method(x0_near_fp, y0_near_fp, h_large, steps)

    # Far from the fixed point
    x_fe_far_small, y_fe_far_small = forward_euler(x0_far_fp, y0_far_fp, h_small, steps)
    x_mp_far_small, y_mp_far_small = midpoint_method(x0_far_fp, y0_far_fp, h_small, steps)

    x_fe_far_large, y_fe_far_large = forward_euler(x0_far_fp, y0_far_fp, h_large, steps)
    x_mp_far_large, y_mp_far_large = midpoint_method(x0_far_fp, y0_far_fp, h_large, steps)

    fig, axs = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle('Phase Plot of Fox-Mouse Population')

    # I used ChatGPT to assist with the repetative plotting
    # Near the fixed point
    axs[0, 0].plot(x_fe_near_small, y_fe_near_small, label="Forward Euler (small h)", color='r')
    axs[0, 0].plot(x_mp_near_small, y_mp_near_small, label="Midpoint (small h)", color='b')
    axs[0, 0].set_title('Near Fixed Point (Small Step)')
    axs[0, 0].set_xlabel('Prey (Mice)')
    axs[0, 0].set_ylabel('Predator (Foxes)')
    axs[0, 0].legend()

    axs[0, 1].plot(x_fe_near_large, y_fe_near_large, label="Forward Euler (large h)", color='r')
    axs[0, 1].plot(x_mp_near_large, y_mp_near_large, label="Midpoint (large h)", color='b')
    axs[0, 1].set_title('Near Fixed Point (Large Step)')
    axs[0, 1].set_xlabel('Prey (Mice)')
    axs[0, 1].set_ylabel('Predator (Foxes)')
    axs[0, 1].legend()

    # Far from the fixpoint
    axs[1, 0].plot(x_fe_far_small, y_fe_far_small, label="Forward Euler (small h)", color='r')
    axs[1, 0].plot(x_mp_far_small, y_mp_far_small, label="Midpoint (small h)", color='b')
    axs[1, 0].set_title('Far From Fixed Point (Small Step)')
    axs[1, 0].set_xlabel('Prey (Mice)')
    axs[1, 0].set_ylabel('Predator (Foxes)')
    axs[1, 0].legend()

    axs[1, 1].plot(x_fe_far_large, y_fe_far_large, label="Forward Euler (large h)", color='r')
    axs[1, 1].plot(x_mp_far_large, y_mp_far_large, label="Midpoint (large h)", color='b')
    axs[1, 1].set_title('Far From Fixed Point (Large Step)')
    axs[1, 1].set_xlabel('Prey (Mice)')
    axs[1, 1].set_ylabel('Predator (Foxes)')
    axs[1, 1].legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()