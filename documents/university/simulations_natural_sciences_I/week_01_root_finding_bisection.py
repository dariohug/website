import numpy as np
import matplotlib.pyplot as plt 

''' 
Root finding Algorithm 


@autor:     Dario Hug
@date:      17.09.2024

Method: 
Define an area in which we assume a root mannually. Split this area recursively until we are inside 
an epsilon space.


'''
# We write the algorithm to find the root

def rootFindingAlgo(function, lowerbound, upperbound, epsilon):
    
    while abs(lowerbound-upperbound) > epsilon:
        c = 0.5 * (lowerbound + upperbound)
        if function(c) < 0:
            lowerbound = c
        elif function(c) > 0: 
            upperbound = c
        else:
            break #found exact root (unlikely but possible)
    
    return c

# We define the function
def base_function(x):
    return x ** x - 100

# We define values, that make sence for our function of interest
a = -5         #avoid "0 ** 0"
b = 5
e = 1e-5

if base_function(a) * base_function(b) > 0: # Check if bounds make any scence 
    raise ValueError("Function should have opposite sighs at bounds.")

# We call the function and print the results
print(rootFindingAlgo(base_function, a, b, e))



# To validate our results visually we can also plot the function
# Define the axes
x = np.linspace(0.01, 5, 400)  
y = base_function(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, label=r'$x^x - 100$', color='b')
plt.axhline(0, color='black',linewidth=1)
plt.axvline(0, color='black',linewidth=1)
plt.title(r'Plot of our fucntion $x^x - 100$')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.grid(True)
plt.legend()
plt.show()
