# Section-by-section report workspace

This is the entry point for the team's section-by-section draft. This reorganisation adds no new report prose and does not replace the existing introduction.

## Shared sources of truth

- [ROADMAP.md](ROADMAP.md): each section's purpose, scope, boundaries, expected output and assignment coverage.
- [ROADMAP.pdf](ROADMAP.pdf): rendered copy of the same roadmap.
- [WRITING_RULES.md](WRITING_RULES.md): single shared guide for style, mathematical rigor, length and review after each section; consolidated at Lucas's request.

## Working folders

| Section | Folder | State (10 Nov 2026) |
| --- | --- | --- |
| 1. Building the model / introduction | [01-introduction](sections/01-introduction/) | Existing introduction; one objectives sentence added and figure resized. |
| 2. Displacement, forces and matrix construction | [02-mechanics-and-matrix](sections/02-mechanics-and-matrix/) | Simplified draft with compiled preview. |
| 3. Numerical methods and comparison protocol | [03-solvers-and-protocol](sections/03-solvers-and-protocol/) | Draft with compiled preview; protocol implementation details in its README. |
| 4. Simple square demonstration | [04-square-example](sections/04-square-example/) | Draft from fresh runs (`experiments/square.py`). |
| 5. Objects and experimental design | [05-objects-and-experiments](sections/05-objects-and-experiments/) | Draft; experiments in `experiments/objects.py`. |
| 6. Results, validation and discussion | [06-results-and-validation](sections/06-results-and-validation/) | Draft from fresh results; figures from `experiments/results_figures.py`. |
| 7. Conclusion | [07-conclusion](sections/07-conclusion/) | Draft. |

All sections are drafts for team review, written for third-year applied mathematics students. The combined preview is built by `python3 draft/combined/build.py` into `draft/combined/draft-report.pdf` (10 pages in the 11 pt / 25 mm preview, including title and references). It is not the final course template. Experiment scripts and fresh outputs are in [experiments/](experiments/).

## How each section thread works

1. Link the roadmap entry and the section folder, then read [WRITING_RULES.md](WRITING_RULES.md). Update that single guide for any new writing rule; do not create a second guide. After drafting or revising a section, reread all earlier sections and remove repetition before calling it complete. This organisational task does not authorise drafting the other sections.
2. Work on only the requested section. Keep its report body in `section.tex` without a preamble; when drafting is requested, add a standalone `main.tex`, bibliography and figures as needed.
3. Compile and inspect that section before updating its `preview.pdf`. Keep source and preview synchronised. Do not call a section final without the team's review.
4. Record decisions or blockers in that folder's README. Update the roadmap only for an agreed structural change, not for routine prose edits.
5. Combine modules into the final course template later, after the individual sections have been reviewed.

The previous full progress drafts are preserved in [reference/](reference/), not distributed into the new section folders. They can supply existing evidence when a section is opened, but do not override the roadmap or the team's later writing rules. Numerical code, raw results and original figure locations remain unchanged.

## Rebuild the roadmap

From the repository root:

```sh
uv run --with reportlab --with matplotlib --with pymupdf python draft/build_roadmap.py
```

The introduction has its own build script in Section 1. This workspace is not yet the combined final report and does not certify final-template compliance.
