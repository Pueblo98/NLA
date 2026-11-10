# Section 4 verification

## Numerical execution

Executed `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python generate_evidence.py` in an isolated virtual environment. Exit status 0. The wrapper uses unchanged copies of the project's existing FEM assembly, load/support helpers and iterative implementations. Its complete final output is `data/execution.log`; environment, all three timing repeats, statuses and checks are in `data/results.json`.

Passed positive-area and unit-total-area checks; independent nodal load-pattern checks; small-matrix symmetry and positive definiteness; known-answer solver checks; three-repeat solution/status consistency; prescribed displacements; constrained-support-only force and moment balance; and direct-solution residual checks. The large matrix has 840 free unknowns. Five iterative methods met the strict residual target; Jacobi diverged, and damped Jacobi and steepest descent reached the budget without acceptance. These failures are retained in the table and data.

Executed `python verify_artifacts.py` with NumPy and PyMuPDF installed. Exit status 0. Checked frozen implementation hashes, history lengths, strict independent acceptance, minimum-of-three timings, complete Cholesky factors/triangular solves, and exact correspondence of the displayed load vector and coupled first equation to the saved arrays. No continuum-accuracy or general algorithmic-stability claim follows from these checks.

## Compilation and visual checks

Built using Tectonic 0.17.0 through `sh build.sh`, including BibTeX and automatic reruns. Exit status 0. Final compiler log contains no overfull or underfull boxes, undefined citations/references or missing characters.

The exact final PDF is three A4 pages with an 11 pt article wrapper and 25 mm margins. All three final pages were rendered and visually inspected after the last prose/plot changes. Equations, both tables and figure labels fit; the small-mesh annotation overlap was removed. The convergence plot uses a logarithmic iteration axis beyond the first step so the short CG/PCG runs and much longer Gauss–Seidel run can all be read. Text-span horizontal margin checks passed. Bibliography and figure/table references resolve. PDF hash and machine-readable checks are in `data/artifact-verification.json`.

A clean portable copy was compiled outside the repository using the same build script. That build succeeded, and all three rebuilt pages were pixel-identical to the visually inspected original, despite differing PDF file hashes. The source ZIP excludes build caches and Python bytecode and carries the original inspected preview.

This is a standalone preview, not certification of the unavailable final `clean,onecolumn` course template or the combined ten-page report. Sections 1–3 were left unchanged and checked for continuity. Section 3's later review at main a4debf1 was read; its source was unchanged from 9736c8e. Team review, assembly-routine permission and final report integration remain open.
