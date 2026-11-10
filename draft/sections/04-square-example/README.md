# Section 4. Simple Square Demonstration

**Status: AI-assisted working draft for team review (10 Nov 2026); not approved.**

Scope: [ROADMAP Section 4](../../ROADMAP.md#4-simple-square-demonstration); style: [WRITING_RULES](../../WRITING_RULES.md).

## Contents
- Case specification of the clamped square under uniform traction (`fem/plate.py:force_driven`).
- 2x2-cell worked system: free unknowns, `b`, the 12x12 `A` in exact integer-scaled form, eigenvalues/kappa_2, PA=LU / inverse / Cholesky residuals, right-edge displacements.
- 20x20-cell system (N = 840): all protocol methods (Table 1, Fig. 2), kappa_2 and rho_J linked to Jacobi divergence, damped Jacobi/SD stall, CG vs the sqrt(kappa) bound, PCG, GMRES cost, sparse LU.
- Deformed view (Fig. 1c, x200) and validation: supports, force/moment balance with reactions, solver agreement, affine patch test.
- One forward pointer to Section 6 for refinement.

## Files
- `section.tex`, `main.tex` (preview; contains preview-only `\stublabel` stand-ins for Sections 2, 3, 6 labels — drop them in the combined report), `references.bib` (entries copied verbatim from Section 3), `build.sh`, `preview.pdf`.
- `figures/square_setup.{pdf,png}` (schematic, 2x2 numbering, deformed plate), `figures/square_residuals.{pdf,png}`.

## Reproduce
From the repository root: `python3 draft/experiments/square.py` (about 1 min; reruns timings).
`python3 draft/experiments/square.py --figures-only` redraws figures without retiming.
Outputs in `draft/experiments/results/square/`: `small.json`, `small_A.csv`, `small_A_integer.csv`,
`small_b.csv`, `small_x.csv`, `solvers.json`, `solver_comparison.csv`, `histories.json`,
`validation.json`, `refinement.json` (5..80 cells and the seeded 1e-6 load perturbation, for Section 6), `square.log`.
Timings in Table 1 are from the last full run recorded in `solvers.json`; timings vary between runs.

## Open decisions
- Body is about 2.5 preview pages, above the 1.5–2 page target. Possible cuts: move the 12x12 matrix to an appendix/CSV, or drop panel (a) of Fig. 2.
- Load-perturbation result (4.51e-7 vs kappa bound 9.1e-3) is saved but left to Section 6.
