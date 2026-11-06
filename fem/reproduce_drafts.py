"""Reproduce the matrix-level numbers reported in the two drafts with repo code.

  - Ernesto (notes/ernesto-draft-force-driven.md): nnz, kappa, Jacobi spectral radius,
    damped-Jacobi bound, CG and Steepest Descent iteration counts on 10/20/40 cells.
  - Darius (Elastic_Sheet_NLA_Project_Draft.pdf): 538 unknowns, 6,054 nonzeros (17 x 17 nodes).

CG and SD below are short textbook versions used ONLY to cross-check iteration counts
(x0 = 0, stop when the TRUE relative residual ||b - A x|| / ||b|| < 1e-8). The official
solver comparison (GS, GMRES, MINRES, timings) lives in solvers/ (Lucas Codex).
Run: python fem/reproduce_drafts.py   (~15 s; dense eigenvalues up to 3,280 x 3,280)
"""
import numpy as np
from scipy.linalg import eigvalsh
from scipy.sparse import diags

from plate import force_driven, grip_driven

TOL = 1e-8


def true_rel_res(A, b, x):
    return np.linalg.norm(b - A @ x) / np.linalg.norm(b)


def cg_iterations(A, b, maxit=200_000):
    x = np.zeros_like(b); r = b.copy(); p = r.copy(); rr = r @ r
    for k in range(1, maxit + 1):
        Ap = A @ p
        alpha = rr / (p @ Ap)
        x += alpha * p; r -= alpha * Ap
        if true_rel_res(A, b, x) < TOL:
            return k
        rr_new = r @ r
        p = r + (rr_new / rr) * p; rr = rr_new
    return None


def sd_iterations(A, b, maxit=200_000):
    x = np.zeros_like(b); r = b.copy(); nb = np.linalg.norm(b)
    for k in range(1, maxit + 1):
        Ar = A @ r
        alpha = (r @ r) / (r @ Ar)
        x += alpha * r; r -= alpha * Ar
        if np.linalg.norm(r) / nb < TOL and true_rel_res(A, b, x) < TOL:   # cheap test first
            return k
    return None


def numerical_nnz(A):
    """Entries that are not cancelled to (round-off) zero during assembly."""
    return int((np.abs(A.data) > 1e-12 * np.abs(A.data).max()).sum())


print("Ernesto's force-driven plate (1 x 1 m steel, t = 1 cm, nu = 0.3, p = 100 MPa)")
print("cells  unknowns  stored_nnz  numeric_nnz  kappa      rho_Jacobi  2/lmax(D^-1A)  CG   SD")
for n in (10, 20, 40):
    s = force_driven(n)
    A, b = s["A"], s["b"]
    ev = eigvalsh(A.toarray())
    Dh = diags(1 / np.sqrt(A.diagonal()))
    es = eigvalsh((Dh @ A @ Dh).toarray())            # S = D^-1/2 A D^-1/2, similar to D^-1 A
    rho = max(abs(1 - es[0]), abs(1 - es[-1]))
    print(f"{n:2d}x{n:<2d}  {A.shape[0]:8d}  {A.nnz:10d}  {numerical_nnz(A):11d}  "
          f"{ev[-1] / ev[0]:9.1f}  {rho:10.4f}  {2 / es[-1]:13.4f}  "
          f"{cg_iterations(A, b):4d} {sd_iterations(A, b):6d}")

g = grip_driven(17)
print("\nDarius's grip case (17 x 17 nodes, E = 1, nu = 0.34, grip (0.01, 0) on 3 nodes)")
print(f"unknowns {g['A'].shape[0]}, stored nnz {g['A'].nnz}, numeric nnz {numerical_nnz(g['A'])}")
