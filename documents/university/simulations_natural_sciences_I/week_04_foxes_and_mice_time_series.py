import numpy as np
import matplotlib.pyplot as plt

"""
Foxes and Mice

@autor:     Dario Hug
@date:      09.10.2024

Assignment: 
Make a one-dimensional plot of the fox-mouse population comparing the behavior for different time-step sizes and for the two methods, 
Forward-Euler and Midpoint. Use different starting values. Show the foxes and mice as different colors. 

Method: 
Simulate the population dynamics of foxes and mice using the Lotka-Volterra equation. The system models the interaction between foxes 
and mice using differential equations. Two numerical methods to solve the ODE's are used: the Forward Euler method, which updates population values based 
on current rates of change, and the Midpoint method, which refines the update by estimating intermediate values. For both methods, 
multiple time-step sizes are applied, and the system is solved for several iterations. The outputs are time-series plots showing
population changes.
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
    for _ in range(steps):
        dxdt, dydt = lotka_volterra(x, y)
        x += h * dxdt
        y += h * dydt
        x_vals.append(x)
        y_vals.append(y)
    return np.array(x_vals), np.array(y_vals)

def midpoint_method(x0, y0, h, steps):
    x_vals, y_vals = [x0], [y0]
    x, y = x0, y0
    for _ in range(steps):
        dxdt1, dydt1 = lotka_volterra(x, y)
        x_mid = x + h/2 * dxdt1
        y_mid = y + h/2 * dydt1
        dxdt2, dydt2 = lotka_volterra(x_mid, y_mid)
        x += h * dxdt2
        y += h * dydt2
        x_vals.append(x)
        y_vals.append(y)
    return np.array(x_vals), np.array(y_vals)

def main():
    # Time steps and number of iterations
    steps = 1000
    h_small = 0.01
    h_large = 0.03

    # Initial conditions
    x0_near_fp = 10   
    y0_near_fp = 5    
    x0_far_fp = 40    
    y0_far_fp = 20   

    # Solve near the fixed point
    x_fe_near_small, y_fe_near_small = forward_euler(x0_near_fp, y0_near_fp, h_small, steps)
    x_mp_near_small, y_mp_near_small = midpoint_method(x0_near_fp, y0_near_fp, h_small, steps)

    x_fe_near_large, y_fe_near_large = forward_euler(x0_near_fp, y0_near_fp, h_large, steps)
    x_mp_near_large, y_mp_near_large = midpoint_method(x0_near_fp, y0_near_fp, h_large, steps)

    # Solve far from the fixed point
    x_fe_far_small, y_fe_far_small = forward_euler(x0_far_fp, y0_far_fp, h_small, steps)
    x_mp_far_small, y_mp_far_small = midpoint_method(x0_far_fp, y0_far_fp, h_small, steps)

    x_fe_far_large, y_fe_far_large = forward_euler(x0_far_fp, y0_far_fp, h_large, steps)
    x_mp_far_large, y_mp_far_large = midpoint_method(x0_far_fp, y0_far_fp, h_large, steps)

    time = np.arange(steps + 1)

    fig, axs = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle('Time-Series Plot of Fox-Mouse Population')

    # Near the fixed point, small step size
    axs[0, 0].plot(time, x_fe_near_small, label="Mice (Forward Euler)", color='blue')
    axs[0, 0].plot(time, y_fe_near_small, label="Foxes (Forward Euler)", color='orange')
    axs[0, 0].plot(time, x_mp_near_small, label="Mice (Midpoint)", color='green', linestyle='--')
    axs[0, 0].plot(time, y_mp_near_small, label="Foxes (Midpoint)", color='red', linestyle='--')
    axs[0, 0].set_title('Near Fixed Point (Small Step)')
    axs[0, 0].set_xlabel('Time')
    axs[0, 0].set_ylabel('Population')
    axs[0, 0].legend()

    # Near the fixed point, large step size
    axs[0, 1].plot(time, x_fe_near_large, label="Mice (Forward Euler)", color='blue')
    axs[0, 1].plot(time, y_fe_near_large, label="Foxes (Forward Euler)", color='orange')
    axs[0, 1].plot(time, x_mp_near_large, label="Mice (Midpoint)", color='green', linestyle='--')
    axs[0, 1].plot(time, y_mp_near_large, label="Foxes (Midpoint)", color='red', linestyle='--')
    axs[0, 1].set_title('Near Fixed Point (Large Step)')
    axs[0, 1].set_xlabel('Time')
    axs[0, 1].set_ylabel('Population')
    axs[0, 1].legend()

    # Far from the fixed point, small step size
    axs[1, 0].plot(time, x_fe_far_small, label="Mice (Forward Euler)", color='blue')
    axs[1, 0].plot(time, y_fe_far_small, label="Foxes (Forward Euler)", color='orange')
    axs[1, 0].plot(time, x_mp_far_small, label="Mice (Midpoint)", color='green', linestyle='--')
    axs[1, 0].plot(time, y_mp_far_small, label="Foxes (Midpoint)", color='red', linestyle='--')
    axs[1, 0].set_title('Far From Fixed Point (Small Step)')
    axs[1, 0].set_xlabel('Time')
    axs[1, 0].set_ylabel('Population')
    axs[1, 0].legend()

    # Far from the fixed point, large step size
    axs[1, 1].plot(time, x_fe_far_large, label="Mice (Forward Euler)", color='blue')
    axs[1, 1].plot(time, y_fe_far_large, label="Foxes (Forward Euler)", color='orange')
    axs[1, 1].plot(time, x_mp_far_large, label="Mice (Midpoint)", color='green', linestyle='--')
    axs[1, 1].plot(time, y_mp_far_large, label="Foxes (Midpoint)", color='red', linestyle='--')
    axs[1, 1].set_title('Far From Fixed Point (Large Step)')
    axs[1, 1].set_xlabel('Time')
    axs[1, 1].set_ylabel('Population')
    axs[1, 1].legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
