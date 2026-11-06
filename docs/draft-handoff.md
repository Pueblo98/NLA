# Consolidated draft handoff

## Deliverables

- `docs/Group02_Draft.md`: editable consolidated six-page draft source.
- `docs/Group02_Draft.pdf`: rendered working draft for group review, not a confirmed submission-ready PDF.

## Scope and sources

Combines the two cached project-draft PDFs, the repository formulation/results notes and assembly/solver specifications, and the thread's proposed two-week schedule. Original restricted PDFs and course materials were not added to the repository.

The proposed main case is Ernesto's force-driven square steel plate. Darius's grip case remains a separate experiment. Baseline choice, numerical benchmark parameters and new comparison budgets are not presented as settled group decisions. The original Session 22 PDF remains unavailable; its exact instructions and submission dates require verification.

All historical FEM tables remain explicitly marked reported/not reproduced. No convergence/deformation figure has been invented or substituted for absent data. The original generating scripts and shared reduced matrices/RHS have not been exported to this checkout.

## Actual checks performed

Environment used for utility checks: Python 3.11.15, NumPy 2.4.6, SciPy 1.17.1, installed in an isolated `uv run` environment rather than changing system Python.

Commands:

```sh
uv run --with numpy --with scipy python solvers/check_system_tools.py
uv run --with numpy --with scipy python solvers/check_sparse_system_tools.py
```

Actual output:

```text
PASS: load refinement, moment, nonzero constraints, support loads, duplicate rejection
PASS: CSR reduction, sparse solve, reactions, unchanged inputs, dense agreement
```

These checks verify the existing load/constraint utilities on synthetic systems. They do not verify FEM assembly, the reported solver rankings, the Jacobi spectral-radius claims, or any historical figure/table.

PDF checks: generated successfully with ReportLab, opened with PyMuPDF, six pages; stage headings, provenance notices, dates and preconditioner correction were found in extracted text; all extracted text blocks were inside page margins. Iterative-method and plan pages were visually inspected for table/paragraph clipping. `git diff --check` also passed.

## Scientific corrections retained

- Distinguish full semidefinite K from supported SPD A = K_ff.
- Keep force/traction units and thickness consistent; retain full loads for reactions.
- Do not combine force-driven and prescribed-displacement results.
- Preserve the historical 20,000 and 3,000 iteration budgets as separate protocols.
- Independently verify true residuals, GMRES inner-iteration counting and MINRES stopping.
- Do not confuse `spilu` (incomplete LU) with incomplete Cholesky or assume its preconditioner is CG-compatible.
- Describe row sparsity as mesh-specific and distinguish solver error from mesh error.

## Remaining actions before submission

1. Reattach/read the original Session 22 slide and confirm dates/template/page limits.
2. Confirm benchmark and responsibility allocations with the group.
3. Export original scripts and reduced A,b, or explicitly authorize/label an independent rebuild.
4. Reproduce small FEM validation and iterative tables; regenerate figures from saved arrays.
5. Replace provisional evidence only after actual reruns; finalize human contributions and AI-use disclosure.

This handoff complements the coordination files proposed separately in PR #1; it does not duplicate or overwrite its pending `docs/status.md`.
