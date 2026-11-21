# Section 7 verification

## Current correction and source scope

Reused the existing PR 12 conclusion at `637911fcd82a8cd4a3f2bd87763c9ac568447e59`, rather than creating a competing conclusion. Read the canonical writing rules, roadmap and Sections 1–6, including the revised Section 6 bridge and limitations. Earlier sections remain unchanged by this task.

The source basis is now Section 4's original measurements, Section 6's preserved structured-square supplement and the **committed PR 11 macOS results at `05465395c6615e0b35b9579689c336bdc709252b`**. The latter were read from `/home/kleon/school/nla-pr11-update/notebook/outputs/results/`, not a newly generated Linux mesh snapshot. Section 6's [verification ledger](../06-results-and-validation/verification.md) supplies exact CSV fields, values, hashes and recount procedure. This conclusion introduces no new experiments.

## Claim-to-evidence review

- **Physical response:** the three geometry rows in `objects_cases.csv` support positive mean extension, rectangle/square ratio **2.0128826014**, opening/square mean increase **12.6278416193%** and half-clamp increases **11.173754566–25.223049426%**. The conclusion no longer attributes the opening's effect to a demonstrated stress-path mechanism.
- **Refinement:** the structured-square means and Triangle square means are about **0.494 mm** with shrinking successive mean changes. The perforated-square final mean change is **0.6620608408%**, versus **0.0338947190%/0.0157166578%** for square/rectangle. This is residual mesh dependence, not measured continuum error, a convergence rate or evidence of corner causation.
- **Load location:** square and rectangle mean extensions vary little between equal-length patches. The opening's lower/middle/upper means are **0.5357793193/0.5844313258/0.5358399959 mm**. Removed the claim that location never changes mean extension. Vertical deflection is explicitly in-plane; no out-of-plane plate-bending result is claimed.
- **Solver acceptance:** four Krylov methods each succeed on **27/27** distinct systems. Ordinary Jacobi diverges and damped Jacobi reaches the cap on **27/27**. Gauss–Seidel **and steepest descent** each succeed on the two coarsest square/opening systems, not on all objects or all coarse meshes. Thus **108 + 2 + 2 = 112** accepted method/system pairs out of **216**. Deduplication must parse the numeric `system_key` tuple before counting; raw string keys overcount.
- **PCG cost:** fewer iterations on all 27 systems, but slower in **26/27** best-of-three comparisons. Finest rectangle: PCG **0.0916805830 s**, CG **0.0921728330 s**, about **0.5%** advantage. Corrected the universal “does not improve time” claim. These tiny differences are not a general performance ranking. Original Section 4 timings remain separate.
- **Validation and sensitivity:** use the existing Section 6 support, balance, same-mesh reference and separate roller-test evidence. Fixed-matrix perturbation amplifications **1.0000000000/1.7662082510** are structured-square results, not cross-object tests. The 36 physical-reference passes were also reproduced by the independent Linux replay recorded in the Section 6 ledger; displayed timings remain the committed macOS measurements.
- **Recommendations:** CG is scoped to the tested supported SPD systems. Stronger preconditioners and local-refinement/stress studies are proposed next steps, not proven necessary or sufficient remedies. No material/thickness comparison or trusted corner-stress prediction is claimed.

## Checks performed and limits

The prose audit used CSV counting, numerical comparisons and read-back of stored evidence. The revised conclusion was then compiled successfully with Tectonic 0.17.0 through the unchanged build script: one A4 page, 11 pt, 25 mm margins. PDF text and layout were inspected, with no unresolved references or text outside the page. This does not certify the final combined report's layout or page limit; numerical replay and failure-injection findings are recorded separately in the Section 6 verification ledger.

The existing `main.tex`/`build.sh` remain the compile entry points. `section.tex` remains preamble-free and introduces no bibliography keys. Delivery is on `docs/pr11-results-update`, based on main `7f8c940`, without changing the notebook or Sections 1–5. Team approval, assembly-routine permission, final physical-model assessment, contribution statements and AI-use disclosure remain open.
