# Section 4. Simple Square Demonstration

**Status: AI-assisted working draft for team review (10 Nov 2026); not approved.**

Scope: [ROADMAP Section 4](../../ROADMAP.md#4-simple-square-demonstration); style: [WRITING_RULES](../../WRITING_RULES.md).

## Contents
Simplified on 10 Nov 2026 for a third-year applied maths audience (about 2 preview pages including two figures and one table; about 1.3 pages of prose).
- Case specification of the clamped square under uniform traction (`fem/plate.py:force_driven`), with the expected stretch pL/E = 0.5 mm.
- 2x2-cell worked system: free unknowns, `b`, symmetry and sparsity of the 12x12 `A`, kappa_2 = 95.8, PA=LU / inverse / Cholesky residuals at rounding level, right-edge u_x. The full matrix is no longer printed; the text points to `draft/experiments/results/square/small_A_integer.csv` (label `eq:square-small-matrix` removed; nothing referenced it).
- 20x20-cell system (N = 840): Table 1 (Method | Iterations | Final eta | Error vs LU | Time), Fig. 2 (one panel, first 300 iterations), three short paragraphs: Jacobi divergence (rho_J = 1.96), CG vs the sqrt(kappa) bound, GMRES cost.
- Deformation (Fig. 1c, x200) and one validation paragraph: supports, force/moment balance, solver agreement, patch test. Pointer to Section 6 for refinement.

## Files
- `section.tex`, `main.tex` (preview; keeps preview-only `\stublabel` stand-ins for labels from Sections 2, 3 and 6 — not used by the combined build), `references.bib`, `build.sh`, `preview.pdf`.
- `figures/square_setup.{pdf,png}` (schematic, 2x2 numbering, deformed plate), `figures/square_residuals.{pdf,png}` (single panel).

## Moved out of the report text (still in the results files)
Stored vs numerical nonzeros, solver status codes/native flags, the u_y asymmetry of the 2x2 mesh, damped-Jacobi/SD contraction factors, kappa_2(S) = 8029, the Gauss-Seidel vs CG accuracy comparison against kappa*eta, the full-budget residual panel, and the platform line in the table caption (see `solvers.json`).

## Reproduce
From the repository root: `python3 draft/experiments/square.py` (about 1 min; reruns timings).
`python3 draft/experiments/square.py --figures-only` redraws figures without retiming.
Outputs in `draft/experiments/results/square/`: `small.json`, `small_A.csv`, `small_A_integer.csv`,
`small_b.csv`, `small_x.csv`, `solvers.json`, `solver_comparison.csv`, `histories.json`,
`validation.json`, `refinement.json` (5..80 cells and the seeded 1e-6 load perturbation, for Section 6), `square.log`.
Timings in Table 1 are from the last full run recorded in `solvers.json`; timings vary between runs.

## Open decisions
- If the team prefers to show the 12x12 matrix, it could go in a short appendix (appendices do not count toward the 10 pages); the combined build would then need to include it.
- Load-perturbation result (4.51e-7 vs kappa bound 9.1e-3) is saved but left to Section 6.
