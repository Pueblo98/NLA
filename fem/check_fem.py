"""Correctness checks for fem/elasticity.py and fem/plate.py. Run: python fem/check_fem.py

Every check has an answer known independently of the code.
"""
import numpy as np
from scipy.linalg import eigvalsh
from scipy.sparse.linalg import spsolve

from elasticity import assemble, element_stiffness, material_matrix
from plate import force_driven, rectangle_mesh, reduce_system, xy_dofs

# 1. D: plane-stress shear entry equals G = E / (2(1 + nu)); D is SPD.
D = material_matrix(200e9, 0.3)
assert np.isclose(D[2, 2], 200e9 / (2 * 1.3))
assert np.all(eigvalsh(D) > 0)

# 2. Unconstrained K is symmetric PSD with exactly 3 zero eigenvalues (2 translations
#    + 1 rotation), and the rigid motions are in its null space.
nodes, tris, edges, side = rectangle_mesh(1.0, 1.0, 3, 3)
K = assemble(nodes, tris, 1.0, 0.3)
Kd = K.toarray()
assert np.allclose(Kd, Kd.T, atol=1e-14)
ev = eigvalsh(Kd)
assert np.sum(np.abs(ev) < 1e-10 * ev.max()) == 3 and ev.min() > -1e-10
x, y = nodes[:, 0], nodes[:, 1]
for rigid in ([np.ones_like(x), 0 * x], [0 * x, np.ones_like(x)], [-y, x]):
    assert np.linalg.norm(Kd @ np.column_stack(rigid).ravel()) < 1e-12

# 3. Darius's two-triangle hand example (E=1, nu=0, t=1): A(0,0) B(1,0) C(0,1) D(1,1),
#    diagonal AD, clamp A and C, B moved by (0.02, 0), D free.
#    Hand result: A = 0.75 I, b = (0.005, 0), u_D = 1/150, v_D = 0.
nodes = np.array([[0, 0], [1, 0], [0, 1], [1, 1.0]])          # A, B, C, D
tris = np.array([[0, 1, 3], [0, 3, 2]])                        # ABD, ADC (CCW)
K = assemble(nodes, tris, 1.0, 0.0)
c = xy_dofs([0, 1, 2])
A, b, free, d = reduce_system(K, np.zeros(8), c, [0, 0, 0.02, 0, 0, 0])
assert np.allclose(A.toarray(), 0.75 * np.eye(2)) and np.allclose(b, [0.005, 0])
assert np.allclose(spsolve(A, b), [1 / 150, 0])

# 4. Patch test: roller support has the exact uniform-tension solution
#    u = p x / E, v = -nu p y / E. P1 elements must reproduce it to rounding error.
for diag in ("bl-tr", "br-tl"):
    s = force_driven(6, 4, Lx=2.0, Ly=1.0, support="roller", diagonal=diag)
    d = s["d"]
    d[s["free"]] = spsolve(s["A"].tocsc(), s["b"])
    E, nu, p = s["params"]["E"], s["params"]["nu"], s["params"]["p"]
    exact = np.column_stack([p * s["nodes"][:, 0] / E, -nu * p * s["nodes"][:, 1] / E]).ravel()
    assert np.linalg.norm(d - exact) / np.linalg.norm(exact) < 1e-12, diag

# 5. Clamped plate: reduced A is SPD; reactions balance the applied force F = p * Ly * t,
#    and the moment about (0, 0) as well.
s = force_driven(4)
A = s["A"].toarray()
assert np.allclose(A, A.T) and eigvalsh(A).min() > 0
d = s["d"]
d[s["free"]] = np.linalg.solve(A, s["b"])
r = s["K"] @ d - s["f"]                         # r[c] = reactions, r[free] = residual
F = s["params"]["p"] * s["params"]["Ly"] * s["params"]["t"]
total = (r + s["f"]).reshape(-1, 2)             # reactions + applied, per node
assert np.allclose(total.sum(axis=0), 0, atol=1e-6 * F)
xy = s["nodes"]
moment = np.sum(xy[:, 0] * total[:, 1] - xy[:, 1] * total[:, 0])
assert abs(moment) < 1e-6 * F
assert np.isclose(r[s["constrained"]].reshape(-1, 2)[:, 0].sum(), -F)

# 6. Linearity: doubling the load doubles the displacement.
d2 = np.linalg.solve(A, 2 * s["b"])
assert np.allclose(d2, 2 * d[s["free"]])

print("PASS: D, rigid-body null space, hand example, patch test, SPD, force/moment balance, linearity")
