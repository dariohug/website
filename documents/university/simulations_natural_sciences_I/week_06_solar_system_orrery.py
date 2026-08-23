import numpy as np
import matplotlib.pyplot as plt
import copy

"""
Orrery

@autor:     Dario Hug
@date:      21.10.2024

Assignment: 
Make a solar system orrery following the steps outlined in the lecture. Also plot the path of the Sun and compare to the size of the Sun.
-> Use Leapfrog Method to solve ODE's 

Method: 
The code implements a numerical simulation of planet motion using the Leapfrog method to solve the ODEs governing the gravitational 
interactions in a N-Body system. It calculates the forces acting on each celestial body, updates their positions and velocities iteratively, 
and records the trajectories over time. The results are visualized through five  plots.
"""

delta_time = 3             #Time Step: 3 Days
astronomic_unit = 1         # roughly 1.496e11 meters
gaussian_constant = 0.01720209894846**2 #((0.01720209895 * astronomic_unit) ** (3 / 2)) / delta_time  # Gaussian Constant = G * M_sun --> 0.0007520572590081562

def leap_frog_positions(data, dt, forces):

    for index, particle in enumerate(data[0]):
        data[2][index] += dt / 2 * forces[particle.strip("'")]
    for index, particle in enumerate(data[0]):
        data[1][index] += dt * data[2][index]
    forces = calculate_forces(data)
    for index, particle in enumerate(data[0]):
        data[2][index] += dt / 2 * forces[particle.strip("'")]
    return data

def calculate_forces(data):
    number_of_particles = len(data[0])
    force_matrix = np.zeros((number_of_particles, number_of_particles, 3))

    for first_index, first_particle in enumerate(data[0]):
        for second_index, second_particle in enumerate(data[0]):
            if second_index != first_index:
                pos1 = np.array(data[1][first_index])
                pos2 = np.array(data[1][second_index])
                
                r_vector = pos2 - pos1
                r_distance = np.linalg.norm(r_vector)
                
                if r_distance > 1e10:
                    continue
                force_magnitude = (gaussian_constant * data[3][first_index] * data[3][second_index]) / r_distance**3
                force_vector = force_magnitude * r_vector

                # Since Newtons third force ij == -force ji
                force_matrix[first_index][second_index] = force_vector
                force_matrix[second_index][first_index] = -force_vector
                
    force_dict = {}
    for index, planet_forces in enumerate(force_matrix):
        total_force = np.sum(planet_forces, axis=0)
        force_dict[data[0][index].strip("'")] = total_force / data[3][index]  # Acceleration
    return force_dict

def plot_all_views(positions):
    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    
    # 1. Top-down 2D
    ax1 = axs[0, 0]
    for planet, pos_list in positions[1].items():
        x_positions = [pos[0] for pos in pos_list]
        y_positions = [pos[1] for pos in pos_list]
        ax1.plot(x_positions, y_positions, label=planet)
    ax1.set_xlabel('X Position (AU)')
    ax1.set_ylabel('Y Position (AU)')
    ax1.set_xlim(-30, 30)
    ax1.set_ylim(-30, 30)
    ax1.set_title('Top-Down 2D View (All Planets Visible)')
    ax1.legend()
    ax1.grid(True)
    
    # 2. Top-down 2D
    ax2 = axs[0, 1]
    for planet, pos_list in positions[0].items():
        x_positions = [pos[0] for pos in pos_list]
        y_positions = [pos[1] for pos in pos_list]
        ax2.plot(x_positions, y_positions, label=planet)
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)
    ax2.set_xlabel('X Position (AU)')
    ax2.set_ylabel('Y Position (AU)')
    ax2.set_title('Zoomed Top-Down 2D View (-2 to 2 AU)')
    ax2.legend()
    ax2.grid(True)
    
    # 3. Side 2D 
    ax3 = axs[0, 2]
    for planet, pos_list in positions[1].items():
        y_positions = [pos[1] for pos in pos_list]
        z_positions = [pos[2] for pos in pos_list]
        ax3.plot(y_positions, z_positions, label=planet)
    ax3.set_xlabel('Y Position (AU)')
    ax3.set_ylabel('Z Position (AU)')
    ax3.set_title('Side View from Positive X-Axis')
    ax3.legend()
    ax3.grid(True)
    
    # 4. 3D Room Projection
    ax4 = fig.add_subplot(2, 3, 4, projection='3d')
    for planet, pos_list in positions[1].items():
        x_positions = [pos[0] for pos in pos_list]
        y_positions = [pos[1] for pos in pos_list]
        z_positions = [pos[2] for pos in pos_list]
        ax4.plot(x_positions, y_positions, z_positions, label=planet)
    ax4.set_xlabel('X Position (AU)')
    ax4.set_ylabel('Y Position (AU)')
    ax4.set_zlabel('Z Position (AU)')
    ax4.set_title('3D Room Projection')
    ax4.legend()
    
    # 5. 2D top-down view focused on Sun's path
    ax5 = axs[1, 1]
    for planet, pos_list in positions[1].items():
        x_positions = [pos[0] for pos in pos_list]
        y_positions = [pos[1] for pos in pos_list]
        ax5.plot(x_positions, y_positions, label="Sun Path", color="orange")

    sun_diameter_au = 0.00465
    ax5.scatter(-0.05, 0, s=(sun_diameter_au * 20000)**2, color='yellow', label="Sun")  # Larger scaled size for visibility
    
    ax5.set_xlim(-0.1, 0.1)
    ax5.set_ylim(-0.1, 0.1)
    ax5.set_xlabel('X Position (AU)')
    ax5.set_ylabel('Y Position (AU)')
    ax5.set_title("Sun's Movement Compared to Size")
    ax5.grid(True)

    plt.tight_layout()
    plt.show()


def main():
    # path = "/SolSystData.dat"
    # data = rd.readPlanets(path)

    data = (np.array(["'Sun'", "'Mercury'", "'Venus'", "'Earth'", "'Mars'", "'Jupiter'",
       "'Saturn'", "'Uranus'", "'Neptune'"], 
       dtype=object), np.array([[-3.40296206e-04,  4.97380148e-03, -6.23013645e-05],
       [ 3.70473517e-02, -4.52921110e-01, -4.09025531e-02],
       [ 4.27215729e-01, -5.83575273e-01, -3.27942205e-02],
       [-9.94848697e-01,  4.56423186e-02, -6.09952519e-05],
       [-1.09353931e+00,  1.24038144e+00,  5.26690538e-02],
       [ 7.19907596e-01, -5.16476541e+00,  5.28130131e-03],
       [-8.46966474e+00,  3.80452712e+00,  2.70847473e-01],
       [ 1.97000144e+01, -3.95637610e+00, -2.69928887e-01],
       [ 2.36144153e+01, -1.85628872e+01, -1.61942570e-01]]), 
       np.array([[-6.47766862e-06, -1.29258041e-07,  1.15458503e-07],
       [ 2.23918387e-02,  3.73600844e-03, -1.75002692e-03],
       [ 1.62232899e-02,  1.18162995e-02, -7.74824282e-04],
       [-9.90140816e-04, -1.72545020e-02,  4.34624163e-07],
       [-9.95847094e-03, -8.08231635e-03,  7.52070865e-05],
       [ 7.38070784e-03,  1.39934409e-03, -1.71002343e-04],
       [-2.58308954e-03, -5.10197677e-03,  1.91556784e-04],
       [ 7.45740274e-04,  3.67279780e-03,  3.98878020e-06],
       [ 1.91927831e-03,  2.48634836e-03, -9.54332415e-05]]), 
       np.array([1.00000000e+00, 1.66013680e-07, 2.44783894e-06, 3.00348960e-06,
       3.22715145e-07, 9.54791938e-04, 2.85885981e-04, 4.36624404e-05,
       5.15138902e-05]))
    

    planet_positions = []

    for count, nr_iterations in enumerate([500, 20000]):
        
        number_of_particles = len(data[0])
        positions_over_time = [] 
        current_positions = [(data[0][index], data[1][index]) for index in range(number_of_particles)]
        positions_over_time.append(copy.deepcopy(current_positions))
        
        for _ in range(nr_iterations):
            forces = calculate_forces(data) 
            data = leap_frog_positions(data, delta_time, forces)  
            
            # use deepcopy since values are related with append
            current_positions = [(data[0][index], data[1][index]) for index in range(number_of_particles)]
            positions_over_time.append(copy.deepcopy(current_positions))

        current_positions_dict = {planet: [] for planet, _ in positions_over_time[0]}
        for snapshot in positions_over_time:
            for planet, position in snapshot:
                current_positions_dict[planet].append(position)
        planet_positions.append(current_positions_dict)

    plot_all_views(planet_positions)

if __name__ == "__main__":
    main()