import numpy as np
import matplotlib.pyplot as plt

"""
Mandelbrot Diagram

@autor:     Dario Hug
@date:      08.10.2024

Assignment: 
Draw some Julia sets with various constants c (you can start with the Mandelbrot set as it was escained in the lecture and the exercise class)! 
z0 = c gives you the Mandelbrot.

Method: 
Create a grid of complex numbers within a specified range. For each number, iterate the mathematical formula to check if the value escapes to infinity 
by exceeding a certain threshold (== 2 per default). The number of iterations before an escape is recorded and used to create a color map, which reveals 
the intricate patterns of the Mandelbrot set. The final output includes an image of the entire set, along with two zoomed-in sections that highlight 
more detailed structures within the fractal.
"""


def fractal(x_min, x_max, y_min, y_max, detail, max_iteration, func):
  a = np.linspace(x_min, x_max,detail,dtype=np.float64)
  b = np.linspace(y_min, y_max, detail,dtype=np.float64)

  B = np.zeros((detail,detail))

  [x,y] = np.meshgrid(a,b)                                #to create the complex plane with the axes defined by a and b
  C = np.array(x+y*1j, np.complex128)
  Z = np.zeros(C.shape, np.complex128)                    #initial conditions (first iteration), Z has same dimension as C
  for n in np.arange(1,max_iteration +1):       
    Z = func(Z, C)                    
    escaped = np.where(np.abs(Z)>2)                          #finding escaped values (i.e. with an absolute value > 2)
    Z[escaped] = 0                                           #removing from iteration
    C[escaped] = 0                                           #removing from plane
    B[escaped] = n                                           #saving color value n
  
  B = B/np.max(np.max(B))
  return B

def mandelbrot_func(Z, C):
  return Z ** 2 + C

# def main(): 


#   detail = 1000                               #number of pixels in x and y direction
#   max_iteration = 120                         #maximum n for iterations (influences how detailed the structures are shown wehn zooming in)

#   # Main Plot
#   B1 = fractal(-2, 0.7, -1.4, 1.4 , detail, max_iteration, mandelbrot_func)

#   # Zoom 1
#   B2 = fractal(-0.25, 0, -1.0, -0.5, detail, max_iteration, mandelbrot_func)

#   # Zoom 2
#   B3 = fractal(-0.15, 0.15, -1.0, -0.5, detail, max_iteration, mandelbrot_func)

#   plt.figure(figsize=(18, 6))

#   plt.subplot(1, 3, 1)
#   plt.imshow(B1, extent=[-2, 0.7, -1.4, 1.4], origin='lower', interpolation='bilinear')
#   plt.title("Entire Mandelbrot Set")

#   plt.subplot(1, 3, 2)
#   plt.imshow(B2, extent=[-0.25, 0, -1.0, -0.5], origin='lower', interpolation='bilinear')
#   plt.title("Zoom 1")

#   plt.subplot(1, 3, 3)
#   plt.imshow(B3, extent=[-0.94, -0.9, -0.15, -0.1], origin='lower', interpolation='bilinear')
#   plt.title("Zoom 2")

#   plt.tight_layout()
#   plt.grid(True)
#   plt.show()

def main():
    detail = 1000  # number of pixels in x and y direction
    max_iteration = 120  # maximum n for iterations (influences how detailed the structures are shown when zooming in)

    # Generate the Mandelbrot set for the main plot
    B1 = fractal(-4, 1.4, -5.6, 5.6, detail, max_iteration, mandelbrot_func)

    # Plot the entire Mandelbrot set
    plt.figure(figsize=(8, 8))
    plt.imshow(B1, origin='lower', interpolation='bilinear')
    plt.title("Entire Mandelbrot Set")
    plt.tight_layout()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
  main() 