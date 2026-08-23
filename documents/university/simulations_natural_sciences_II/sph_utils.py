#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   sph_utils.py
@Time    :   2025/02/19 08:07:01
@Author  :   Dario B. Hug
@Desc    :   Utils of the Simulations II Course on the SPH
'''

import numpy as np
import matplotlib.pyplot as plt
from heapq import *


class Particle:
    def __init__(self, pos_x, pos_y, mass = 1):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.mass = mass
        self.dens = 0
        self.energy = 1
        self.vel_x = 0
        self.vel_y = 0
        self.acc_x = 0
        self.acc_y = 0
        self.pred_vel_x = 0
        self.pred_vel_y = 0
        self.pred_energy = 0

    def get_pos(self):
        return (self.pos_x, self.pos_y)
    
    def get_vel(self):
        return (self.vel_x, self.vel_y)

    def set_vel(self, vel_x, vel_y):
        self.vel_x = vel_x
        self.vel_y = vel_y

    def get_acc(self):
        return (self.acc_x, self.acc_y)

    def set_acc(self, acc_x, acc_y):
        self.acc_x = acc_x
        self.acc_y = acc_y

    def get_dens(self):
        return self.dens
    
    def set_dens(self, dens):
        self.dens = dens

    def get_energy(self):
        return self.energy
    
    def set_energy(self, energy):
        self.energy = energy

class Cell:
    def __init__(self, pos_bl_x, pos_bl_y, pos_tr_x, pos_tr_y,particles = None):
        self.pos_bl_x = pos_bl_x
        self.pos_bl_y = pos_bl_y
        self.pos_tr_x = pos_tr_x
        self.pos_tr_y = pos_tr_y
        self.particles = particles if particles is not None else []
        self.children = []
        
    def get_boundry(self):
        return [(self.pos_bl_x, self.pos_bl_y), (self.pos_tr_x, self.pos_tr_y)]
    
    def print_boundry(self):
        print(f"{(self.pos_bl_x, self.pos_tr_y)}  ---  {(self.pos_tr_x, self.pos_tr_y)} \n \n {(self.pos_bl_x, self.pos_bl_y)}  ---  {(self.pos_tr_x, self.pos_bl_y)}")

    def split_cell(self, dimension_x, max_particles = 8):

        if len(self.particles) <= max_particles:
            return

        # Splitting in X direction
        if dimension_x:
            # Find middle of cell in x-Dimension
            mid_x = 0.5 * (self.pos_bl_x + self.pos_tr_x)

            subcells = [
                Cell(self.pos_bl_x, self.pos_bl_y, mid_x, self.pos_tr_y),
                Cell(mid_x, self.pos_bl_y, self.pos_tr_x, self.pos_tr_y),
            ]

            for particle in self.particles:
                x, y = particle.get_pos()
                if x < mid_x: subcells[0].particles.append(particle) #Append to lower Side
                else: subcells[1].particles.append(particle) #Append to upper Side

        else: #Splitting in Y-Direction

            mid_y = 0.5 * (self.pos_bl_y + self.pos_tr_y)

            subcells = [
                Cell(self.pos_bl_x, self.pos_bl_y, self.pos_tr_x, mid_y),
                Cell(self.pos_bl_x, mid_y, self.pos_tr_x, self.pos_tr_y)
            ]

            for particle in self.particles: 
                x, y = particle.get_pos()
                if y < mid_y: subcells[0].particles.append(particle)
                else: subcells[1].particles.append(particle)
    
        self.children = subcells 
        self.particles = [] #Clear current Cell

        for child in self.children: 
            if len(child.particles) >= max_particles:
                child.split_cell( not dimension_x, max_particles)



"""         ---               week 02                   ---     """


# Priority queue
# Min heap structure -> smalles elmt is always at root
class prioq:
    def __init__(self, k):
        self.heap = []
        sentinel = (-np.inf, None, np.array([0.0,0.0]))
        for i in range(k):
            heappush(self.heap, sentinel)

        self.count = 0

    def replace(self, dist2, particle, dr):
        """Heapraplce() automatically restrucures heap after an elmt is pushed
        Function therefore ensures that smalles elmt is at root"""

        # heappushpop(self.heap, (dist2, particle, dr))
        heapreplace(self.heap, (dist2, particle, dr))
    
    def key(self):
        """Distance is negative, so prioq has stores the 
        "farthest" distance at heap[0] since it is the most negative"""
        return self.heap[0][0]

def celldist2(cell: Cell, r):
    """Calculates the squared minimum distance between a particle
    position and this node."""
    r = np.array(r)

    r_high = np.array([cell.pos_tr_x, cell.pos_tr_y])  # Top-right corner
    r_low = np.array([cell.pos_bl_x, cell.pos_bl_y])   # Bottom-left corner

    d1 = r - r_high
    d2 = r_low - r

    d1 = np.maximum(d1, d2)
    d1 = np.maximum(d1, np.zeros_like(d1))

    return float(np.dot(d1, d1))


def neighbor_search_periodic(pq, root, r, period):
    # walk the closest image first (at offset=[0, 0])
    for y in [0.0, -period[1], period[1]]:
        for x in [0.0, -period[0], period[0]]:
            rOffset = np.array([x, y])
            neighbor_search(pq, root, r, rOffset)

def neighbor_search(pq: prioq, root:Cell, r, rOffset):
    """ Recursively checking cell and children cells to fill up prioq"""
    if not root.children:
        for particle in root.particles:
            pos_x, pos_y = particle.get_pos()
            dr_x = (pos_x + rOffset[0]) - r[0]
            dr_y = (pos_y + rOffset[1]) - r[1]
            distance = -(dr_x**2 + dr_y**2) #negativee to ensure prioq behaviour

            if distance > pq.key():
                pq.replace(distance, particle, (dr_x, dr_y))
    
    else:
        for child in root.children:
            if -celldist2(child, r- rOffset) > pq.key():
                neighbor_search(pq, child, r, rOffset)


"""         ---               week 03                   ---     """


def top_hat_kernel(distance, radius):
    if np.linalg.norm(distance) <= radius:
        return 1.0
    else:
        return 0.0

def monaghan_kernel(distance, radius):
    distance_norm = np.linalg.norm(distance) if isinstance(distance, (list, np.ndarray)) else distance
    radius = float(radius)
    rel_dist = distance_norm / radius
    if rel_dist <= 1:
        kernel_value = (2/3) * (1 - 1.5 * rel_dist**2 + 0.75 * rel_dist**3)
        return kernel_value
    elif rel_dist <= 2:
        kernel_value = (2/3) * 0.25 * (2 - rel_dist)**3
        return kernel_value
    else:
        return 0.0

def calculate_density(particles, root, radius, kernel_func, period):
    for particle in particles:
        pq = prioq(32)
        particle_pos = np.array(particle.get_pos())
        neighbor_search_periodic(pq, root, particle_pos, period)
        density = 0.0
        for _, neighbor, distance in pq.heap:
            if neighbor is not None:
                distance_norm = np.linalg.norm(distance)
                kernel_value = kernel_func(distance_norm, radius)
                if kernel_value > 0:
                    density += neighbor.mass * kernel_value
        particle.dens = density


"""         ---               week 04/05                 ---     """

def leapfrog_update(particles, root, radius, kernel_func, period, dt, gamma=7):
    # Drift 1 (dt/2)
    for particle in particles:
        vel_x, vel_y = particle.get_vel()
        particle.pos_x += 0.5 * dt * vel_x
        particle.pos_y += 0.5 * dt * vel_y

        if particle.pos_x < 0:
            particle.pos_x = -particle.pos_x
            particle.vel_x = -0.8 * particle.vel_x
        elif particle.pos_x > period[0]:
            particle.pos_x = 2 * period[0] - particle.pos_x
            particle.vel_x = -0.8 * particle.vel_x

        if particle.pos_y < 0:
            particle.pos_y = -particle.pos_y
            particle.vel_y = -0.8 * particle.vel_y
        elif particle.pos_y > period[1]:
            particle.pos_y = 2 * period[1] - particle.pos_y
            particle.vel_y = -0.8 * particle.vel_y

    # Predictions
    for particle in particles:
        pq = prioq(32)
        particle_pos = np.array(particle.get_pos())
        neighbor_search_periodic(pq, root, particle_pos, period)

        # Calculate Density with Regularization
        density = 0.0
        for _, neighbor, distance in pq.heap:
            if neighbor:
                distance_norm = np.linalg.norm(distance)
                kernel_val = kernel_func(distance_norm, radius)
                density += neighbor.mass * max(kernel_val, 1e-5)  # Regularization

        particle.set_dens(density)
        
        # Calculate Acceleration
        acc_x, acc_y = 0.0, 6.0
        du_dt = 0.0

        bla = 7

        for _, neighbor, distance in pq.heap:
            if neighbor and particle.dens > 1e-5 and neighbor.dens > 1e-5:
                pressure_i = (gamma - 1) * particle.dens * particle.energy
                pressure_j = (gamma - 1) * neighbor.dens * neighbor.energy

                distance_norm = np.linalg.norm(distance) + 1e-9

                kernel_val = kernel_func(distance_norm, radius)
                
                pressure_term = (pressure_i / (particle.dens**2)) + (pressure_j / (neighbor.dens**2))

                vel_ij = np.array([particle.vel_x - neighbor.vel_x, particle.vel_y - neighbor.vel_y])

                r_ij = np.array(distance)

                mu_ij = (radius * np.dot(vel_ij, r_ij)) / (np.linalg.norm(r_ij) + 1e-9**2)
                
                pi_ij = -0.5 * mu_ij * np.sqrt(gamma * (gamma - 1) * particle.energy) + 1 * mu_ij**2 if np.dot(vel_ij, r_ij) < 0 else 0

                force_x = -neighbor.mass * (pressure_term + pi_ij) * kernel_val * (distance[0] / distance_norm)

                force_y = -neighbor.mass * (pressure_term + pi_ij) * kernel_val * (distance[1] / distance_norm)

                acc_x += force_x
                acc_y += force_y

                du_dt += 0.5 * neighbor.mass * pi_ij * np.dot(vel_ij, r_ij) * kernel_val / particle.dens
        
        particle.set_acc(acc_x, acc_y)
        
        # Enegry Prediction
        particle.pred_energy = particle.energy + du_dt * 0.5 * dt

        # Velocity Prediction
        particle.pred_vel_x = particle.vel_x + particle.acc_x * 0.5 * dt
        particle.pred_vel_y = particle.vel_y + particle.acc_y * 0.5 * dt

    # Kick (dt)
    for particle in particles:
        vel_x, vel_y = particle.get_vel()
        acc_x, acc_y = particle.get_acc()
        particle.set_vel(vel_x + dt * acc_x, vel_y + dt * acc_y)

    # Drift 2 (dt/2)
    for particle in particles:
        pos_x, pos_y = particle.get_pos()
        vel_x, vel_y = particle.get_vel()
        particle.pos_x = pos_x + 0.5 * dt * vel_x
        particle.pos_y = pos_y + 0.5 * dt * vel_y

        if particle.pos_x < 0:
            particle.pos_x = -particle.pos_x
            particle.vel_x = -0.8 * particle.vel_x
        elif particle.pos_x > period[0]:
            particle.pos_x = 2 * period[0] - particle.pos_x
            particle.vel_x = -0.8 * particle.vel_x

        if particle.pos_y < 0:
            particle.pos_y = -particle.pos_y
            particle.vel_y = -0.8 * particle.vel_y
        elif particle.pos_y > period[1]:
            particle.pos_y = 2 * period[1] - particle.pos_y
            particle.vel_y = -0.8 * particle.vel_y