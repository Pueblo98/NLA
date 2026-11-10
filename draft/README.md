# Section-by-section report workspace

This is the entry point for the team's section-by-section draft. This reorganisation adds no new report prose and does not replace the existing introduction.

## Shared sources of truth

- [ROADMAP.md](ROADMAP.md): each section's purpose, scope, boundaries, expected output and assignment coverage.
- [ROADMAP.pdf](ROADMAP.pdf): rendered copy of the same roadmap.
- [WRITING_RULES.md](WRITING_RULES.md): single shared guide for style, mathematical rigor, length and review after each section; consolidated at Lucas's request.

## Working folders

| Section | Folder | Starting state |
| --- | --- | --- |
| 1. Building the model / introduction | [01-introduction](sections/01-introduction/) | Existing introduction, LaTeX sources, figure, bibliography and exact-source compiled preview. No rewrite. |
| 2. Displacement, forces and matrix construction | [02-mechanics-and-matrix](sections/02-mechanics-and-matrix/) | LaTeX review draft and simplification note; Hermes reports a compiled, inspected PDF in Slack. Repository preview pending. |
| 3. Numerical methods and comparison protocol | [03-solvers-and-protocol](sections/03-solvers-and-protocol/) | Section workspace only; no new prose. |
| 4. Simple square demonstration | [04-square-example](sections/04-square-example/) | Section workspace only; no new prose. |
| 5. Objects and experimental design | [05-objects-and-experiments](sections/05-objects-and-experiments/) | Section workspace only; no new prose. |
| 6. Results, validation and discussion | [06-results-and-validation](sections/06-results-and-validation/) | Section workspace only; no new prose. |
| 7. Conclusion | [07-conclusion](sections/07-conclusion/) | Section workspace only; no new prose. |

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
