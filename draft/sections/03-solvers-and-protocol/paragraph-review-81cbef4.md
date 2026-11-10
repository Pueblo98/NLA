# Section 3 paragraph and PDF review

Lucas's Codex, 10 November 2026. Reviewed Hermes's PR [#4](https://github.com/Pueblo98/NLA/pull/4), commit [`81cbef470047c21096ef83c7fc6924344fadb6d7`](https://github.com/Pueblo98/NLA/commit/81cbef470047c21096ef83c7fc6924344fadb6d7). This supplements the earlier implementation audit; it does not mark the report final or merge the PR.

## Verdict

The draft is readable, follows Section 2 naturally and accurately describes the recorded solver comparison. No major mathematical or protocol blocker was found. Two small edits to the accuracy paragraph are recommended before integration. A ready-to-apply [patch](../../../notes/section3-review-81cbef4/suggested-edits.patch) is provided for Hermes; the reviewed source remains unchanged.

## Requested edits

1. **Distinguish load sensitivity from solver stability** (`section.tex`, lines 116–120). Changing the right-hand side at fixed matrix measures sensitivity to input data, hence conditioning in the tested direction. That experiment alone does not establish an algorithm's stability under floating-point rounding. Replace the sentence grouping all these checks under numerical stability with: “Residuals, reference agreement and termination behaviour provide practical checks on solver reliability. A separate load-perturbation experiment probes sensitivity at fixed $A$.” Retain the caution about one direction not measuring worst-case sensitivity.
2. **Remove the implemented-zero-reference claim** (line 114). The current benchmark computes `norm(x-ref)/norm(ref)` unconditionally; it has no absolute-error fallback. The current nonzero-load results are unaffected. Delete “For a zero reference we use the absolute difference.” If zero-load cases are added later, implement absolute reference differences and guard the outer residual calculation as well. The iterative solver's existing early zero-RHS return is correct, but does not guard those outer calculations.

These edits concern interpretation and an untested edge-case claim, not a request to regenerate the current nonzero-load experiments.

## Readability and continuity

- Reread all of Sections 1 and 2, including Section 2's ending. It closes with supported positive definiteness, conditioning and a solver transition; Section 3 immediately uses those properties. No repeated assembly or mechanics derivation is needed.
- The progression from direct methods through stationary methods, CG/preconditioning and the residual-minimizing comparisons is understandable. Symbols and the four displayed equations are introduced in context.
- Timing and stopping details are dense but relevant to reproducing the existing implementation. Leave numerical tables and case specifications to Sections 4 and 6.
- At final integration, replace hard-coded section numbers with LaTeX cross-references and check the combined course-template page budget. This is integration work, not a defect in the standalone preview.

## Protocol fidelity

Checked the full draft against `solvers/progress_benchmark.py`. The local benchmark code and Section 2 source were also fetched at the reviewed commit and are byte-for-byte identical to this checkout.

The following match: eight iterative methods; a common reduced system and zero initial guess; strict independently recomputed residual acceptance below $10^{-8}$; the 20,000-iteration cap; damping 0.5; diagonal PCG applying the inverse diagonal; full GMRES and legacy inner-step counting; Arnoldi residual estimates distinguished from true residuals; MINRES's true-residual callback target; divergence and non-convergence reporting; minimum of three setup-inclusive iterative times; separately collected histories; and the untimed sparse-LU reference. The treatment of solver error versus discretization error, reactions, and the separate roller-supported affine test is appropriate.

This review inspected existing code and results rather than rerunning FEM experiments or timings. It carries forward the earlier saved-results consistency audit without claiming new measurements.

## PDF inspection and provenance

Retrieved the committed source files and PDF using the GitHub connector, pinned to the full commit above. Preserved them in [the review input snapshot](../../../notes/section3-review-81cbef4/inputs/) with their GitHub blob SHAs in `manifest.json`. All seven files passed an independent Git blob SHA-1 calculation.

Rendered and visually inspected every page of the unchanged committed PDF using the existing project PyMuPDF dependency. It has three A4 pages: two pages of section text and one bibliography page. Equations (1)–(4), citations [1]–[3], headings, page numbers and text are legible. No clipping, overlap or unresolved citation/reference marker was observed. The third reference has loose word spacing, but stays within the margins and is readable. The bibliography will be consolidated in the final report.

No independent LaTeX rebuild was completed here; compilation evidence remains Hermes's `verification.md`. Inspection of a committed PDF and its source does not independently prove the build process. After applying the proposed paragraph edits, Hermes should rebuild and inspect the updated preview before replacing it.

## Handoff

Hermes: apply the two small edits, rebuild the preview and recheck its pages. Darius-codex: use PR #4 as the identified review source; any remaining independent observations should refer to its commit or a successor. Lucas's Codex has completed this paragraph-level and visual review. Team approval and final-template pagination remain pending.
