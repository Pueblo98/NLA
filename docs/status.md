# Project status and handoff

## Snapshot

Coordination bootstrap based on the repository and project thread on 6 November 2026. This document is not evidence of a completed FEM implementation or a final baseline decision.

The inspected main branch contains README.md, directory placeholders in mesh/, fem/, figures/, notebook/, solvers/ and validation/, and solvers/comparison-plan.md. The comparison plan is a specification, not executable solver code. No end-to-end FEM solve was verified in this bootstrap.

## Shared documentation

Use docs/ for shared documentation:

- docs/status.md: this handoff.
- docs/interfaces.md: pending mesh / assembly / solver contract.
- docs/model.md: pending physical formulation and assumptions.
- Root AGENTS.md: repository-wide working guide.

Do not duplicate these shared files under notes/.

## Baseline decision required

The committed solvers/comparison-plan.md proposes:

- Plane stress on a unit square, E = 1, nu = 0.34, thickness = 1; unit convention must be stated.
- n by n nodes, each cell split from bottom-left to top-right; odd n.
- Clamp the left edge; prescribe displacement (0.01, 0) at the middle three right-edge nodes.
- No applied nodal forces: A = K_ff, b = -K_fp d_p, with retained full K for reactions.
- Shared reduced arrays for direct-reference and iterative comparisons, with independent residual verification.
- A distinction between reproducing a three-node grip and keeping a fixed physical grip interval during refinement.

Earlier thread planning used a different case: a 2 by 1 rectangle clamped on the left with a line load q on the right. That is force-driven, not the displacement-driven square above. Do not combine the geometry of one with the boundary conditions of the other or merge their results into one solver table.

The group must confirm the baseline and whether both cases are needed, check the source brief/draft, and record the authoritative model before integration. The comparison plan's references to a draft have not been independently validated by this bootstrap.

## Work handoffs reported in the thread

- Hermes: mesh / geometry handoff and shared coordination bootstrap.
- Frambuesa + Ernesto: physical formulation and docs/model.md, subject to Ernesto's authorization for their clone operations.
- Lucas Codex: latest thread offers assembly / supports and interface notes. The committed comparison plan also names Lucas Codex for GMRES, MINRES and the Jacobi diagnostic, while the thread associates solver comparison with Pablo. Reconcile ownership explicitly rather than assuming those allocations match.

These are reported coordination intentions, not verified completed deliverables. Preserve other teammates' agreed roles; use Issues/PRs to make concrete assignments and acceptance checks visible.

## Open inputs and integration checks

- Obtain or locate the course FEM routine and verify its actual input/output conventions.
- Confirm material values, units, thickness, plane-stress versus plane-strain choice, and boundary conditions for the chosen baseline.
- Obtain a usable export of Ernesto's model notes if still required; the earlier PDF was reported blank apart from its heading.
- Agree node/element formats, indexing, orientation, labelled boundaries, DOF order, prescribed values and reduced-system export in docs/interfaces.md.
- Run and report assembly, support elimination, reactions/equilibrium and solver acceptance tests on the same case.
- Agree dependencies and reproducible run/test commands after executable code is added.

## Collaboration

Each agent verifies its own authentication and target branch. Prefer a task branch and reviewed PR. Successful read access or an API permission flag alone is not a verified push. Do not assume another agent's runner targets a safe branch. Fetch before starting and avoid overwriting concurrent changes.

The repository was public when inspected; the owner should confirm that visibility before restricted course material or personal data is uploaded. Never commit credentials.
