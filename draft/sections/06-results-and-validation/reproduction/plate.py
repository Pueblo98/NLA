"""Structured rectangular plate meshes and the two benchmark load cases.

A minimal structured grid for benchmarks only; general meshes (holes,
`triangle`) belong in mesh/. Counts: nx * ny CELLS = (nx+1) * (ny+1) NODES.

Cases (the group has not yet chosen the main one):
  - force_driven:  Ernesto's draft. Left edge clamped, uniform traction p on the
    right edge (line load q = t * p, N/m). f_f != 0, d_p = 0.
  - grip_driven:   Darius's draft. Left edge clamped, middle right-edge nodes
    moved by a prescribed (ux, uy). f = 0, d_p != 0.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "solvers"))
from system_tools import constant_edge_load, reduce_system  # noqa: E402

from elasticity import assemble  # noqa: E402


def rectangle_mesh(Lx, Ly, nx, ny, diagonal="bl-tr"):
    """Nodes, CCW triangles and named boundary edges/nodes of an nx-by-ny cell grid.

    Node (i, j) (column i, row j) has index i + j * (nx + 1).
    diagonal: 'bl-tr' cuts each cell from bottom-left to top-right, 'br-tl' the other way.
    """
    xs, ys = np.linspace(0, Lx, nx + 1), np.linspace(0, Ly, ny + 1)
    X, Y = np.meshgrid(xs, ys)                 # row j, column i
    nodes = np.column_stack([X.ravel(), Y.ravel()])
    idx = lambda i, j: i + j * (nx + 1)         # noqa: E731
    tris = []
    for j in range(ny):
        for i in range(nx):
            n0, n1, n2, n3 = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            if diagonal == "bl-tr":
                tris += [(n0, n1, n2), (n0, n2, n3)]
            elif diagonal == "br-tl":
                tris += [(n0, n1, n3), (n1, n2, n3)]
            else:
                raise ValueError("diagonal must be 'bl-tr' or 'br-tl'")
    side = {
        "left": [idx(0, j) for j in range(ny + 1)],
        "right": [idx(nx, j) for j in range(ny + 1)],
        "bottom": [idx(i, 0) for i in range(nx + 1)],
        "top": [idx(i, ny) for i in range(nx + 1)],
    }
    edges = {k: np.column_stack([v[:-1], v[1:]]) for k, v in side.items()}
    return nodes, np.array(tris), edges, {k: np.array(v) for k, v in side.items()}


def xy_dofs(node_ids):
    node_ids = np.asarray(node_ids)
    return np.column_stack([2 * node_ids, 2 * node_ids + 1]).ravel()


def force_driven(nx, ny=None, *, Lx=1.0, Ly=1.0, E=200e9, nu=0.3, t=0.01, p=100e6,
                 diagonal="bl-tr", support="clamp"):
    """Ernesto's case. Units: m, Pa, N. Returns a dict with the full and reduced system.

    support='clamp'  : u = v = 0 on the whole left edge.
    support='roller' : u = 0 on the left edge, plus v = 0 at (0, 0) only
                       (removes the vertical rigid translation; exact solution
                       u = p x / E, v = -nu p y / E).
    """
    ny = nx if ny is None else ny
    nodes, tris, edges, side = rectangle_mesh(Lx, Ly, nx, ny, diagonal)
    K = assemble(nodes, tris, E, nu, plane="stress", thickness=t)
    f = constant_edge_load(nodes, edges["right"], [t * p, 0.0])   # q = t * p  [N/m]
    if support == "clamp":
        c = xy_dofs(side["left"])
    elif support == "roller":
        c = np.append(2 * side["left"], 2 * side["left"][0] + 1)
    else:
        raise ValueError("support must be 'clamp' or 'roller'")
    c = np.sort(c)
    A, b, free, d = reduce_system(K, f, c, np.zeros(c.size))
    return dict(nodes=nodes, triangles=tris, side=side, K=K, f=f, constrained=c,
                prescribed=np.zeros(c.size), free=free, d=d, A=A, b=b,
                params=dict(Lx=Lx, Ly=Ly, nx=nx, ny=ny, E=E, nu=nu, t=t, p=p,
                            diagonal=diagonal, support=support))


def grip_driven(n_nodes=17, *, E=1.0, nu=0.34, t=1.0, grip=(0.01, 0.0), grip_nodes=3,
                diagonal="bl-tr"):
    """Darius's case: unit square, n_nodes x n_nodes NODES, middle `grip_nodes`
    right-edge nodes moved by `grip` (both components prescribed). No applied force."""
    if n_nodes % 2 == 0 or grip_nodes % 2 == 0:
        raise ValueError("use odd n_nodes and odd grip_nodes so the grip is centred")
    n = n_nodes - 1
    nodes, tris, edges, side = rectangle_mesh(1.0, 1.0, n, n, diagonal)
    K = assemble(nodes, tris, E, nu, plane="stress", thickness=t)
    f = np.zeros(2 * len(nodes))
    mid = n // 2
    grip_ids = side["right"][mid - grip_nodes // 2: mid + grip_nodes // 2 + 1]
    c_left, c_grip = xy_dofs(side["left"]), xy_dofs(grip_ids)
    c = np.concatenate([c_left, c_grip])
    vals = np.concatenate([np.zeros(c_left.size), np.tile(grip, len(grip_ids))])
    order = np.argsort(c)
    c, vals = c[order], vals[order]
    A, b, free, d = reduce_system(K, f, c, vals)
    return dict(nodes=nodes, triangles=tris, side=side, K=K, f=f, constrained=c,
                prescribed=vals, free=free, d=d, A=A, b=b, grip_nodes=grip_ids,
                params=dict(n_nodes=n_nodes, E=E, nu=nu, t=t, grip=grip, diagonal=diagonal))
