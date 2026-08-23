import matplotlib.pyplot as plt
import numpy as np


def logistic_equation(p, k):
    return p*k*(1-p)

def main():
    N = 500
    T = 500
    k_ra = np.linspace(1, 4, 1000)
    k = 3
    res_k = []
    res_p = []

    for k in k_ra:
        p = 0.5 #fraction of the max supportable population (0 -> pop = 0, 1 -> pop = N)

        for i in range(T):
            p = logistic_equation(p, k)
            
        for i in range(N):
            p = logistic_equation(p, k)
            res_k.append(k)
            res_p.append(p)


    plt.figure(figsize=(10, 6))
    plt.scatter(res_k, res_p, s=0.1, color='black')
    plt.title("Bifurcation Diagram of the Logistic Map")
    plt.xlabel("Growth Rate (k)")
    plt.ylabel("Population (p)")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()