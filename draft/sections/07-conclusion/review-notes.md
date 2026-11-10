# Section 7 source and continuity review

## Basis

Read the live repository's writing rules, roadmap and complete Sections 1–6 before drafting, using main revision `b138327cb949b5bc63ed10233fec12e37200c9a4`. Sections 5 and 6 are now merged, so their actual bodies, rather than historical placeholder READMEs, supply the basis. Read Section 6's README/review notes and the stored refinement and solver tables as supporting provenance. No predecessor section or numerical dataset is edited.

The open `notebook/initial` PR is separate from the current report sources. This conclusion does not evaluate that notebook or incorporate its claimed additional-object results. “Proposed” and “next step” describe the present Sections 5–6 evidence, not a claim that no collaborator has executed work elsewhere.

## Claim-to-source ledger

| Conclusion claim | Existing source | Qualification |
| --- | --- | --- |
| Square extends and contracts sideways; mean extension approaches 0.494 mm | Section 4 equilibrium paragraph; Section 6 refinement subsection and `data/refinement_rows.tex` | Tested structured meshes, not a certified continuum value |
| CG is a practical starting method for the supported SPD system | Section 2 supported-matrix argument; Section 3 CG motivation; Section 4 solver table | Recommendation among tested iterative methods on the recorded square |
| PCG has fewer steps without a measured time improvement | Sections 4 and 6; Section 4 `data/solver_rows.tex` | Same setup-inclusive protocol; no universal speed ranking |
| Ordinary Jacobi diverges; damped Jacobi and steepest descent exhaust the budget | Sections 4 and 6 solver evidence | These runtimes are not times to the target accuracy |
| LU is an untimed same-mesh reference | Section 3 protocol | No direct-versus-iterative timing claim |
| Support, equilibrium, reference, refinement and affine tests answer different questions | Section 6 validation and limits | Affine exact solution uses rollers, not the clamped benchmark |
| Conditioning worsens while displacements settle; perturbation direction matters | Section 6 refinement and fixed-matrix perturbations | No worst-case direction search or continuum error bound |
| Geometry/load-location/support findings cannot yet be synthesized | Section 5 proposal; Section 6 closing paragraphs | Additional notebook work requires reconciliation into Section 6 first |

These are previously recorded results, not independently rerun calculations in this drafting task. No novel quantitative result, derivation or physical experiment is introduced.

## Continuity decisions

- Section 1 asks about geometry and supports. The conclusion explicitly states which part is answered by the square and which part remains open, without reopening the approved introduction.
- Section 2 supplies the plane-stress assumptions and the sufficiently supported SPD matrix. The conclusion does not extend positive definiteness to the unsupported stiffness matrix or repeat the mechanics.
- Section 3 supplies method definitions and the common protocol. The conclusion gives a qualified recommendation instead of another solver survey, and retains the untimed-reference distinction.
- Section 4 supplies the physical demonstration and solver data. The conclusion omits the parameter register and detailed rankings.
- Section 5 is still a proposed experiment design in the report. Its proposed shapes and support variations are not claimed as findings.
- Section 6 ends with validation boundaries and unfinished studies. The new opening moves from those limits to a concise answer about the square; the final paragraph identifies feasible next steps rather than presenting another results table.

After drafting, reread all six earlier section bodies and check Section 6's ending beside Section 7's opening. Record the final source/PDF checks in `verification.md`. Team review remains pending.

## Earlier-section issues not silently repaired

Section 3 locates the separate affine test in Section 4, whereas the current main report body describes it in Section 6. This conclusion refers to the test without repeating the misplaced cross-reference. Section 6's historical README says Section 5 is not on main; the current main tree does contain it. Section 2 may have newer Slack-only text according to Section 6's review notes. These are integration matters for the earlier sections, not reasons to overwrite their sources here.
