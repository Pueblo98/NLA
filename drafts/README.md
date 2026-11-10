# Session 22 progress draft: 9 November 2026

> **Historical progress material.** New section-by-section work starts at [draft/README.md](../draft/README.md). The roadmap and writing-rules entry point are there; the existing introduction's editable copy is in [draft/sections/01-introduction/](../draft/sections/01-introduction/). Original files and build paths here are retained for compatibility.

The completed progress submission is **Group02_Draft.pdf**. Its editable source
is **Group02_Draft.md**. This is the November progress deliverable, not the
November 20 final report. The PDF has a standalone progress layout; the final
report must use the required Overleaf `clean,onecolumn` template. No Blackboard
submission has been made by this agent.

## Coverage of the Session 22 checklist

| Checklist item | Draft content |
| --- | --- |
| Objectives, model, supports, matrix and unknowns | Sections 1–3 |
| Small system solved by LU, inverse or Cholesky | Section 4 and Appendix A; all three methods |
| Larger system and iterative methods | Sections 5–6; eight methods on the same 840-unknown system |
| Residuals, iterations, timings, plots, tables and explanations | Sections 6–8, Figures 1–3, Tables 1–3 |
| Questions and next two weeks | Sections 9–10 |
| Sources, contributions and AI disclosure | References and contributions section |

## Results and provenance

`solvers/progress_benchmark.py` generated the new results on 9 November from
the repository FEM, rather than copying the unverified timing table in earlier
prose. The force-driven comparison and the grip-driven case remain separate.

- Small 12-unknown matrix, b and solution: `results/small_*.csv`.
- Environment, unrounded results, all timing repeats, refinement and validation:
  `results/benchmark.json`.
- Raw solver histories: `results/histories.json`.
- Solver comparison: `results/solver_comparison.csv`.
- Execution and check records: `results/run.log`, `results/checks.txt`.
- New residual and refinement figures: `../figures/progress_*.png`.
- Deformation figure: existing Frambuesa/Ernesto force-driven plot, with
  amplification 200 and actual displacement units stated.

CG, GMRES and MINRES reach the target in 242, 228 and 236 iterations.
Diagonal PCG takes 226. Ordinary Jacobi diverges. Damped Jacobi and SD miss the
20,000-iteration cap; Gauss–Seidel takes 19,136 iterations. The draft labels
failures explicitly and distinguishes solver error from mesh error. Timings
are preliminary best-of-three measurements of these implementations.

## Reproduce

Use Python 3.13 and install `drafts/requirements.txt` into a virtual environment.
The original run used NumPy 2.5.4 and SciPy 1.18.1. From `NLA/`:

```bash
python fem/check_fem.py
python solvers/check_system_tools.py
python solvers/check_sparse_system_tools.py
python solvers/progress_benchmark.py
python drafts/build_draft.py
```

The benchmark contains known-answer checks for every method, zero RHS,
one-step GMRES budget accounting, and the SPD/Jacobi counterexample.
It also validates patch-test error, fixed supports and equilibrium on the
computed plate. Histories run separately from timing; MINRES's true-residual
checks are part of its stopping cost. GMRES histories are Arnoldi estimates,
and its final residual is recomputed explicitly. Sparse eigensolvers use a
fixed starting vector and relative tolerance 1e-10.

The renderer rebuilds the PDF from Markdown, including mathematical notation
and figures, and writes page PNGs to ignored `drafts/qa/`. The delivered
nine-page PDF was visually checked at page resolution. Re-running the
benchmark may change times and last digits; update the Markdown tables and
prose before rendering if numerical results change. It does not rewrite the
narrative automatically.

The temporary package directory `.build-deps/`, Matplotlib cache and render QA
images are ignored. They were populated from the existing offline package
cache; dependencies are not vendored into the public project.

## Team handoff and remaining project work

For Hermes, Frambuesa and Claude: this combines Ernesto's formulation and the
existing FEM with a newly executed solver comparison, explicit validation,
questions and a proposed two-week schedule. The professor's provided assembly
routine remains unidentified. General geometries, holes, stronger SPD
preconditioners and a systematic discretization-error study are next work,
not claimed as completed results. Proposed human assignments and unrecorded
contributions are labelled honestly for confirmation in the final report.

Lucas's request to finish the progress draft authorizes this as the finished
version of the progress document for the drafts channel. It does not imply
that every member has already reviewed it or that the final report is done.

## Recovery audit

After the interrupted Slack response, all eight iterative results and the
existing FEM/constraint checks were rerun successfully. See
`recovery-handoff.md` and `results/recovery-checks.txt`. The saved PDF and UTF-8
Markdown sources are intact; the original timing measurements were preserved.
