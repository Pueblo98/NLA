# Latest files for the seven-section working draft

Lucas's Codex, 10 November 2026. Handoff for darius-codex and Hermes in
response to Darius's request to collect recent work. Paths below are relative
to `NLA/`. This records the current checkout; it does not certify unseen
versions in another agent's workspace or approve a final report.

## Sources to use

| Material | Current source | Integration guidance |
| --- | --- | --- |
| Opening model module | `drafts/modules/01-building-model/section.tex` | Latest prose revision includes a comma-free opening and the triangulation figure. Keep the opening general across shapes, loads and supports. |
| Opening figure | `drafts/modules/01-building-model/figures/triangulation.pdf` and `.png` | Illustrative L-shaped region, not a selected experimental geometry. Retain caption and reference. |
| Module integration and status | `drafts/modules/01-building-model/README.md`, `main.tex`, `references.bib`, `build.sh` | Include the section once, preserve citations and load `graphicx`. The README supersedes the earlier absence-of-source statement in `drafts/building-model-review.md`. |
| Assignment coverage and flow review | `notes/2026-11-10-report-structure-review.md` | Maps the seven sections to the brief, guidelines and Lab 5 checklist. This is a recommendation, not agreed final prose. |
| Completed progress document | `drafts/Group02_Draft.md` and `drafts/Group02_Draft.pdf` | Canonical 9 November progress source and nine-page PDF. Reuse numerical material; these predate the revised opening module and are not the new seven-section draft. |
| Numerical tables and provenance | `drafts/results/solver_comparison.csv`, `benchmark.json`, `histories.json` | Use these together for outcomes, settings, timings, refinement, validation and convergence histories. |
| Existing figures | `figures/progress_residuals.png`, `progress_refinement.png`, `deformed_plate_force_20x20.png` | The deformation figure uses amplification 200; retain that label and displacement units. |
| Reproduction and audit | `solvers/progress_benchmark.py`, `drafts/README.md`, `drafts/recovery-handoff.md`, `drafts/results/recovery-checks.txt` | Explain how the results were generated and previously checked. No solver reruns were performed for this handoff. |

## Numerical results ready to reuse

The common comparison uses the force-driven plane-stress square with 20 by
20 cells and 840 free displacement unknowns, not the separate prescribed-grip
case with 538 unknowns. The true relative residual target is below `1e-8`.
Saved iteration counts are CG 242, full GMRES 228, MINRES 236, diagonal PCG
226 and Gauss–Seidel 19,136. Ordinary Jacobi triggers the divergence guard;
damped Jacobi and steepest descent miss the target at 20,000 iterations.
Preserve these failure classifications. Timings are historical best-of-three
measurements of these implementations, not universal solver rankings.

The saved refinement cases have 220, 840 and 3,280 unknowns, condition numbers
approximately 2,469.5, 9,103.9 and 34,547.7, and CG counts 120, 242 and 469.
These are initial mesh comparisons, not a completed discretization-error
analysis. Small direct-example arrays are in `drafts/results/small_*.csv`.

## Rendering and remaining gaps

The revised opening's triangulation figure was verified previously, but its
full section PDF has not been built in this checkout: the recorded Tectonic
build failed because its TeX resource bundle was unavailable. There is no
current module PDF alongside `section.tex`. Hermes should compile this exact
source and check figure placement before its rendered version is integrated.
The earlier reported one-body-page preview predates the figure.

General constrained meshes, holes, broader load/support experiments, stronger
preconditioning and a systematic discretization-error study remain future
work in these sources. The professor's provided assembly routine remains
unidentified. Do not fill the additional-geometries or results sections with
invented outcomes. Keep progress questions and the two-week plan when making
a progress draft; retain contributions and AI-use disclosure.

For darius-codex: use these sources as the local baseline and ask Hermes to
identify any newer unmerged source by repository path and revision. This
handoff adds no new experimental results or final-draft approval.
