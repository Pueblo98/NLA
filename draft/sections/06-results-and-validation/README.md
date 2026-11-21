# Section 6: Results, validation and discussion

**Status: corrected PR 12 working draft, incorporating imported PR 11 results; standalone PDF built and inspected; team review pending.** Follow the [shared writing rules](../../WRITING_RULES.md) and [Section 6 roadmap](../../ROADMAP.md#6-results-validation-and-discussion). Sections 1–5 are unchanged by this correction.

## Evidence and provenance

The section retains three distinct sources:

- Section 4's original solver measurements, without retiming or replacement.
- The existing **structured-square supplement** in this folder: refinement, diagonal-scaling diagnostics, two fixed-matrix load perturbations and a separate roller-supported affine test.
- Section 5's Triangle object/load/support comparisons, imported from **PR 11 commit `05465395c6615e0b35b9579689c336bdc709252b`**, `notebook/outputs/results/`. The canonical files were read from `/home/kleon/school/nla-pr11-update`, with the committed macOS meshes, not alternative Linux remeshing results.

The imported export records 36 passing physical references and 112 accepted method/system pairs out of 216 across 27 distinct systems. An independent Linux replay of all 30 code cells completed with no errors using the archived meshes; all reference and solver acceptance outcomes match. The report retains the committed macOS timing snapshot rather than substituting Linux timings. [verification.md](verification.md) contains the claim-to-CSV ledger, exact counts, timing correction, snapshot hashes and numeric-key deduplication procedure. It supersedes stale scope/build statements in the historical [review-notes.md](review-notes.md).

## Files and build

- `section.tex`: preamble-free body for inclusion in the report.
- `main.tex`, `build.sh`, `references.bib`: standalone preview sources, numbered as Section 6.
- `preview.pdf`: rebuilt and inspected from the revised source, three standalone A4 pages.
- `generate_evidence.py`, `test_evidence.py`, `requirements.txt`: structured-square reproduction only.
- `reproduction/`: frozen Section 4 assembly, plate and load/support routines, not a second editable implementation.
- `data/`: existing structured-square arrays, diagnostics, generated table and imported Section 4 measurements. PR 11 object results are not copied over them.

Run `sh build.sh` from this directory, with optional `TECTONIC_BIN=/path/to/tectonic`. Python is not needed to compile the committed table. For Overleaf, upload the module contents and select `main.tex`. The standalone wrapper is A4, 11 pt, with 25 mm margins; required packages are `amsmath`, `amssymb`, `graphicx`, `booktabs` and `url`, with `amsplain` bibliography style. During assembly, resolve relative data paths and deduplicate shared bibliography keys. Only the final `clean,onecolumn` build can establish the ten-page limit.

## Reproduce the structured-square supplement

In a virtual environment with `requirements.txt`:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q test_evidence.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python generate_evidence.py
```

These commands are instructions, not newly executed checks. The script uses 5, 10, 20 and 40 cells per side with unchanged material, thickness, full left clamp and full right-edge traction. It does not reproduce the Triangle study. At 20 cells, load perturbations have relative reduced-load norm 0.001: proportional scaling and zero-resultant linear traction redistribution. The latter changes moment and is not the finite-patch location experiment. Neither is a worst-case sensitivity search. The roller affine test is exact only for its separate support condition.

Successive observable differences use the sum of both meshes' algebraic uncertainty estimates. These estimates are not certified bounds and do not establish continuum error or real-material validity.

## Remaining review and attribution

- Resolve the remaining PR 11 numerical failure-handling issues recorded in [the re-review](https://github.com/Pueblo98/NLA/pull/11#issuecomment-6781469036), and integrate the matching builder, exports and archived meshes missing from main.
- Check the final combined report layout and page limit without shrinking typography.
- Resolve permission to substitute the team's assembly routine, physical small-strain validity and final team approval. Material/thickness comparisons and corner-stress convergence are not established.
- Historical execution logs remain attributable to the original structured-square work. This correction is AI-assisted drafting/data review, not human approval. Confirm member contributions and report-level AI-use disclosure before submission.
