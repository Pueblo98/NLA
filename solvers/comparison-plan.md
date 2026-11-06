# Solver comparison handoff

Working agreement from the Slack thread, 6 November 2026. No FEM results
have been reproduced yet. Lucas's Codex owns GMRES, MINRES and the Jacobi
spectral-radius diagnostic; Frambuesa and Ernesto own the formulation and
coupled small example.

## Shared input

Use the draft's plane-stress unit-square case: E = 1, nu = 0.34, thickness
t = 1, n by n nodes, each cell split bottom-left to top-right. Clamp the
left edge and prescribe (0.01, 0) at the middle three right-edge nodes.
Use odd n so that the centre node is unambiguous. State the unit convention.

Supply the assembled K, constrained DOF indices and prescribed values,
free DOF ordering, and reduced A and b. With no applied nodal forces,
A = K_ff and b = -K_fp d_p. Retain K to recover reactions. All comparison
methods must use these same arrays, with x0 = 0.

The square displacement-driven case is the draft reproduction benchmark.
Earlier notes about a force-loaded 2 by 1 rectangle describe a different
experiment and should not be mixed into its solver table.

## Measurement contract

- Target: independently recomputed ||b - A x||_2 / ||b||_2 < 1e-8.
  Since x0 = 0, this equals the agreed ||r||_2 / ||r0||_2 criterion.
  Handle b = 0 separately: return the zero solution with zero iterations
  and absolute residual zero; do not divide by zero.
- Budget: 3000 Krylov iterations. Record GMRES restart length explicitly
  (proposed baseline: 50). Count inner Arnoldi iterations, not restart cycles.
  Check the installed SciPy callback/maxiter semantics before implementation.
- Record the solver's return status AND the independent residual acceptance
  flag. MINRES's native stopping test need not equal this residual threshold;
  a native success flag alone must not mark the shared target as satisfied.
- Use unpreconditioned GMRES and MINRES for this baseline. Label any later
  preconditioned runs separately.
- Report solve time separately from assembly, diagnostics and setup. Collect
  histories in separate runs so residual calculations do not distort timing.
- Compare solutions to a sparse direct reference on the identical system.
  Solver agreement is not a measurement of mesh discretization error.

## Jacobi diagnostic

For symmetric A with positive diagonal D, form the sparse symmetric matrix
S = D^(-1/2) A D^(-1/2). The Jacobi iteration matrix I - D^(-1) A is
similar to I - S. Therefore

    rho_J = max(abs(1 - lambda_min(S)), abs(1 - lambda_max(S))).

Check symmetry and diagonal positivity first. Use dense symmetric eigenvalues
only for small validation cases; use sparse extremal eigenvalue estimates for
larger systems and report eigensolver convergence/tolerance. An estimate near
one needs tighter verification before classifying convergence.

Do not infer rho_J > 1 from the reported run alone. For SPD A, weighted Jacobi
converges for 0 < omega < 2/lambda_max(S); omega = 2/3 is not universal.

## Verification before FEM integration

1. Coupled SPD matrix [[4, 1], [1, 3]] with a manufactured solution:
   verify GMRES/MINRES solution accuracy and independently computed residuals;
   compare rho_J against sqrt(1/12).
2. SPD matrix with diagonal 1 and every off-diagonal entry 0.75 (size 3):
   eigenvalues are 0.25, 0.25, 2.5, so ordinary Jacobi has rho_J = 1.5.
   This checks that SPD is not mistaken for a Jacobi convergence guarantee.
3. Zero RHS and a deliberately exhausted iteration budget: ensure neither
   division by zero nor a false success classification occurs.
4. A problem requiring GMRES restarts: verify inner-iteration accounting and
   enforce the stated total budget.

## Refinement decision

Three adjacent nodes span 2/(n-1) along the unit-square boundary. Keeping
exactly three nodes under refinement shrinks the physical grip. For mesh-error
comparisons, fix its physical interval instead (the n = 17 reference spans
y in [7/16, 9/16]) and refine with those endpoints represented. Preserve the
three-node rule only when reproducing the original individual benchmark.

## Current status

The local repository contains no assembly script or reduced system yet.
Neither the default Python nor the workspace virtual environment currently
has SciPy installed. This file specifies pending implementation and tests;
it is not a solver implementation or a verified FEM result.
