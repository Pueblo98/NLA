"""Run with python3 solvers/check_system_tools.py; synthetic checks, not FEM results."""
import numpy as np
from system_tools import constant_edge_load, reduce_system

# Refinement must preserve total force AND moment for a straight boundary.
for n in (1, 2, 7, 32):
    nodes = np.column_stack((np.full(n + 1, 2.), np.linspace(0, 1, n + 1)))
    edges = np.column_stack((np.arange(n), np.arange(1, n + 1)))
    forces = constant_edge_load(nodes, edges, [6., 0.]).reshape(-1, 2)
    np.testing.assert_allclose(forces.sum(axis=0), [6., 0.])
    np.testing.assert_allclose(np.sum(nodes[:, 0]*forces[:, 1] - nodes[:, 1]*forces[:, 0]), -3.)

# A two-DOF spring with nonzero prescribed motion and a load on its support.
K = np.array([[2., -2.], [-2., 2.]])
f = np.array([3., 4.])
A, b, free, d = reduce_system(K, f, [0], [.5])
d[free] = np.linalg.solve(A, b)
np.testing.assert_allclose(d, [.5, 2.5])
np.testing.assert_allclose(K @ d - f, [-7., 0.])
np.testing.assert_allclose(f, [3., 4.])
try:
    constant_edge_load([[0., 0.], [0., 1.]], [[0, 1], [1, 0]], [1., 0.])
except ValueError:
    pass
else:
    raise AssertionError("reversed duplicate edge accepted")
print("PASS: load refinement, moment, nonzero constraints, support loads, duplicate rejection")
