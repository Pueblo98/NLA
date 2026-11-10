"""Linear-triangle (P1 / CST) finite elements for 2D linear elasticity.

Follows solvers/assembly-solver-interface.txt:
  - nodes (N, 2) floats, triangles (M, 3) zero-based, counter-clockwise
  - DOF ordering [ux0, uy0, ux1, uy1, ...]
  - assemble(nodes, triangles, E, nu, *, plane, thickness) -> CSR K (2N, 2N)

Math (see notes/physical-model.md):
  strain  eps = [eps_xx, eps_yy, gamma_xy] = B d_e      (B is 3x6, constant per triangle)
  stress  sigma = D eps                                  (D is 3x3, symmetric positive definite)
  element stiffness  K_e = t * area * B^T D B            (6x6, symmetric)
"""
import numpy as np
from scipy.sparse import coo_matrix


def material_matrix(E, nu, plane="stress"):
    """Constitutive matrix D in sigma = D eps (engineering shear strain gamma_xy)."""
    if not (E > 0 and -1 < nu < 0.5):
        raise ValueError("need E > 0 and -1 < nu < 0.5 for a positive definite D")
    if plane == "stress":
        return E / (1 - nu**2) * np.array([[1, nu, 0],
                                           [nu, 1, 0],
                                           [0, 0, (1 - nu) / 2]])
    if plane == "strain":
        return E / ((1 + nu) * (1 - 2 * nu)) * np.array([[1 - nu, nu, 0],
                                                         [nu, 1 - nu, 0],
                                                         [0, 0, (1 - 2 * nu) / 2]])
    raise ValueError("plane must be 'stress' or 'strain'")


def strain_displacement(xy):
    """Return (B, area) for one triangle with corner coordinates xy (3, 2), CCW.

    Inside a P1 triangle u(x, y) = sum_i N_i(x, y) u_i with linear N_i, so
    dN_i/dx = b_i / (2 area), dN_i/dy = c_i / (2 area), where
    b_i = y_j - y_k and c_i = x_k - x_j for (i, j, k) cyclic.
    """
    (x1, y1), (x2, y2), (x3, y3) = xy
    two_area = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    if two_area <= 0:
        raise ValueError("triangle is degenerate or not counter-clockwise")
    b = np.array([y2 - y3, y3 - y1, y1 - y2])
    c = np.array([x3 - x2, x1 - x3, x2 - x1])
    B = np.zeros((3, 6))
    B[0, 0::2] = b          # eps_xx  = du/dx
    B[1, 1::2] = c          # eps_yy  = dv/dy
    B[2, 0::2] = c          # gamma_xy = du/dy + dv/dx
    B[2, 1::2] = b
    return B / two_area, two_area / 2


def element_stiffness(xy, D, thickness):
    """K_e = t * area * B^T D B (6 x 6)."""
    B, area = strain_displacement(xy)
    return thickness * area * B.T @ D @ B


def assemble(nodes, triangles, E, nu, *, plane="stress", thickness=1.0):
    """Global stiffness matrix K (CSR, 2N x 2N), interleaved x/y DOFs."""
    nodes = np.asarray(nodes, dtype=float)
    triangles = np.asarray(triangles, dtype=int)
    if thickness <= 0:
        raise ValueError("thickness must be positive")
    D = material_matrix(E, nu, plane)
    rows, cols, vals = [], [], []
    for tri in triangles:
        Ke = element_stiffness(nodes[tri], D, thickness)
        dofs = np.column_stack([2 * tri, 2 * tri + 1]).ravel()  # [ux_a, uy_a, ux_b, ...]
        rows.append(np.repeat(dofs, 6))
        cols.append(np.tile(dofs, 6))
        vals.append(Ke.ravel())
    n = 2 * len(nodes)
    K = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                   shape=(n, n)).tocsr()   # duplicates (shared nodes) are summed here
    K.sum_duplicates()
    return K
