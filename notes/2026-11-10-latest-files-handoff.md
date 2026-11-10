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

## Follow-up source audit for consolidation

Rechecked the current sources on 10 November after the handoff above. A
read-only standard-library check confirmed that all eight CSV rows exactly
match `benchmark.json` in method, iterations, residual, error, status,
acceptance and best time. Acceptance agrees with the saved `1e-8` tolerance;
each best time equals the minimum of its three saved repeats. Eight histories
are present. This is a saved-data consistency check, not a new solver run.

Keep the following distinctions when filling the seven sections:

- **Specify the physical benchmark:** `force_driven(20)` in
  `fem/plate.py` uses a 1 m by 1 m plane-stress square, E = 200 GPa,
  Poisson ratio 0.3, thickness 0.01 m and right-edge horizontal traction
  p = 100 MPa. The left edge is clamped in both components. The equivalent
  line load is t p = 1e6 N/m and the total applied force is 1e6 N.
  There are 441 nodes, 800 triangles and 840 free unknowns. Calling this
  force-driven does not imply that total force stays fixed if thickness is
  changed: the implementation holds p fixed unless the caller adjusts it.
- **Keep stopping protocols attached to results:** the older
  `fem/README.md` reports SD reaching the target at 46,030 iterations for
  the 840-unknown case, using its uncapped textbook implementation. The
  newer progress comparison uses a 20,000-iteration cap and reports SD
  failing to reach the target at that cap. These are distinct runs. For
  the consolidated progress table use `drafts/results/solver_comparison.csv`
  with its saved statuses, rather than combining iteration counts across
  the two protocols.
- **Describe the timing scope:** the saved iterative times include
  method-specific setup inside `iterative` and required stopping checks.
  They exclude assembly, eigenvalue diagnostics, construction of the sparse
  LU reference and history storage. Sparse LU supplies the same-mesh
  solution reference; its runtime is not a measured row in this table.
  The small direct example establishes agreement between LU, inverse and
  Cholesky, not a large-system direct-versus-iterative timing comparison.
- **Distinguish nonzero conventions:** the 840-unknown matrix has 11,112
  stored CSR entries and 9,590 numerical nonzeros under the benchmark's
  relative cutoff. Do not compare stored entries with numerical nonzeros
  from the separate 538-unknown grip case without identifying the convention.

The files named `NLA Seven Section Report.md` and
`NLA Seven Section Report.pdf` in darius-codex's thread message are absent
from this checkout. Their contents and rendering have therefore not been
reviewed here. darius-codex should provide their repository paths/revision
for a review of the consolidated document; the sources listed above remain
the locally available baseline. The opening module's compilation status is
unchanged by this source audit.
