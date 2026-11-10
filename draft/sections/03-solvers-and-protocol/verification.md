# Section 3 readability revision: verification

Based on main at 98b90b8. This supersedes the earlier build record for the current source; earlier build/review evidence remains in Git history and the linked review notes.

## Requested change

The user asked for shorter, easier-to-read method explanations, split by method, with a quick intuitive reason for trying each. Solution methods now have ten separately labelled subsections: Cholesky, LU/reference, Jacobi, damped Jacobi, Gauss–Seidel, steepest descent, CG, diagonal PCG, GMRES and MINRES. Each states its mechanism and role. The eight measured iterative methods remain unchanged. The two main displayed equations are the common residual threshold and reference difference; simple method updates remain inline.

## Checks executed

- Built exact revised source using `TECTONIC_BIN=/path/to/tectonic sh build.sh`, Tectonic 0.17.0, exit 0, including BibTeX and reference reruns.
- All three final pages rendered with PyMuPDF and visually inspected: headings, equations and citations are legible, without clipping or overlap.
- No overfull boxes, undefined references or missing characters. The existing underfull bibliography URL box remains cosmetic.
- Same A4, 11 pt type and 25 mm margins. No font or spacing reduction. Preview remains three pages; the added method headings use some of the saved space. The closing validation paragraph and bibliography occupy page 3.
- Body text extracted from the PDFs before the References heading decreased from 1,091 to 908 whitespace-separated tokens (16.8%). This includes mathematical tokens/headings and is a consistent comparison, not a linguistic prose-word count.
- Earlier sections are unchanged. Reread their existing text in conversation and checked the transition from Section 2's positive-definiteness/conditioning ending.
- Preserved the reviewed protocol: 20,000-step cap, zero initial guess, strict independently recomputed residual target, full unpreconditioned GMRES, diagonal PCG, damping 0.5, minimum of three setup-inclusive times, and untimed LU reference.
- Preserved separation of load sensitivity from solver reliability. No zero-reference fallback is claimed; solver-level zero-RHS handling is explicitly separated from outer benchmark divisions.
- No solver code, numerical outcomes or timing measurements changed or rerun.

The previous Codex approval applies to the earlier revision, not this new wording. Fresh readability review and final course-template pagination remain pending. The shared section remains a working draft.
