import numpy as np
import matplotlib.pyplot as plt 

''' 
Feigenbaum Diagram

@autor:     Dario Hug
@date:      02.10.2024

Assignment: 
Draw a Feigenbaum diagram that results from solving the logistic equation. 
(Optional: Implement a function that allows you to zoom into the Feigenbaum diagram)

Method: 
Compute the Feigenbaum Diagram for a specific amount of points in a specific region (in our case [[2.5, 4.0][0, 1]] per default) and save the data.
The computation works as followed: It repeatedly applies the equation for different values of a and tracks how the variable x evolves. 
Initially, some iterations are discarded to remove temporary effects, and then the steady behavior is recorded. We use two function to plot these 
x values against a, creating a bifurcation diagram. The first one shows how the system transitions from stable states to more complex behaviors, 
eventually leading to chaos as a increases. The second one can be used to zoom in on more specific regions. Both plotting functions use the same data.  
'''

def logisticEquation(a, x):
    return a * x * (1 - x)

def computeBifurcation(a_min=2.5, a_max=4.0, a_points=1000, x_points=100, transient_iterations=500, plot_iterations=100):
    a_list = np.linspace(a_min, a_max, a_points)
    x_list = np.linspace(0, 1, x_points)
    bifurcation_data = []
    for a in a_list:
        x_values = []
        for x in x_list:            
            for _ in range(transient_iterations):
                x = logisticEquation(a, x)          #get discarted 
            for _ in range(plot_iterations):
                x = logisticEquation(a, x)          #are saved
                x_values.append((a, x))
        bifurcation_data.extend(x_values)
    return bifurcation_data

def plotBifurcationFull(bifurcation_data):
    a_values = [point[0] for point in bifurcation_data]
    x_values = [point[1] for point in bifurcation_data]

    plt.figure(figsize=(10, 7))
    plt.plot(a_values, x_values, ',k', alpha=0.25)
    plt.title("Full Bifurcation Diagram (a ∈ [2.5, 4.0])")
    plt.xlabel("a")
    plt.ylabel("x")
    plt.xlim(2.5, 4.0)
    plt.ylim(0, 1)
    plt.show()

def plotBifurcationRegion(bifurcation_data, a_min, a_max, x_min, x_max):
    filtered_data = [(a, x) for (a, x) in bifurcation_data if a_min <= a <= a_max and x_min <= x <= x_max]  # Filter out parts outside of our zoom window
    
    a_values = [point[0] for point in filtered_data]
    x_values = [point[1] for point in filtered_data]

    plt.figure(figsize=(10, 7))
    plt.plot(a_values, x_values, ',k', alpha=0.25)
    plt.title(f"Bifurcation Diagram (a ∈ [{a_min}, {a_max}], x ∈ [{x_min}, {x_max}])")
    plt.xlabel("a")
    plt.ylabel("x")
    plt.xlim(a_min, a_max)
    plt.ylim(x_min, x_max)
    plt.show()

def main():
    # For zooming in on a specific region of the Feigenbaum Diagram:
    # If you want to focus on a region outside of [2.5, 4.0], it must also be computed in the compute_bifurcation function.
        # If you want to focus on a very small region, it makes sense to increase the resolution by increasing a_points, x_points, and plot_iterations.
        # Since the Feigenbaum Diagram is a fractal, this can theoretically be done infinitely, but be aware that it will also exponentially increase computation time.

    a_min_region = 3.4
    a_max_region = 3.9

    x_min_region = 0.3
    x_max_region = 0.7

    data = computeBifurcation()
    plotBifurcationFull(bifurcation_data = data)
    plotBifurcationRegion(bifurcation_data = data, a_min = a_min_region, a_max = a_max_region, x_min = x_min_region, x_max = x_max_region)

if __name__ == "__main__":
        main()
