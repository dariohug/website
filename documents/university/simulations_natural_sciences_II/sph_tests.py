import numpy as np
from sph_utils import Particle, Cell 

# Used ChatGPT to helop me generate testcases for scenarious which I specified


def test_single_particle():
    """Test that a single particle does not cause cell splitting."""
    root_cell = Cell(0, 0, 1, 1)
    root_cell.particles = [Particle(0.5, 0.5)]
    root_cell.split_cell(dimension_x=True, max_particles=2)
    
    assert len(root_cell.children) == 0, "Single particle should not trigger splitting."


def test_no_particles():
    """Test that an empty cell does not split."""
    root_cell = Cell(0, 0, 1, 1)
    root_cell.split_cell(dimension_x=True, max_particles=2)
    
    assert len(root_cell.children) == 0, "Empty cell should not split."


def test_particles_on_boundary():
    """Ensure particles exactly on the split boundary are assigned correctly."""
    root_cell = Cell(0, 0, 1, 1)
    particles = [Particle(0.1, 0.1) for _ in range(8)]
    particles.append(Particle(0.5, 0.5))
    root_cell.particles = particles
    print(len(root_cell.particles))
    root_cell.split_cell(dimension_x=True, max_particles=8)

    assert len(root_cell.children) == 2, f"{len(root_cell.children)} Splits. Cell should split into two childrent"
    
    left_child, right_child = root_cell.children
    total_particles = len(left_child.particles) + len(right_child.particles)
    
    assert total_particles == 9, "All boundary particles should be assigned to a child cell."


def test_balanced_distribution():
    """Ensure splitting stops when max_particles is reached."""
    root_cell = Cell(0, 0, 1, 1)
    particles = [Particle(np.random.rand(), np.random.rand()) for _ in range(10)]
    root_cell.particles = particles
    root_cell.split_cell(dimension_x=True, max_particles=5)

    # Check that no child cell exceeds max_particles
    assert all(len(child.particles) <= 5 for child in root_cell.children), "No child cell should exceed max_particles."


def test_large_dataset():
    """Ensure large datasets split correctly and do not crash."""
    root_cell = Cell(0, 0, 1, 1)
    particles = [Particle(np.random.rand(), np.random.rand()) for _ in range(100000)]  # 100,000 random particles
    root_cell.particles = particles
    root_cell.split_cell(dimension_x=True, max_particles=500)

    # Ensure there are multiple splits happening
    assert len(root_cell.children) > 0, "Large dataset should trigger multiple splits."

def test_large_balanced_distribution():
    """Ensure large particles are distributed across multiple cells without unnecessary splits."""
    root_cell = Cell(0, 0, 1, 1)
    particles = [Particle(np.random.rand(), np.random.rand()) for _ in range(1000)]  # 1000 random particles
    root_cell.particles = particles
    root_cell.split_cell(dimension_x=True, max_particles=200)

    # Ensure that no cell has more than 200 particles
    for child in root_cell.children:
        assert len(child.particles) <= 200, f"Child cell has more than 200 particles: {len(child.particles)}"


def test_split_efficiency():
    """Test the efficiency of splitting large datasets with millions of particles."""
    root_cell = Cell(0, 0, 1, 1)
    particles = [Particle(np.random.rand(), np.random.rand()) for _ in range(1000000)]  # 1 million particles
    root_cell.particles = particles

    # Perform the split, but ensure that it doesn't go too deep (avoid excessive recursion)
    root_cell.split_cell(dimension_x=True, max_particles=500)

    # Ensure that cells are properly split into smaller chunks without excessive depth
    assert len(root_cell.children) > 1, "The dataset should split into multiple cells."

