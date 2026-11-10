# Section 4 numerical handoff for Hermes

Lucas's Codex, 10 November 2026. Supporting review, not approved report prose.

Read the assignment text, `draft/WRITING_RULES.md`, roadmap, and current Sections
1–3 before preparing this handoff. Hermes owns the Section 4 narrative and PDF
requested by Simon. The local checkout still has only the Section 4 README;
this review therefore checks the inputs and numerical evidence, not Hermes's
unavailable prose or compiled layout. Earlier sections were not edited.

## Complete case specification

Use the same **force-driven** square throughout this demonstration:

- Domain `[0,1] × [0,1]` m; plane stress; Young's modulus `E = 200 GPa`,
  Poisson ratio `nu = 0.3`, thickness `t = 0.01 m`.
- Clamp both displacement components on the entire left edge. Apply uniform
  outward horizontal traction `(p,0)` with `p = 100 MPa` to the right edge;
  top and bottom are traction-free. There is no body force.
- The traction gives line load `q = t p = 10^6 N/m` and total force
  `(10^6,0) N`. Thickness is already included in this line load.
- Structured square cells are split along bottom-left to top-right diagonals.
  These demonstration meshes are not generated with `triangle`.
- Small: 2 × 2 cells, 9 nodes, 8 triangles, 18 displacement components,
  6 constrained components and 12 free unknowns.
- Large: 20 × 20 cells, 441 nodes, 800 triangles, 882 displacement components,
  42 constrained components and 840 free unknowns; 11,112 stored matrix entries.

This is distinct from Darius's prescribed-displacement grip and from the
roller-supported patch test. The exact affine roller solution does not solve
this clamped problem.

## Small worked solution and array order

The existing full SI arrays remain in `drafts/results/small_A.csv`,
`small_b.csv`, and `small_x_cholesky.csv`. The new script verifies them against
a fresh assembly and triangular solves. Node `(i/2,j/2)` has zero-based index
`i+3j`. In the full vector, node `n` contributes components `2n,2n+1`.
The free nodes are `(1,2,4,5,7,8)`, each ordered `(ux,uy)`, so the free global
components are `(2,3,4,5,8,9,10,11,14,15,16,17)`.

For a legible display, define the dimensionless numerical arrays

\[
 \widehat A=A/(10^9\,\mathrm{N/m}),\qquad
 \widehat b=b/(10^6\,\mathrm N),\qquad
 \widehat x=x/(10^{-3}\,\mathrm m).
\]

Then `Ahat xhat = bhat`, with

\[
 \widehat b=(0,0,0.25,0,0,0,0.5,0,0,0,0.25,0)^T,
\]

and the computed free-displacement vector in millimetres is

\[
 \widehat x\simeq
 (0.261349,0.0760584,0.511195,0.104528,
  0.231629,0.00748693,0.482153,0.0293745,
  0.224451,-0.0541342,0.467800,-0.0460867)^T.
\]

Use the unrounded arrays for residual checks. `numerical-review/` contains
the scaled matrix and load, `small_unknowns.csv` mapping every unknown to its
node/component, and the actual lower Cholesky factor `L` and intermediate
vector `y` in SI units. These support a worked `Ly=b`, `L^T x=y` solution
without displaying all 144 matrix entries in the report. The independently
recomputed small-system residual is `6.61e-16`; slight changes in last digits
relative to the historical benchmark reflect numerical rounding.

For pivoted LU, use a consistent permutation convention. SciPy's
`scipy.linalg.lu(A)` returns `A = P L U`; the row-permutation form is therefore
`P^T A = L U`. The script verifies this identity (relative defect `8.37e-17`).
It should not be transcribed as `P A = L U` using the same returned `P`
without explaining the convention.

## Rechecked large-system outcomes

All eight methods were rerun once with the existing Section 3 implementation
and its complete stopping budget. Every iteration count and acceptance outcome
matches `drafts/results/benchmark.json`. This verification did not measure or
replace timings.

| Method | Iterations | Final true relative residual | Outcome |
|---|---:|---:|---|
| Jacobi | 49 | `1.324e10` | divergence guard |
| Damped Jacobi, weight 0.5 | 20,000 | `4.758e-6` | budget exhausted |
| Gauss–Seidel | 19,136 | `9.996e-9` | accepted |
| Steepest descent | 20,000 | `3.081e-6` | budget exhausted |
| CG | 242 | `9.405e-9` | accepted |
| Full GMRES | 228 | `9.476e-9` | accepted |
| MINRES | 236 | `9.445e-9` | callback reached target |
| Diagonal PCG | 226 | `8.012e-9` | accepted |

The large supported matrix's relative symmetry defect is `3.33e-17`.
Its estimated extreme eigenvalues are `1.916521e6` and `1.744789e10 N/m`,
giving `kappa_2 ≈ 9103.94`. The relative eigenpair defects
`||Av-lambda v||/(|lambda| ||v||)` are below `1e-11`.

For `S = diag(A)^(-1/2) A diag(A)^(-1/2)`, the extreme eigenvalues are
`0.0003686667` and `2.96005024`. Thus ordinary Jacobi's iteration matrix has
spectral radius `1.96005024 > 1`, explaining its failure here. Weight `0.5`
is inside the stability interval `0 < omega < 0.67566421`, but the damped
iteration's spectral radius is `0.99981567`, consistent with very slow
convergence. Budget exhaustion is not proof of mathematical divergence.

For report concision, Section 4 can illustrate CG and one contrasting method,
with full outcomes in the notebook/supporting data. Preserve failure labels
wherever those methods appear. Historical timings include iterative setup and
stopping checks; unsuccessful runs' elapsed times are not times to tolerance.

## Static iterates for figures

`numerical-review/cg_snapshots.csv` contains all nodes' SI coordinates and
displacements at CG iterations 0, 5, 25, 100 and 242. It can be plotted with
the original mesh using any explicitly stated common amplification factor.

| CG iteration | True relative residual | Relative error against same-mesh LU |
|---|---:|---:|
| 0 | 1 | 1 |
| 5 | 1.16896 | 0.936884 |
| 25 | 1.20260 | 0.200931 |
| 100 | `8.64464e-4` | `2.27883e-3` |
| 242 | `9.40527e-9` | `9.76875e-10` |

The residual initially exceeds its starting value, even while the error
decreases at these sampled steps. Do not describe the CG Euclidean residual as
monotonically decreasing. These fields are approximations to one static
equilibrium, not snapshots of the plate moving in physical time. GMRES history
in the historical data uses Arnoldi residual estimates; label that distinction.

The large solution's maximum right-edge horizontal displacement is
`0.496683 mm` (bottom-right). Its **top-right** horizontal displacement is
`0.495509 mm`; do not interchange these two observables. The coarse mesh's
bottom/top asymmetry is affected by the common diagonal orientation, so it
should not be presented as a physical asymmetry of the symmetric loading.

## Equilibrium validation

Using the large sparse-LU reference and reactions only on constrained
components:

- Applied force: `(1,000,000, 0) N`; support-force sum:
  `(-1,000,000.000000001, -1.64e-9) N`.
- Applied moment about `(0,0)`: `-500,000 N m`; support moment:
  `+500,000.0000000034 N m`.
- Remaining force imbalance: `(-1.20e-9, -1.64e-9) N`; remaining moment:
  `3.34e-9 N m`.
- Prescribed displacement error is exactly zero; free-system reference
  relative residual is `3.38e-14`.

Compute reactions from the original `K,d,f`, as in Section 2, rather than
counting free-row numerical residuals as support forces. These checks support
the algebraic equilibrium computation. They do not quantify continuum error.

## Reproduction and limits

Run `verify_numerics.py` in this folder using NumPy and SciPy. From `NLA/`,
the command is:

```sh
PYTHONPATH=.build-deps python3 draft/sections/04-square-example/verify_numerics.py
```

The local bundled packages require Python 3.13; select that interpreter if
`python3` resolves to a different version. Verification completed with Python
3.13.16, NumPy 2.5.4 and SciPy 1.18.1. The output
`numerical-review/verification.json` records values, residual checks, environment
and all solver results. The existing `fem/check_fem.py` also passed its material,
rigid-body null-space, hand-example, affine-patch, SPD, force/moment balance
and linearity checks in this session. The review reuses the team's assembly and iterative
implementations; it is an independent rerun and consistency check, not a second
FEM implementation or an analytical validation of the clamped continuum model.

Suggested opening bridge (optional working prose):

> We now apply the comparison protocol to a square plate. A small mesh makes
> the displacement variables and direct solution explicit; a finer mesh then
> shows how iterative methods approach the same static equilibrium.

Keep the detailed mechanics in Section 2 and algorithm/stopping explanations
in Section 3. The status of the course-provided assembly routine remains
unresolved, as already disclosed in Section 2. Hermes still needs to integrate
the chosen evidence into his source and compile and inspect that exact PDF
before reporting the section's layout as checked.
