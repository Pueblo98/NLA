# Section 3. Numerical Methods and Comparison Protocol

**Status: simplified for third-year level (10 Nov 2026); AI-assisted working draft for team review, not approved.**
Scope: [ROADMAP entry](../../ROADMAP.md#3-numerical-methods-and-comparison-protocol); style: [WRITING_RULES](../../WRITING_RULES.md).
Body length in the preview: about 1.1 pages (was 1.7). No experimental numbers appear in this section.

## Contents
- Why the SPD, sparse structure of A picks the methods; direct (LU/Cholesky) vs iterative in one paragraph.
- Stationary iterations: residual correction, convergence iff rho < 1, Jacobi radius (eq:solvers-jacobi-radius),
  damped Jacobi (omega = 0.5, interval 0 < omega < 2/lambda_max(S)), Gauss-Seidel.
- Energy view, steepest descent, CG with the A-norm bound (eq:solvers-cg-bound), PCG, MINRES, full GMRES.
- Protocol: acceptance residual (eq:solvers-residual), cap, accuracy vs sparse LU, timing, eigenvalues,
  perturbation bound (eq:solvers-perturbation), algebraic vs discretization error, validation checks
  (prescribed values, force/moment balance, perturbation test, roller patch test).
- Labels: sec:solvers and the four equation labels above. eq:solvers-splitting was dropped (no other section used it).

## Implementation details of the protocol (moved out of the prose)
Code: `solvers/progress_benchmark.iterative(A, b, method, cap, tol, history)` and `METHODS`.
- Acceptance uses an independently recomputed eta; SciPy's native convergence flags are recorded but never
  replace it (its Krylov solvers stop on internal residual estimates). MINRES gets native tolerance 0 and is
  stopped by a callback once eta < 1e-8.
- Iteration = one sweep (Jacobi, damped Jacobi, Gauss-Seidel), one search direction (SD, CG, PCG, MINRES),
  one inner Arnoldi step (GMRES). GMRES uses restart = N, so it never restarts.
- Ordinary Jacobi divergence guard: stop when eta > 1e10 or eta is non-finite. Cap or guard = failure;
  status, iteration count and final eta are still reported.
- Direct reference: `scipy.sparse.linalg.splu` (COLAMD column ordering, partial pivoting); factorization and
  solve timed separately. Small dense system: PA=LU, explicit inverse, Cholesky.
- Timing: best of 3 runs with `time.perf_counter`. Iterative times include method setup and stopping checks;
  they exclude assembly, reduction, eigenvalue diagnostics, the reference solve and residual histories
  (recorded in a separate run). Times compare these SciPy implementations on one machine.
- Eigenvalues: dense `eigvalsh` for small systems; otherwise `eigsh`, tol 1e-10, which='LA' for lambda_max
  and shift-invert about sigma = 0 for lambda_min. Applied to S they give rho_J and the damped-Jacobi limit.
- Patch test: left edge restrained only in x, corner at the origin in y, uniform traction p on the opposite
  edge; exact plane-stress field u_x = p x/E, u_y = -nu p y/E.

## Verification of the protocol code
`python3 draft/experiments/protocol_checks.py` (from repo root) runs
`solvers/progress_benchmark.known_answer_checks()`, checks the divergence guard and damped-Jacobi bound on a
3x3 SPD matrix, and checks the `eigsh` estimators against dense `eigvalsh` on a 40-unknown plate. All pass on
Python 3.13.18, NumPy 2.5.3, SciPy 1.18.1, Linux x86_64. Outputs: `draft/experiments/results/solvers/protocol_checks.{json,log}`.

## Files and open notes
- `section.tex`, `main.tex` (preview; defines Section 2 labels, equations start at 10), `references.bib`, `build.sh`, `preview.pdf`.
- N = |F| is the number of unknowns (Section 2 uses n for nodes).
- Cut from the prose: the h^{-2} growth of kappa (Elman, Silvester and Wathen) and the remark on why the
  diagonal of A varies little on 2D meshes. Section 5 still says it tests "kappa ~ h^{-2} (Section 3)"; it
  should state or cite that expectation itself.
