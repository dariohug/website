import numpy as np
import pandas as pd



#load text files with pandas
def readPlanets(filename, N=-1):
    df = pd.read_csv(filename, sep=',', header=None, names=['name', 'm', 'x', 'y', 'z', 'vx', 'vy', 'vz'])
    name = np.array(df.loc[:, 'name'])
    m = np.array(df.loc[:, 'm'])
    r = np.array(df.loc[:, 'x':'z'])
    v = np.array(df.loc[:, 'vx':'vz'])
    if N > 0:
        name = name[0:N - 1]
        m = m[0:N - 1]
        r = r[0:N - 1]
        v = v[0:N - 1]
    return (name, r, v, m)

def main():
    path = "/home/dario/Documents/UZH/HS_2024/01_Simulations_in_Sciences/CodingExercises/week_06/SolSystData.dat"
    data = readPlanets(path)
    print(data)
    return data

"""
(array(["'Sun'", "'Mercury'", "'Venus'", "'Earth'", "'Mars'", "'Jupiter'",
       "'Saturn'", "'Uranus'", "'Neptune'"], 

       --> Position
       
       dtype=object), array([[-3.40296206e-04,  4.97380148e-03, -6.23013645e-05],
       [ 3.70473517e-02, -4.52921110e-01, -4.09025531e-02],
       [ 4.27215729e-01, -5.83575273e-01, -3.27942205e-02],
       [-9.94848697e-01,  4.56423186e-02, -6.09952519e-05],
       [-1.09353931e+00,  1.24038144e+00,  5.26690538e-02],
       [ 7.19907596e-01, -5.16476541e+00,  5.28130131e-03],
       [-8.46966474e+00,  3.80452712e+00,  2.70847473e-01],
       [ 1.97000144e+01, -3.95637610e+00, -2.69928887e-01],
       [ 2.36144153e+01, -1.85628872e+01, -1.61942570e-01]]), 
       
        --> Velocity 

       array([[-6.47766862e-06, -1.29258041e-07,  1.15458503e-07],
       [ 2.23918387e-02,  3.73600844e-03, -1.75002692e-03],
       [ 1.62232899e-02,  1.18162995e-02, -7.74824282e-04],
       [-9.90140816e-04, -1.72545020e-02,  4.34624163e-07],
       [-9.95847094e-03, -8.08231635e-03,  7.52070865e-05],
       [ 7.38070784e-03,  1.39934409e-03, -1.71002343e-04],
       [-2.58308954e-03, -5.10197677e-03,  1.91556784e-04],
       [ 7.45740274e-04,  3.67279780e-03,  3.98878020e-06],
       [ 1.91927831e-03,  2.48634836e-03, -9.54332415e-05]]), 
       
       --> Mass
       
       array([1.00000000e+00, 1.66013680e-07, 2.44783894e-06, 3.00348960e-06,
       3.22715145e-07, 9.54791938e-04, 2.85885981e-04, 4.36624404e-05,
       5.15138902e-05]))
"""

if __name__ == "__main__":
    main()    
    pass