---
title: Electron-Detector Design Competition
---

One of the exercises in *Simulations in the Natural Sciences I* was run as a
class competition. The task: design the electrode layout of an electron
detector, then trace 100 electrons through the resulting electrostatic field.
Designs were ranked on two things. First, how many electrons reached the
detector. Second, how tightly their arrival times clustered. My winning layout
got **all 100 electrons** onto the detector.

The electrostatic potential is first solved on a grid with SOR relaxation. Each
electron is then pushed through that field with a Leapfrog integrator, and the
field between grid points is filled in with **bilinear interpolation**:

<div class="math">
\[ \phi(x,y) = (1-u)(1-t)\,\phi_1 + (1-u)\,t\,\phi_2 + u\,(1-t)\,\phi_3 + u\,t\,\phi_4 \]
</div>

where *t* and *u* are the fractional position inside a cell. The force on an
electron is **F** = −e ∇φ, so differentiating the interpolation gives the
acceleration directly:

<div class="math">
\[ a_x = \frac{e}{m_e}\left(-\frac{1}{\Delta}\big[(1-u)(\phi_2-\phi_1) + u(\phi_4-\phi_3)\big]\right) \]
</div>

That is exactly what the core of the simulation does. It interpolates the
field, then takes a symmetric half-kick, drift, half-kick Leapfrog step:

```python
def accel(x, y, U):
    j, l = getindex(x, y)          # cell containing (x, y)
    t = (x - j*delta) / delta      # fractional position in the cell
    u = (y - l*delta) / delta

    phi_1, phi_2 = U[j, l],   U[j+1, l]
    phi_3, phi_4 = U[j, l+1], U[j+1, l+1]

    # Bilinear field, then a = (e/m_e) * (-grad phi)
    ax = (e / me) * (-1/delta) * ((1-u)*(phi_2 - phi_1) + u*(phi_4 - phi_3))
    ay = (e / me) * (-1/delta) * ((1-t)*(phi_3 - phi_1) + t*(phi_4 - phi_2))
    return ax, ay

def leapfrog(x, y, vx, vy, h, U):
    ax, ay = accel(x, y, U)
    vx += 0.5*h*ax;  vy += 0.5*h*ay   # half kick
    x  += vx*h;      y  += vy*h        # drift
    ax, ay = accel(x, y, U)
    vx += 0.5*h*ax;  vy += 0.5*h*ay   # second half kick
    return x, y, vx, vy
```

The plot below shows the winning design: on the left the 100 electron paths
(cyan) with the local force vectors (magenta) over the potential, on the right
the electric field, and underneath the arrival-time and arrival-position
histograms. The efficiency is 100 %.

![Winning detector design: 100 electron paths through the potential, the electric field, and arrival histograms showing 100 % efficiency](/projects/electron_detector_winning_design.png)

A more conservative layout that keeps the detector further from the strong
field trades some of that efficiency (down to ~81 %) for a design that would be
gentler on a real, fragile sensor.

The full notebook is rendered in the
[notes folder](/documents/university/simulations_natural_sciences_I/). It has
every layout, the SOR solver, the histograms and my bicubic experiment that
never quite worked.
