---
title: Computational Astrophysics
featured: hydro_project_report.ipynb
featured_title: "Hydro project: solving advection and diffusion"
featured_note: |
  The semester project: solve the advection, diffusion and advection-diffusion
  equations in 1D, then advection in 2D, and compare the schemes. The solvers
  are written in C++ (`task_01` … `task_04`, listed below) and the notebook
  compiles them, runs them over a grid of methods, resolutions and initial
  profiles, and plots what comes back. It compares first-order Euler against
  RK2 and Lax-Wendroff, the second-order MUSCL scheme with slope limiters, and
  operator splitting for the combined equation.

  Re-running it recompiles the C++ and regenerates the result files, so those
  are not kept here.
---

Coursework for *Computational Astrophysics* (autumn 2024): the lecture notes,
the hydro project assignment, and my solution to it.
