# Section 5. Additional objects and experimental design

**Status:** AI-assisted working draft for team review (simplified to the third-year level; ~1.3 pages of body in the
11pt preview: one figure, one case-register table). Not an approved final section.

## Contents
- Four selected objects (no illustrative-only shapes): square **S** on a Triangle mesh, square plate with a central
  hole **H**, L-bracket **L**, cantilever beam **B**; ordered boundaries, meshing, loads, supports.
- Case register (Table `tab:objects-register`): geometry, refinement, mesh type, load size, load location, supports,
  material, bending, load type. Design only; outcomes go to Section 6.
- Labels: `sec:objects`, `fig:objects-meshes`, `tab:objects-register`. No numbered equations.

## Files
- `section.tex`, `main.tex` (preview; stand-in labels for Sections 2-4, 6), `references.bib`, `build.sh`, `preview.pdf`.
- `figures/objects_meshes.{pdf,png}` from `python3 draft/experiments/objects_figure.py`.

## Reproduce
- `python3 draft/experiments/objects.py` (repo root, ~11 min) -> `draft/experiments/results/objects/`
  (`objects.json`, `cases.csv`, `solver_runs.csv`, `meshes.csv`, `histories.npz`, `run.log`).
- `draft/experiments/results/objects/SUMMARY.md`: digest of all results and caveats for Section 6, plus the
  implementation details removed from the prose (Triangle switches `pq30a<sqrt(3)h^2/4>`, eigsh settings,
  Gauss-Seidel timing policy, matched-point coordinates).
- `sh build.sh` here builds `main.pdf`; copy to `preview.pdf`.

## Open decisions
- Total run time is 648 s (slightly above the 10-minute target), dominated by capped Gauss-Seidel runs.
- MINRES fails the shared residual test on the beam (residual stagnation at kappa ~ 1e6-1e7 despite tiny error);
  Section 6 should decide how to present this.
- The preview numbers equations globally (Sections 3's convention); Section 4's preview uses `\numberwithin`.
