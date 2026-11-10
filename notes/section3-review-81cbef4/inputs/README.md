# Section 3: Numerical methods and comparison protocol

Status: Hermes working draft for Codex/team review. Not approved final prose.

The source is `section.tex`; `main.tex` is a standalone A4, 11 pt preview with 25 mm margins. It uses amsmath, amssymb and url, plus the amsplain bibliography style. Include section.tex and merge references.bib into the final report. The wrapper is not the final course template; the combined ten-page limit remains to be checked there.

Run `sh build.sh` with Tectonic or pdfLaTeX/BibTeX installed. Alternatively set TECTONIC_BIN to a Tectonic executable. The script creates preview.pdf from the exact source.

## Basis and scope

Read draft/WRITING_RULES.md and the Section 3 entry of draft/ROADMAP.md. Read current Sections 1 and 2 and solvers/progress_benchmark.py at base revision d67eb5f. Applied the implementation findings in review-2026-11-10.md. No results table is imported into this methods section and no numerical benchmark was rerun for drafting.

This describes the current eight-method implementation, not the historical 3,000-step/restarted-GMRES plan. Timings include iterative setup and stopping checks; the sparse LU reference is untimed. The current cap is 20,000, GMRES restart equals the number of free unknowns, damping is 0.5, and PCG uses inverse diagonal scaling.

## Remaining review decisions

- Codex/team paragraph-level review is pending. The existing review file audits implementation and saved results, not this new prose.
- Confirm that all eight iterative methods remain in the final report; this draft explains those currently implemented rather than silently changing the method set.
- Section 2 is evolving. Recheck the transition after any newer Section 2 revision; this draft leaves earlier sections unchanged.
- Separate setup/solve timings are not available in the existing benchmark. Any future split-cost comparison requires fresh measurements.
- Preserve Section 2's unresolved course assembly-routine permission. This draft does not resolve it.
- Add member contributions and the required AI-use disclosure when assembling the report. This section was drafted with Hermes assistance; team review is required.

## Deliverables

section.tex, main.tex, references.bib, build.sh and compiled preview.pdf. Verification details accompany delivery. This module contains no external images or private path dependency.
