# fem/: P1 plane-elasticity assembly, benchmark plates, small direct example

Owner: Frambuesa + Ernesto (formulation). The theory is in `notes/physical-model.md`.

| File | What it does |
|---|---|
| `elasticity.py` | `material_matrix` (D, plane stress/strain), `strain_displacement` (B), `element_stiffness` (K_e = t·area·BᵀDB), `assemble(nodes, triangles, E, nu, *, plane, thickness)` → CSR K, following `solvers/assembly-solver-interface.txt` |
| `plate.py` | `rectangle_mesh` (structured grid; nx×ny **cells** = (nx+1)×(ny+1) **nodes**; diagonal `bl-tr` or `br-tl`), `force_driven(...)` (Ernesto's case), `grip_driven(...)` (Darius's case). Both return K, f, the constrained DOFs and values, the free DOFs, and the reduced A, b, using `solvers/system_tools.reduce_system` |
| `check_fem.py` | Checks with known answers: D, the rigid-body null space of the unconstrained K (exactly 3), Darius's 2-triangle hand example (A = 0.75 I, u_D = 1/150), the patch test against the exact roller solution, SPD, force and moment balance, linearity |
| `small_example.py` | Stage 2: 2×2 cells (12 unknowns), solved with PA = LU, the inverse and Cholesky → `results/small_example.txt` |
| `reproduce_drafts.py` | Matrix-level numbers from both drafts → `results/reproduce_drafts.txt` |
| `plot_deformed.py` | `figures/deformed_plate_force_20x20.png` |

Run from `fem/` with numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2 and Python 3.12.2.

DOFs are `[ux0, uy0, ux1, uy1, ...]` and zero-based. Node (i, j) has index `i + j*(nx+1)`.

## Reproduced so far (run by Frambuesa, 6 Nov 2026)

**Ernesto's force-driven plate.** Diagonal `bl-tr`, 1×1 m, E = 200 GPa, ν = 0.3, t = 1 cm, p = 100 MPa.

| Cells | Unknowns | Stored nnz | κ₂ | ρ(I − D⁻¹A) | 2/λmax(D⁻¹A) | CG | SD |
|---|---|---|---|---|---|---|---|
| 2×2 | 12 | 96 | 95.8 | | | | |
| 10×10 | 220 | 2,752 | 2,469.5 | 1.9513 | 0.6777 | 120 | 14,202 |
| 20×20 | 840 | 11,112 | 9,103.9 | 1.9601 | 0.6757 | 242 | 46,030 |
| 40×40 | 3,280 | 44,632 | 34,547.7 | 1.9622 | 0.6752 | 469 | 149,816 |

- The CG and SD counts use textbook implementations: x₀ = 0, stop when the true relative residual is below 1e-8, no iteration cap.
- Every value above matches Ernesto's draft.
- The 2×2 direct-solve residuals are 5.8e-16 (LU), 7.4e-16 (inverse) and 7.4e-16 (Cholesky). Ernesto's draft has 6.1/6.0/5.3e-16. Both sets are rounding level, and the exact digits depend on the BLAS library.
- The 2×2 right-edge displacements are u = 0.511 / 0.482 / 0.468 mm and v = +0.105 / +0.029 / −0.046 mm, listed bottom / middle / top. The clamp reactions sum to −1.0000e6 N.

**Darius's grip case.** 17×17 nodes. It gives **538 unknowns**. A has 7,004 stored entries, of which **6,054 are numerically nonzero**: about 950 entries cancel to exactly zero when the triangles are summed. So Darius's 6,054 counts numeric nonzeros, while Ernesto's 11,112 counts stored entries. Say which convention a table uses.

**Not reproduced here:** the Jacobi, damped-Jacobi, Gauss–Seidel, GMRES and MINRES runs, all timings, and Darius's solver table. Those belong to the solver comparison in `solvers/`.
