---
title: Simulations in the Natural Sciences I
featured: week_08_electron_optics_detector_design.ipynb
featured_title: "Week 08 — Electron optics: designing a detector"
featured_note: |
  The week 08 exercise was run as a class competition: everyone designed the
  electrode layout of an electron detector, and the designs were compared on
  how many of the 100 electrons reached the detector and how tightly their
  arrival times clustered.

  Electrons are traced through the electrostatic potential of the previous
  week (SOR relaxation) with a Leapfrog integrator and bilinear interpolation
  of the field. Three layouts are shown: one that reaches 100 % efficiency
  with an electrode right in front of the detector, one more realistic variant
  that trades some efficiency for a detector that is less exposed to the
  field, and one that accelerates the electrons into the detector. The bicubic
  interpolation at the end never worked properly — that part is left as it was.
---

Coursework for *Simulations in the Natural Sciences I* (ESC201, autumn 2024):
lecture notes, a summary, and one Python exercise per week — from root finding
and Kepler orbits to PDE solvers and 1-D hydrodynamics. The notebooks are
rendered in full, including their plots.
