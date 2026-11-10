# Section 6 source review and evidence boundaries

Initial drafting review by Hermes, subject to team review. This note is not a replacement for `../../WRITING_RULES.md`.

## Sources read before drafting

- Live `origin/main` at `8aefb2a`: the canonical writing rules and roadmap, all of Sections 1–4, the Section 2 review history, Section 3 verification/protocol, and Section 4 source, reproducibility code and stored results.
- Section 5 is not yet integrated into that main revision. Its actual initial draft, README and `cases.json` were read from `origin/docs/section5-initial-draft` at `005a260d47b7021939782658257d0d2e99fe791e` (PR #7). This is the latest accessible Section 5 draft, not merely its empty main-branch handoff.
- Section 2's review notes refer to an even shorter Slack attachment that is not the committed `section.tex`. This task uses the accessible GitHub source, without claiming that it is the latest uncommitted attachment. No earlier section is rewritten.

## Continuity and consistency decisions

Section 5 ends by distinguishing checked physical observables, mesh dependence, linearity, directional sensitivity and unresolved modelling decisions. Section 6 starts by separating completed square evidence from the proposed additional-object study, then reports physical mesh dependence, solver interpretation, a fixed-matrix sensitivity diagnostic and validation limits. The introductory elasticity explanation, material law, element assembly and solver definitions stay in their existing sections.

All new baseline measurements use the Section 4 force-driven square, not the prescribed-displacement grip case. Material, plane-stress convention, traction, thickness and complete left clamp stay unchanged. Increasing the structured cell count preserves the same physical load and support boundary. This is a new square-only diagnostic extension, not execution of Section 5's Triangle-meshed geometry comparisons. The roller-supported exact affine test is separately identified and cannot supply an exact solution for the clamped square.

Only the supported matrix is described as positive definite. The diagonal scaling used for conditioning is the symmetric matrix `P^(-1/2) A P^(-1/2)`, not a claim that nonsymmetric `P^(-1) A` has the same Euclidean condition number. Uniform scaling of the load tests linearity; a zero-resultant redistribution tests one different load direction and changes its moment. Neither is a worst-case sensitivity search or a general floating-point stability test.

## Evidence ledger

| Material | Status and permitted use |
| --- | --- |
| Section 4 `data/results.json` | Imported previously executed benchmark, including all timings, statuses and residual/reference differences. Not retimed for Section 6. |
| Section 4 `numerical-review/verification.json` | Previously reported independent handoff, useful as a consistency check; not substituted for the main timing dataset. |
| Section 6 `generate_evidence.py` outputs | New square-only refinement, spectral, perturbation and validation measurements; claims require successful execution and final artifact verification. |
| Section 5 geometries, patch-load and half-clamp comparisons | Proposed, unexecuted by this task. No cross-object rankings or deformation plots claimed. |
| Material and thickness variations | Not part of the present Section 5 register. No measured conclusions; require an agreed physical loading convention and future execution. |
| Small-strain linear elasticity | Working modelling assumption, not experimentally validated by numerical equilibrium checks. |

The physical observables use sparse-LU solutions that pass the prescribed support, residual, force and moment checks. Reactions are restricted to constrained components; free-row residuals are checked independently. Refinement uses edge integrals and the same physical midpoint, with absolute differences to avoid division by a near-zero vertical component. Algebraic uncertainty estimates use the actual observable weights and estimated smallest eigenvalue; these are diagnostics, not certified continuum-error bounds.

## Items left for team review

1. Approve or revise the additional-object register and execute it before drawing cross-object, support-location or load-patch conclusions.
2. Reconcile the final committed Section 2 text with any newer Slack-only revision, and recheck Section 3 if its protocol changes.
3. Resolve permission to use the team assembly routine instead of the course-provided routine.
4. Review the square-only refinement and chosen linear load-redistribution diagnostic; these do not silently replace Section 5's proposed experiments.
5. Confirm physical validity, any material/thickness study, report-level member contributions and AI-use disclosure.
6. Integrate into the actual course `clean,onecolumn` template, remove overlap with Section 4 and check the combined ten-page limit. The standalone preview is not that final layout.
