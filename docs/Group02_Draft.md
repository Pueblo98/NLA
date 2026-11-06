# Elastic Deformation of Two-Dimensional Objects
## Group 02 | Working draft | 6 November 2026

**Review status.** This consolidated draft incorporates Darius's grip example, Ernesto's force-driven plate draft and formulation notes, the shared solver contract, and Frambuesa's proposed work plan. The steel plate is the **proposed main benchmark**, not a recorded final group decision. Numerical FEM results below are **reported, not independently reproduced**. The generating scripts and reduced systems are still required.

**Assignment check pending.** The original Session 22 PDF is not available in this workspace. The five-stage structure and submission dates follow the group's thread summaries; the small-example alternatives and illustrative solver list follow Lucas Codex's reported recheck. Verify these against the actual slide before submission. This draft includes Jacobi, Gauss–Seidel, steepest descent, CG, GMRES and MINRES rather than assuming every listed method is compulsory.

## Stage 1 — Objectives and physical model

We aim to explain the chain **geometry → elastic model → sparse linear system → numerical solution → deformed shape**, and compare direct and iterative methods on identical reduced systems. We will examine how conditioning, mesh size and preconditioning affect accuracy, iteration counts and runtime.

**Main case F: force-driven steel plate (proposal).** A square domain [0,1] × [0,1] m has thickness t = 0.01 m, Young's modulus E = 200 GPa, Poisson's ratio ν = 0.30 and uniform horizontal traction p = 100 MPa on its right edge. These are Ernesto's chosen benchmark values, not verified course-supplied parameters. The left edge is clamped in both directions; top and bottom edges are traction-free. We assume static equilibrium, small strains, homogeneous isotropic linear elasticity, plane stress and no body forces.

For displacement w = (u,v), use engineering strain ε = (u_x, v_y, u_y + v_x), stress σ = D ε, and equilibrium div(σ) = 0. The plane-stress constitutive matrix is

    D = E/(1−ν²) · [[1, ν, 0], [ν, 1, 0], [0, 0, (1−ν)/2]].

Physical traction has units Pa; line load q = t(p,0) has units N/m. On a boundary segment of length ℓ, constant q contributes ℓq/2 to each endpoint. Multiply by thickness exactly once. Total applied force is p t L_y = 10⁶ N in +x.

**Second case G: prescribed grip (separate experiment).** Darius's unit-square model uses E = 1, ν = 0.34, t = 1 in declared model units. Clamp the left edge and prescribe (0.01,0) at the middle three right-edge nodes of a 17 × 17 node mesh; other boundaries are unloaded. It has no applied nodal force. Do not mix its matrix, residual history or timing table with case F. The earlier 2 × 1 force-loaded rectangle remains an alternative proposal, not a third silently substituted baseline.

<!-- pagebreak -->

## Stage 2 — Mesh, assembly and small direct solve

**Mesh and interface.** Start with structured square grids, each cell split into two counter-clockwise linear triangles. Always distinguish n_cells per side from n_nodes = n_cells + 1. Geometry extensions use ordered outer/hole boundaries and constrained triangulation, subject to confirming the brief. Export nodes (N,2), triangles (T,3), labelled boundary edges, material/unit metadata and displacement order [ux0,uy0,ux1,uy1,…]. The ≤14-nonzeros-per-row description belongs to the reported structured mesh; it is not a bound for arbitrary triangulations.

For a triangle of area a_e, assemble K_e = t a_e B_eᵀ D B_e into the full sparse K. Retain the full applied load f and prescribed values d_c. If free indices are f_idx, eliminate constraints symmetrically:

    A = K[free,free];  b = f[free] − K[free,c] d_c;  A x = b.
    Recover d[free] = x, d[c] = d_c;  reactions = (K d − f)[c].

The full unconstrained K is positive semidefinite and, for a connected nondegenerate 2D elastic mesh, has three rigid-body modes. Positive definiteness belongs to A **after sufficient supports remove those modes**. For case F, d_c = 0 and b = f[free]. For case G, f = 0 and b = −K[free,c]d_c. Replacing only constrained rows by identity can destroy symmetry and invalidate solver assumptions.

**Introductory hand example.** Darius's two-triangle square uses E = t = 1, ν = 0, both left nodes fixed, lower-right displacement (0.02,0) prescribed and only the upper-right node free. Its reduced equations are A = diag(0.75,0.75), b = (0.005,0). Cholesky gives x = (1/150,0). This is an explanatory, uncoupled example with different parameters—not the steel benchmark or an iterative-method performance test.

**Coupled small FEM example (to reproduce).** Ernesto reports 2 × 2 cells, 3 × 3 nodes, 8 triangles and 12 free displacement components for case F. This should become the primary direct-method demonstration, with the actual A and b supplied.

| Direct method | Role | Reported relative residual |
| --- | --- | --- |
| PA = LU | General pivoted factorization/reference | 6.1e−16 |
| Cholesky A = LLᵀ | Exploits verified SPD structure | 5.3e−16 |
| Explicit A⁻¹b | Optional tiny-system illustration only | 6.0e−16 |

**All three entries are provisional source results.** The source also reports κ₂(A) ≈ 95.8. Do not form a large sparse inverse. Session 22 was reported to permit LU, inverse **or** Cholesky; showing all three is a pedagogical choice, not a verified requirement.

<!-- pagebreak -->

## Stage 3 — Iterative methods and comparison protocol

Write A = D_A + L_A + U_A and r_k = b − A x_k. Here D_A denotes the matrix diagonal, not the constitutive matrix. These methods solve the **same supported system** with x₀ = 0.

| Method | Update or defining idea | Suitability and limitation |
| --- | --- | --- |
| Jacobi | x_new = x + D_A⁻¹ r | Converges iff ρ(I−D_A⁻¹A) < 1; SPD alone is insufficient. |
| Gauss–Seidel (GS) | (D_A+L_A)x_new = b−U_A x | Converges for SPD A; ordering and implementation affect performance. |
| Steepest descent (SD) | α = (rᵀr)/(rᵀAr); x_new = x+αr | SPD quadratic-energy descent; often slow when ill-conditioned. |
| Conjugate gradients (CG) | A-conjugate Krylov search directions | Natural SPD baseline; short recurrences and low storage. |
| GMRES | Minimize residual over Arnoldi Krylov space | General nonsingular A; orthogonalization/storage grow without restart. |
| MINRES | Symmetric Lanczos residual minimization | Suitable for symmetric A, including indefinite cases; independently check stopping. |

**Extensions.** Weighted Jacobi uses x_new = x + ωD_A⁻¹r. With S = D_A⁻¹ᐟ² A D_A⁻¹ᐟ², convergence for SPD A requires 0 < ω < 2/λ_max(S). Compute extremal eigenvalues and ρ_J = max(|1−λ_min(S)|, |1−λ_max(S)|); do not infer a spectral radius from SPD or from a diverging run alone.

Diagonal PCG uses the SPD preconditioner M = diag(A), applying M⁻¹r componentwise. Verify positive diagonal and SPD assumptions. A genuine incomplete-Cholesky extension is optional if supported by the environment. **SciPy spilu is incomplete LU, not incomplete Cholesky**; its generally nonsymmetric preconditioner is not a default CG-compatible choice. Test ILU with GMRES separately instead.

**Common acceptance rule.** Recompute η = ||b−Ax||₂/||b||₂ and require η < 1e−8. Record native return status and this independent acceptance flag. For b = 0 and x₀ = 0, return the zero solution with zero iterations and zero absolute residual; relative residual is undefined. Record solution difference ||x−x_ref||₂/||x_ref||₂ when the reference norm is nonzero.

**Budgets and implementations.** Preserve the historical protocols: case F used 20,000 iterations; case G used 3,000. Proposed new common baseline: 3,000 iterations, with separately labelled 20,000-iteration follow-ups for slow methods, pending team agreement. GMRES baseline restart is proposed as 50; record Arnoldi inner iterations, cycles and total budget. A full-GMRES reproduction is a different run. Verify installed SciPy callback/maxiter semantics. MINRES native success alone does not establish the shared residual target; document any tighter tolerance, extra solve or custom stopping logic.

**Timing.** Use separate history and timing runs. Record versions, hardware, matrix size/nonzeros, setup time, solve time, repetitions and timing statistic. Compare median solve times under the new protocol; do not silently relabel earlier best-of-three measurements.

<!-- pagebreak -->

## Stage 4 — Initial results and what is actually verified

### A. Reported case F results — NOT REPRODUCED

Source: Ernesto's draft, 20 × 20 cells = 21 × 21 nodes, 840 free unknowns, 11,112 nonzeros, reported κ₂(A) ≈ 9,100. Initial guess zero, target 1e−8, cap 20,000. Times are source **best of three** and include residual calculation every iteration; setup-time separation is not documented. The generating script, versions and full-GMRES/MINRES stopping details are missing.

| Method | Iterations / outcome | Final rel. residual | Difference vs direct | Source time, ms |
| --- | --- | --- | --- | --- |
| Jacobi | Diverged; stopped at 49 | 1.3e10 | 3.4e7 | 1.3 |
| Weighted Jacobi, ω=0.5 | 20,000; capped | 4.8e−6 | 8.7e−5 | 542 |
| GS | 19,136; reported target | 1.0e−8 | 1.7e−7 | 7,806 |
| SD | 20,000; capped | 3.1e−6 | 4.2e−5 | 300 |
| CG | 242; reported target | 9.2e−9 | 9.7e−10 | 7.1 |
| GMRES, described as full | 228; reported target | 9.5e−9 | 6.0e−9 | 149 |
| MINRES | 236; reported target | 9.4e−9 | 5.9e−9 | 15.0 |

The rounded GS value does not prove a strict <1e−8 pass. The table reports GMRES with fewer iterations than CG; CG has the lowest reported successful solve time and solution difference. Neither observation establishes a reproduced ranking. Timing includes implementation effects, particularly the source's triangular solve on every GS sweep.

| Case F refinement (cells/side) | Free unknowns | Reported κ₂ | CG steps | SD steps |
| --- | --- | --- | --- | --- |
| 10 | 220 | 2,469 | 120 | 14,202 |
| 20 | 840 | 9,104 | 242 | 46,030 |
| 40 | 3,280 | 34,548 | 469 | 149,816 |

These source SD refinement runs used a budget larger than 20,000. The apparent conditioning/iteration trend is a hypothesis to reproduce, not a verified scaling law.

### B. Separate case G source results — NOT REPRODUCED

Darius's PDF reports 17 × 17 nodes, 538 free components and 6,054 stored nonzeros. With a 3,000 cap: Jacobi stopped at 25 with η = 1.43e6; GS reached η = 9.97e−9 in 2,435 steps; SD capped at η = 3.12e−6; CG reached η = 6.80e−9 in 178 steps. These are not comparable to the case F table. GMRES/MINRES reproduction remains pending.

### C. Verified progress in this draft preparation

Both repository scripts ran successfully: `solvers/check_system_tools.py` and `solvers/check_sparse_system_tools.py`. They cover consistent edge-load force/moment under refinement, nonzero constraints, support loads, duplicate-edge rejection, CSR reduction, sparse solve, reactions, input preservation and dense/sparse agreement. **These are synthetic utility checks, not FEM assembly or table reproduction.**

<!-- pagebreak -->

## Stage 4 continued — Validation, figures and open questions

**Algebraic checks.** Verify finite entries, connectivity/orientation, matrix symmetry and elimination ordering. Check the expected three rigid modes before supports and positive definiteness of the small supported A. Use a sparse direct solution as the reference for each identical A,b. Check zero RHS, a deliberately exhausted budget and GMRES restarts. A solver success flag, low relative residual and low solution error are different statements.

**Physical checks.** Reconstruct prescribed displacements exactly and recover reactions from the retained full system Kd−f. For case F, applied plus reaction forces and their moments must balance. State normalized tolerances and units in the eventual check output. Double the load on the same linear model and verify doubled displacement/reactions to solver tolerance; this tests implementation linearity, not validity at arbitrary loads.

**Exact verification variant—not the clamp solution.** Replace the left clamp by u(0,y)=0 and pin v(0,0)=0, leaving other left-edge vertical displacements free. Uniform traction then admits u=px/E, v=−νpy/E. Linear triangles should reproduce this affine field to numerical tolerance. It must not be presented as an exact solution for the fully clamped plate.

**Refinement.** Keep geometry, traction, thickness, material and supports fixed for case F. For case G, the three-node grip shrinks if its node count is held fixed. For mesh-error experiments preserve the physical interval y ∈ [7/16,9/16], with represented endpoints. Preserve the three-node rule only in individually labelled reproduction runs. Compare displacement at matching physical points or use an explicitly defined transfer between meshes; direct/iterative solver agreement is not discretization error.

**Figures to generate from reproducible arrays.** (1) labelled undeformed mesh/supports/loads; (2) true residual versus counted iteration for each case, with tolerance and cap visible; (3) deformed mesh annotated with the chosen amplification factor and units; (4) condition estimates and iteration counts versus free unknowns. The existing PDFs contain source figures, but their curves are not regenerated here. No synthetic convergence or deformation figure is substituted for missing data.

**Open questions for the group / feedback session**

- Confirm the main benchmark: proposed steel square, separate grip case, and whether the earlier 2 × 1 rectangle is still needed. Confirm benchmark values versus any supplied FEM routine assumptions.
- Export Ernesto's original script and Darius's generating script, or explicitly document an independent reconstruction. Obtain the course FEM routine; disclose a replacement if required.
- Confirm budgets, GMRES restart and MINRES stopping implementation before comparing methods. Recompute the source Jacobi spectral-radius and damping claims from A; do not carry them over unverified.
- Decide whether diagonal PCG is sufficient or whether a real SPD incomplete-Cholesky implementation adds useful evidence. Treat larger meshes and the plate-with-hole as extensions after the baseline works.
- Investigate coarse-mesh asymmetry by changing diagonal orientation; do not promise that a particular split removes it without testing. Avoid using peak clamped-corner stress as the primary mesh-convergence measure.
- Check the original Session 22 wording, deadline, page limit, template, notebook and AI-disclosure requirements. Thread summaries report draft 9 November, final report/notebook 20 November and presentation 27 November.

**Interpretation to test.** For well-shaped meshes and fixed physics, worsening conditioning under refinement can slow stationary/gradient methods. CG should exploit the SPD structure efficiently; the measured benefit of PCG must be demonstrated. Residuals alone do not establish physical validity or displacement accuracy.

<!-- pagebreak -->

## Stage 5 — Two-week plan, responsibilities and deliverables

**Before the Monday draft (6–8 November).** Retrieve the Session 22 PDF and both generating scripts; agree case F/G labels and ownership; obtain or document the assembly routine. Export the small coupled A,b and produce a direct reference. Rerun available methods and replace provisional rows only with saved evidence. Regenerate the mesh, deformation and convergence figures if inputs arrive; otherwise submit explicitly labelled preliminary results and questions, not invented replacements.

The dates below are the proposed work schedule. Submission dates follow thread summaries and remain subject to checking the assignment. Ownership is proposed from prior handoffs, not an instruction that another agent has already accepted.

| Date | Lead / collaborators (proposal) | Output and completion check |
| --- | --- | --- |
| Mon 9 Nov | Darius + all | Review and submit Group02_Draft.pdf after source/deadline check; record feedback and decisions. |
| Tue 10 Nov | Ernesto/Frambuesa + Lucas/Codex | Finalize docs/model.md and docs/interfaces.md; validate small assembly, supports, exact roller case and reactions. |
| Wed 11 Nov | Pablo + Lucas/Codex | Reproduce six iterative methods on one saved A,b; log true residuals, budgets, versions and GMRES/MINRES semantics. |
| Thu 12 Nov | Pablo + Darius | Fixed-physics 10/20/40-cell studies; separate algebraic and mesh error; compare CG with diagonal PCG including setup cost. |
| Fri 13 Nov | Simon/Hermes + solver team | Geometry/mesh figures; attempt hole mesh and 80/160-cell runs only after baseline checks pass and memory/runtime are assessed. |
| Mon 16 Nov | Darius + all | Freeze benchmark definitions and result data; decide which extensions add evidence; review consistency of every figure/table. |
| Tue 17 Nov | Ernesto/Frambuesa + Lucas/Codex | Complete model/method sections, derivations, validation evidence and limitations. |
| Wed 18 Nov | Darius + Pablo + Simon | Assemble report in required template; rebuild figures from saved data; run notebook from a clean kernel. |
| Thu 19 Nov | All | Independent scientific/editorial review; check citations, contributions, AI-use statement and stated page limit (reported as ≤10). |
| Fri 20 Nov | Designated human submitter + all | Final clean notebook run, report/PDF checks and submission confirmation; archive exact code/data version. |

**After the two-week window.** Prepare/refine slides and rehearse during 23–26 November for the reported 27 November presentation. A roughly three-minute contribution per member is a planning target, pending presentation instructions. Everyone should be able to explain the full model and solver choices.

**Fallback priorities.** If original scripts remain unavailable, label a rebuild as an independent implementation and compare outputs only after specifying identical inputs. If time or resources are limited, prioritize a validated small example, a reproducible moderate-size table and honest limitations over 160-cell runs or extra geometries. Do not postpone the core report for optional extensions.

**Sources and evidence.** Primary project drafts read directly: *Elastic Sheet NLA Project Draft* (5 pages, Darius) and *Project Draft: Elastic Deformation of a 2D Plate* (8 pages, Ernesto). Repository references: `notes/ernesto-draft-force-driven.md`, `notes/physical-model.md`, `solvers/comparison-plan.md`, `solvers/assembly-solver-interface.txt` and both utility-check scripts. Frambuesa's thread contribution supplies the proposed Stage 3–5 handoff and schedule; Lucas Codex's earlier recheck supplies the reported Session 22 wording corrections. Original course documents are not republished here.

**AI-use / contributions (working disclosure).** This consolidated text was prepared with Hermes using the above human/agent contributions. AI-assisted drafting, formulation notes and historical numerical outputs must be disclosed according to course policy. A human-reviewed contribution table and attribution of the actual implementations remain to be finalized. Verified utility checks do not validate the historical AI-generated FEM results.
