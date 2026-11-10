"""Mesh-independent loads and constraints; interleaved x/y DOFs.

Reduction supports NumPy dense matrices and SciPy CSR matrices. No FEM
assembly or material assumptions are supplied by this module.
"""
import numpy as np


def constant_edge_load(nodes, edges, q):
    """Return full nodal forces for constant global line load q (N/m)."""
    nodes = np.asarray(nodes, dtype=float)
    edges = np.asarray(edges)
    q = np.asarray(q, dtype=float)
    if nodes.ndim != 2 or nodes.shape[1] != 2 or not np.isfinite(nodes).all():
        raise ValueError("nodes must be finite (N, 2) coordinates")
    if edges.ndim != 2 or edges.shape[1] != 2 or edges.dtype.kind not in 'iu':
        raise ValueError("edges must be integer (B, 2) indices")
    if q.shape != (2,) or not np.isfinite(q).all():
        raise ValueError("q must have two finite components")
    if np.any(edges < 0) or np.any(edges >= len(nodes)):
        raise ValueError("edge index outside nodes")
    if len(np.unique(np.sort(edges, axis=1), axis=0)) != len(edges):
        raise ValueError("duplicate loaded edge")
    lengths = np.linalg.norm(nodes[edges[:, 1]] - nodes[edges[:, 0]], axis=1)
    if np.any(lengths <= 0):
        raise ValueError("zero-length loaded edge")
    forces = np.zeros_like(nodes)
    for endpoint in (0, 1):
        np.add.at(forces, edges[:, endpoint], lengths[:, None] * q / 2)
    return forces.ravel()


def reduce_system(K, f, constrained, values):
    """Return A, b, free, d; fill d[free] after solving A x = b.

    Inputs K and f remain intact for reactions K @ d - f. CSR inputs
    stay sparse; callers should convert other sparse formats to CSR first.
    """
    f = np.asarray(f, dtype=float)
    c = np.asarray(constrained)
    values = np.asarray(values, dtype=float)
    if f.ndim != 1 or K.shape != (f.size, f.size):
        raise ValueError("incompatible K and f shapes")
    if c.ndim != 1 or (c.size and c.dtype.kind not in 'iu'):
        raise ValueError("constraints must be integer indices")
    c = c.astype(int)
    if np.any(c < 0) or np.any(c >= f.size) or len(np.unique(c)) != len(c):
        raise ValueError("constraints must be unique and in range")
    if values.shape != c.shape or not np.isfinite(values).all() or not np.isfinite(f).all():
        raise ValueError("invalid prescribed values or loads")
    free = np.setdiff1d(np.arange(f.size), c)
    d = np.zeros(f.size)
    d[c] = values
    return K[free, :][:, free], f[free] - K[free, :][:, c] @ values, free, d
