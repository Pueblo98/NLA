"""Stage 2: small coupled example solved with direct methods (PA = LU, inverse, Cholesky).

Case: Ernesto's force-driven plate (notes/ernesto-draft-force-driven.md), 2 x 2 cells
= 3 x 3 nodes = 8 triangles. Clamping the 3 left nodes leaves 12 unknowns.
Run: python fem/small_example.py
"""
import numpy as np
from scipy.linalg import cho_factor, cho_solve, eigvalsh, inv, lu_factor, lu_solve

from plate import force_driven

s = force_driven(2)                     # 1 x 1 m steel, t = 1 cm, p = 100 MPa, nu = 0.3
A = s["A"].toarray()                    # dense is fine at 12 x 12 (never for large meshes)
b = s["b"]
print(f"system: {A.shape[0]} unknowns, {s['A'].nnz} stored nonzeros")

# --- Is the matrix suitable for each method? ---
ev = eigvalsh(A)
print(f"symmetry: max |A - A^T| = {np.abs(A - A.T).max():.1e}")
print(f"eigenvalues: min {ev[0]:.3e}, max {ev[-1]:.3e}  -> positive definite: {ev[0] > 0}")
print(f"condition number kappa_2 = {ev[-1] / ev[0]:.1f}")

# --- Three direct solves ---
lu, piv = lu_factor(A)                  # PA = LU with partial pivoting
x_lu = lu_solve((lu, piv), b)
x_inv = inv(A) @ b                      # explicit inverse: only acceptable because A is tiny
C = cho_factor(A, lower=True)           # A = C C^T, no pivoting needed since A is SPD
x_ch = cho_solve(C, b)

rel = lambda x: np.linalg.norm(b - A @ x) / np.linalg.norm(b)  # noqa: E731
print("\nmethod      relative residual ||b - A x|| / ||b||")
for name, x in [("PA = LU", x_lu), ("inverse", x_inv), ("Cholesky", x_ch)]:
    print(f"{name:10s}  {rel(x):.1e}")
spread = max(np.linalg.norm(x_lu - x_inv), np.linalg.norm(x_lu - x_ch),
             np.linalg.norm(x_inv - x_ch)) / np.linalg.norm(x_ch)
print(f"max relative difference between the three solutions: {spread:.1e}")

# --- Physical result and checks ---
d = s["d"]
d[s["free"]] = x_ch
U = d.reshape(-1, 2) * 1e3              # mm
right = s["side"]["right"]              # bottom, middle, top
print("\nright edge (bottom, middle, top):")
print("  u [mm] =", np.round(U[right, 0], 4), "  estimate pL/E =",
      s["params"]["p"] * s["params"]["Lx"] / s["params"]["E"] * 1e3, "mm")
print("  v [mm] =", np.round(U[right, 1], 4))
r = s["K"] @ d - s["f"]
F = s["params"]["p"] * s["params"]["Ly"] * s["params"]["t"]
print(f"sum of clamp reactions: x {r[s['constrained']][0::2].sum():.4e} N, "
      f"y {r[s['constrained']][1::2].sum():.1e} N  (applied F = {F:.1e} N)")
