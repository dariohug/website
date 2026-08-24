---
title: Simulations in the Natural Sciences II
featured: sph_neighbour_search_and_density.ipynb
featured_title: "SPH: from a k-d tree to smoothed particle hydrodynamics"
featured_note: |
  The main thread of the course, built up week by week: a particle and cell
  class with a bomb-proof partitioning function, a k-nearest-neighbour search
  on the resulting tree with a priority queue and periodic boundaries, density
  estimates from the neighbour lists with the top-hat and Monaghan kernels,
  and finally the SPH equations themselves. That last part covers sound speed,
  pressure forces and a Sedov-Taylor blast wave.

  `sph_utils.py` holds the classes the notebook imports, `sph_tests.py` the
  edge cases for the partitioning, and the two `.mp4` files below are the
  resulting animations.
videos:
  - url: https://www.youtube.com/watch?v=KzZ3QqxkNw8
    title: 20k boids
    description: >
      The flocking exercise, run on the GPU with Taichi: 20,000 boids steering
      by the neighbours around them.
---

Coursework for *Simulations in the Natural Sciences II* (ESC202, spring 2025):
smoothed particle hydrodynamics, the Ising model with Metropolis, and the
travelling salesman problem by simulated annealing. It also has the lecture
notes on neighbour searching and SPH.
