#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

# size of the grid in one dimension
N = 100
# Definition of the state vector
# in every grid cell, [mass density, momentum density, energy density]
U = np.zeros((N, 3))
e = 1e-5
# gamma for a 1-dimensional problem
gamma = 3
# defines the time step, must obey the Courant Condition
deltaX = 100.0 / N
deltaT = round(0.2*deltaX,12)
tEnd = 1000

def initShockTube(U):
    """sets up initial condition for the shock tube problem"""
    Unew = np.zeros_like(U)
    first = int(0.5 * N)
    # mass density rho
    Unew[:first, 0] = 1
    Unew[first:, 0] = 4
    # momentum density u
    Unew[:,1] = 0
    # defining E
    E = 0.5 * Unew[:,1] * (Unew[:,1]/Unew[:,0]) + Unew[:,0] * e
    Unew[:,2] = E

    return Unew


def initBlastWave(U):
    """sets up initial conditions for the blast wave problem"""
    Unew = np.zeros_like(U)
    # mass density rho
    Unew[:,0] = 1
    # momentum density u
    Unew[:,1] = 0
    # defining E
    E = 0.5 * Unew[:,1] * Unew[:,1]/Unew[:,0] + Unew[:,0] * e
    Unew[:,2] = E
    # adding one cell in the middle that has very large energy value of e = 1
    half = N//2
    Unew[half,2] = 0.5 * Unew[half,1] * (Unew[half,1]/Unew[half,0]) + Unew[half,0]

    return Unew


def calculateFlux(U):
    """Calculates the flux for the conservation laws."""
    F = np.zeros_like(U)
    rho = U[:, 0]  # mass density
    u = U[:, 1] / rho  # velocity
    E = U[:, 2]  # energy density

    # Pressure from equation of state
    p = (gamma - 1) * (E - 0.5 * rho * u**2)

    # Flux terms
    F[:, 0] = rho * u  # mass flux
    F[:, 1] = rho * u**2 + p  # momentum flux
    F[:, 2] = u * (E + p)  # energy flux

    return F


def RiemannSolver(UL, UR):
    """Solves the Riemann problem using a simple approximate solver."""
    # Left and right states
    rhoL, uL, EL = UL[:, 0], UL[:, 1] / UL[:, 0], UL[:, 2]
    rhoR, uR, ER = UR[:, 0], UR[:, 1] / UR[:, 0], UR[:, 2]

    # Pressure from equation of state
    pL = (gamma - 1) * (EL - 0.5 * rhoL * uL**2)
    pR = (gamma - 1) * (ER - 0.5 * rhoR * uR**2)

    # Average states
    rho_avg = 0.5 * (rhoL + rhoR)
    u_avg = 0.5 * (uL + uR)
    p_avg = 0.5 * (pL + pR)

    # Energy from average states
    E_avg = p_avg / (gamma - 1) + 0.5 * rho_avg * u_avg**2

    # Construct the flux for the averaged state
    F_avg = np.zeros_like(UL)
    F_avg[:, 0] = rho_avg * u_avg
    F_avg[:, 1] = rho_avg * u_avg**2 + p_avg
    F_avg[:, 2] = u_avg * (E_avg + p_avg)

    return F_avg


def methodA(U):
    """Implements the first numerical method (e.g., Lax-Friedrichs)."""
    F = calculateFlux(U)
    U_new = np.zeros_like(U)

    for i in range(1, N - 1):
        U_new[i] = 0.5 * (U[i + 1] + U[i - 1]) - deltaT / (2 * deltaX) * (F[i + 1] - F[i - 1])

    return U_new


def methodB(U):
    """Implements the second numerical method (e.g., MacCormack)."""
    F = calculateFlux(U)
    U_pred = np.zeros_like(U)
    U_new = np.zeros_like(U)

    # Predictor step
    for i in range(1, N - 1):
        U_pred[i] = U[i] - deltaT / deltaX * (F[i + 1] - F[i])

    # Recompute flux with predicted values
    F_pred = calculateFlux(U_pred)

    # Corrector step
    for i in range(1, N - 1):
        U_new[i] = 0.5 * (U[i] + U_pred[i] - deltaT / deltaX * (F_pred[i] - F_pred[i - 1]))

    return U_new


def methodC(U):
    """Implements the third numerical method (e.g., Godunov)."""
    U_new = np.zeros_like(U)

    for i in range(1, N - 1):
        UL = U[i]
        UR = U[i + 1]
        F_star = RiemannSolver(np.array([UL]), np.array([UR]))[0]
        U_new[i] = U[i] - deltaT / deltaX * (F_star - calculateFlux(U)[i])

    return U_new


# defining the six initial conditions for the six plots
UShockA = initShockTube(U)
UShockB = initShockTube(U)
UShockC = initShockTube(U)
UBlastA = initBlastWave(U)
UBlastB = initBlastWave(U)
UBlastC = initBlastWave(U)

fig, ax = plt.subplots(6, 3, figsize=(12, 21))
fig.subplots_adjust(left=0.08, right=0.95, bottom=0.1, top=0.87, wspace=0.2, hspace=0.6)
plt.suptitle("1-D Hydrodynamics", fontweight="bold", fontsize=14)

#method A plots
plot1 = ax[0][0]
plot2 = ax[0][1]
plot3 = ax[0][2]
plot4 = ax[1][0]
plot5 = ax[1][1]
plot6 = ax[1][2]

#method B plots
plot7 = ax[2][0]
plot8 = ax[2][1]
plot9 = ax[2][2]
plot10 = ax[3][0]
plot11 = ax[3][1]
plot12 = ax[3][2]

#method C plots
plot13 = ax[4][0]
plot14 = ax[4][1]
plot15 = ax[4][2]
plot16 = ax[5][0]
plot17 = ax[5][1]
plot18 = ax[5][2]


plot1.set_title("Method A Shock Tube density")
plot4.set_title("Method A Blast Wave density")
plot2.set_title("Method A Shock Tube momentum density")
plot5.set_title("Method A Blast Wave momentum density")
plot3.set_title("Method A Shock Tube energy density")
plot6.set_title("Method A Blast Wave energy density")

plot7.set_title("Method B Shock Tube density")
plot10.set_title("Method B Blast Wave density")
plot8.set_title("Method B Shock Tube momentum density")
plot11.set_title("Method B Blast Wave momentum density")
plot9.set_title("Method B Shock Tube energy density")
plot12.set_title("Method B Blast Wave energy density")

plot13.set_title("Method C Shock Tube density")
plot16.set_title("Method C Blast Wave density")
plot14.set_title("Method C Shock Tube momentum density")
plot17.set_title("Method C Blast Wave momentum density")
plot15.set_title("Method C Shock Tube energy density")
plot18.set_title("Method C Blast Wave energy density")

for n in range(int(tEnd/deltaT)):
    if n % (int(tEnd/deltaT/100.0)) == 0:
        print(n)
    UShockA = methodA(UShockA)
    UBlastA = methodA(UBlastA)
    UShockB = methodB(UShockB)
    UBlastB = methodB(UBlastB)
    UShockC = methodC(UShockC)
    UBlastC = methodC(UBlastC)
    if n % (int(tEnd/deltaT/10)) == 0:
        plot1.plot(UShockA[:,0])
        plot4.plot(UBlastA[:,0])
        plot2.plot(UShockA[:,1])
        plot5.plot(UBlastA[:,1])
        plot3.plot(UShockA[:,2])
        plot6.plot(UBlastA[:,2])
        
        plot7.plot(UShockB[:,0])
        plot10.plot(UBlastB[:,0])
        plot8.plot(UShockB[:,1])
        plot11.plot(UBlastB[:,1])
        plot9.plot(UShockB[:,2])
        plot12.plot(UBlastB[:,2])
        
        plot13.plot(UShockC[:,0])
        plot16.plot(UBlastC[:,0])
        plot14.plot(UShockC[:,1])
        plot17.plot(UBlastC[:,1])
        plot15.plot(UShockC[:,2])
        plot18.plot(UBlastC[:,2])

plt.savefig("newwwww.png",dpi=350)
plt.show()
