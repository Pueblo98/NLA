# Section 6 verification

## Source scope and continuity

Read the canonical writing rules, roadmap and Sections 1–4 at main `8aefb2a5d5fc6745b358c32c537afc14160828d1`, plus Section 5's actual source and specification at `005a260d47b7021939782658257d0d2e99fe791e` on its review branch. The earlier texts were revisited after drafting for the Section 5/6 transition, notation and overlap. Final remote checks found both source revisions unchanged. A scoped Git diff confirms that Sections 1–5 are unchanged by this task. These are still working drafts, not final approved text.

## Actual numerical execution

Executed the new square-only script and reran all tests locally with Python 3.14.4, NumPy 2.5.4 and SciPy 1.18.1, with BLAS/OpenMP thread counts set to one. Final pytest result: **5 passed**. The four mesh levels, two perturbations and separate roller exact-solution check executed successfully; `data/execution.log` and `data/evidence.json` contain the actual outputs. Frozen implementation copies were checked byte-for-byte against the Section 4 files. No new solver timings or Section 5 object-family experiments were run.

The parent review caught an initial mismatch in the spectral diagnostic: the drafting subagent had selected an optimal Jacobi damping parameter instead of Section 3's measured weight 0.5. An added regression assertion failed on that mismatch (`data/protocol-red.log`). The calculation and its recorded definition were corrected to 0.5, all five tests passed, and the complete evidence was regenerated. Historical TDD logs describe intermediate development, not the final experiment. The committed `data/execution.log` and `data/evidence.json` supersede those intermediate outputs.

Independent read-back checks reconstructed the saved sparse matrices, recomputed the reference residuals and observable values, verified constrained-only reactions and prescribed values, positive triangle areas and unit total area, checked source hashes, and recomputed the algebraic uncertainty estimates. Every successive difference for the three observables exceeds its summed estimate by more than one million. The estimates are not certified bounds. An additional reconstruction of Section 4's n=20 LU reference agreed with its archived displacement; its true relative residual was `3.8338007936838075e-14`.

Imported solver measurements are retained byte-identically in `data/imported_section4_results.json`. Checks confirmed strict residual acceptance and minimum-of-three timing selection. They were not retimed. The optional companion plot is generated from the new refinement data; the main section uses the compact table instead of repeating the same data in a figure. `data/refinement_rows.tex` is a rounded rendering of `data/evidence.json`; after rerunning experiments, refresh its values if the underlying observations change.

## Exact PDF checks

Built `main.tex` through `TECTONIC_BIN=/path/to/tectonic sh build.sh` using Tectonic 0.17.0, including BibTeX and reference reruns. Exit status 0. The final compiler log contains no overfull/underfull boxes, undefined references/citations or missing characters.

The final preview is **two A4 pages**, in the same 11 pt article wrapper and 25 mm margins used by earlier sections. Both pages were rendered and visually inspected after the final prose changes. The table, displayed sensitivity equation and references fit without clipping or overlap. Automated horizontal text-margin checks passed. PDF and source hashes plus numerical read-back checks are recorded in `data/delivery-verification.json`.

This verifies the standalone preview, not the combined report in the final course template. It does not establish continuum accuracy, real-material validity, cross-object findings, general solver rankings or team approval. Remaining decisions are listed in the README and review notes.
