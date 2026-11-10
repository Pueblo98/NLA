# Section 6. Results, validation and discussion

**Status:** AI-assisted working draft for team review (not approved). Label `sec:results`.
Body is 2.0 pages in the 11pt/25 mm preview (`preview.pdf`, excluding references).

## Contents
Four run-in paragraph groups plus limitations: physical response (hole, re-entrant corner,
load location, beam bending vs stretching, supports, linearity, E and nu); mesh refinement and
discretization vs algebraic error (beam vs 51.2/51.8 mm); conditioning and solvers
(Fig. `fig:results-scaling`, Table `tab:results-solvers`, MINRES residual stall on the beam);
validation (support values, force/moment balance, negative control, load perturbation).
Figure `fig:results-deformed` shows H, L, B deformed (x100, x100, x5).

## Files
- `section.tex`, `main.tex` (preview stubs for labels of Sections 2-5, numbered as in the
  combined draft), `references.bib`, `build.sh`, `.gitignore`, `preview.pdf`.
- `figures/results_{deformed,scaling}.{pdf,png}`.

## Reproduce
From the repo root: `python3 draft/experiments/results_figures.py` (about 3 s). It reads
`draft/experiments/results/objects/{cases,solver_runs}.csv` and
`draft/experiments/results/square/refinement.json`, re-solves the level-2 meshes of H, L, B
with sparse LU for the deformed plot, and writes `draft/experiments/results/results/extra.json`
(fitted slopes, plot extrema, ten smallest eigenvalues of A for S and B at level 2).
Every other number comes from `results/objects/SUMMARY.md` / `objects.json` (fresh run,
10 Nov 2026) and `results/square/refinement.json` (perturbation test). Then `sh build.sh`.

## Notes and open decisions
- Table times: level 2 has best-of-3 timings for every method, Gauss-Seidel included;
  LU time = factorization + solve.
- "Only four beam eigenvalues lie below the square's smallest" uses `extra.json` (new, cheap).
- Hole peak stress is not compared with the wide-plate factor 3 (finite clamped plate, still
  rising under refinement); Section 5 cites the factor 3.
- Subsections were replaced by run-in paragraph headings to meet the 2-page limit.
- Damped Jacobi, steepest descent and full GMRES results on level 2 exist in SUMMARY.md but
  are not reported here (Section 4 covers them on the square).
