# Section 7. Conclusion

**Status:** AI-assisted working draft for team review (not approved). Label `sec:conclusion`.
Body is about 0.45 page in the 11pt/25 mm preview (`preview.pdf`), three short paragraphs.

## Contents
1. Physical answers: hole softens the plate; holes and inner corners concentrate stress;
   load location moves the peak; fewer supports raise kappa_2 more than displacement;
   bending is the hardest case for accuracy.
2. Matrix properties and solvers: SPD + sparse, kappa_2 ~ N, CG iterations ~ N^(1/2), CG best
   iterative method, diagonal PCG little gain, Jacobi diverges, Gauss-Seidel impractical,
   MINRES stall on the beam, sparse LU fastest.
3. Refinement and validation, then limitations (one sentence, pointing to Section 6) and
   next steps (one sentence).

## Numbers
No new results. The only numbers repeated are from Section 6's text: 0.7% (finest beam mesh
vs beam theory with shear), 119 to 178 MPa (corner peak), 1e-9 (CG algebraic error).

## Files
`section.tex`, `main.tex` (preview stub for `sec:results`), `build.sh` (pdflatex, no bibtex),
`.gitignore`, `preview.pdf`. No `references.bib`: the section cites nothing.

## Open decisions
- Section 1 does not state explicit objectives or mention the numerical effort; this section
  answers the questions as phrased in Sections 1 and 5.
