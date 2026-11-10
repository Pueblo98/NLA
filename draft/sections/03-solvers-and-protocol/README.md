# Section 3. Numerical Methods and Comparison Protocol

**Status: AI-assisted working draft for team review (10 Nov 2026); not approved.**
Scope: [ROADMAP entry](../../ROADMAP.md#3-numerical-methods-and-comparison-protocol); style: [WRITING_RULES](../../WRITING_RULES.md).

## Contents
- 3.1 Direct methods: PA=LU, Cholesky, dense factor/solve cost, fill-in, `splu` with COLAMD.
- 3.2 Stationary iterations: residual-correction form (eq:solvers-splitting), Jacobi radius
  via S = D_A^{-1/2} A D_A^{-1/2} (eq:solvers-jacobi-radius), damped Jacobi bound, Gauss-Seidel.
- 3.3 Krylov methods: SD, CG with A-norm bound (eq:solvers-cg-bound), diagonal PCG, MINRES, full GMRES; selection rationale.
- 3.4 Protocol: acceptance residual (eq:solvers-residual), cap/guard/status, iteration conventions,
  accuracy vs same-mesh `splu`, perturbation bound (eq:solvers-perturbation), algebraic vs
  discretization error, timing rules, eigenvalue estimation, validation checks used in Sections 4 and 6.
- No results: this section contains no numbers from experiments.

## Files
- `section.tex` (body), `main.tex` (11pt preview; defines placeholder labels for Sections 2, 4, 6 and
  starts equations at 10 to match the combined numbering), `references.bib`, `build.sh`, `preview.pdf`.
- Body length in the preview: about 1.6 pages (budget 1.25-1.5).

## Verification of the protocol code
`python3 draft/experiments/protocol_checks.py` (from repo root) runs
`solvers/progress_benchmark.known_answer_checks()`, checks the divergence guard and the
damped-Jacobi bound on a 3x3 SPD matrix (Jacobi stops at the guard; omega = 0.5 converges),
and checks the `eigsh` estimators (LA; shift-invert sigma=0; tol 1e-10) against dense `eigvalsh`
on a 40-unknown plate. All pass on Python 3.13.18, NumPy 2.5.3, SciPy 1.18.1, Linux x86_64.
Outputs: `draft/experiments/results/solvers/protocol_checks.{json,log}`.

## Notes and open decisions
- Uses N = |F| for the number of unknowns, because Section 2 uses n for the number of nodes.
- The h^{-2} growth of kappa is cited as for the model Poisson problem (Elman, Silvester and Wathen).
- If the page budget must shrink, candidates are the h^{-2} sentence and the PCG diagonal remark.
