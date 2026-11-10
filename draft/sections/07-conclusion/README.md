# Section 7: Conclusion

**Status: corrected PR 12 working draft; standalone PDF built and inspected; team review pending.** The scope is the [Section 7 roadmap](../../ROADMAP.md#7-conclusion), following [WRITING_RULES.md](../../WRITING_RULES.md). This correction changes Sections 6/7 only, not Sections 1–5.

## Source and evidence

The conclusion synthesizes the revised Section 6, with the original Section 4 measurements and structured-square supplement kept separate from imported object results. The additional-object/load/support evidence is the **PR 11 macOS snapshot `05465395c6615e0b35b9579689c336bdc709252b`**, audited at `/home/kleon/school/nla-pr11-update/notebook/outputs/results/`. It is distinct from a newly generated Linux mesh snapshot, and the canonical timing snapshot is retained. A separate Linux replay using the archived meshes reproduced all reference and solver acceptance outcomes; see the Section 6 verification ledger.

[verification.md](verification.md) maps the corrected claims to the audited data and supersedes historical scope/build statements in [review-notes.md](review-notes.md). In particular, load-location invariance is not generalized to the perforated square, PCG's timing result includes its one slight advantage, and the two accepted steepest-descent runs are retained alongside the two Gauss–Seidel successes. Physical-reference passes remain attributed to the export.

## Files and build

- `section.tex`: preamble-free body for inclusion in the report.
- `main.tex`, `build.sh`: standalone preview wrapper and portable build.
- `preview.pdf`: rebuilt from the revised source and visually inspected, one standalone A4 page.
- `verification.md`: current source/data audit and explicit build boundary.

Run `sh build.sh` from this directory, with optional `TECTONIC_BIN=/path/to/tectonic`. For Overleaf, upload the source and select `main.tex`. The wrapper uses A4, 11 pt and 25 mm margins. It does not certify the final `clean,onecolumn` layout or the assembled ten-page limit. The conclusion introduces no figures, equations or bibliography entries; retain earlier sections' citations and the report's `amsplain` bibliography.

## Outstanding review and integration

- Keep the canonical macOS timing snapshot separate from the independently replayed Linux verification.
- Verify final combined-report layout and page-count compliance; standalone previews do not establish those.
- Resolve assembly-routine permission, final team approval, small-strain validity and outstanding local-refinement/stress questions.
- Preserve the tested-system scope of the solver recommendation. Untimed LU is not a performance competitor, and stronger preconditioning is a proposed extension.

This prose correction and evidence audit are AI-assisted work, not human team approval. Confirm member contributions and the required report-level AI-use disclosure before submission.
