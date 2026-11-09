# Progress draft recovery and handoff - 9 November 2026

For Hermes and Lucas: the previous Slack response reported a UTF-8 decoding
error, but the draft artifacts had already been saved. No report content was
lost. The canonical Markdown and its drafts-channel copy both decode as UTF-8
and match after normalizing the three figure links.

The finished progress document is `Group02_Draft.pdf` (nine pages); its editable
source is `Group02_Draft.md`. The local reference files include both the
Session 22 PDF and its text checklist. The draft covers the problem, model,
boundary conditions, small direct example, larger iterative experiment,
residuals, iterations, timings, figures, initial interpretation, questions,
two-week plan, contributions and AI-use disclosure.

## Checks repeated after recovery

- `fem/check_fem.py`, `solvers/check_system_tools.py` and
  `solvers/check_sparse_system_tools.py` all pass.
- All eight iterative methods were rerun against a freshly assembled
  840-unknown system. Iteration counts, final residuals, errors against LU,
  statuses and acceptance decisions reproduce the saved benchmark.
- The saved small matrix and right-hand side exactly match fresh assembly.
- PDF text extraction confirms nine readable pages and the required sections;
  text bounding boxes fit the page margins. The nine-page contact sheet and
  full-size pages 2, 4 and 9 were visually inspected without visible defects.
- The historical best-of-three timing measurements were preserved.

Detailed recovery results are in `results/recovery-checks.txt`; the original
benchmark data and verification record remain in `results/`.

The headline iteration counts are CG 242, full GMRES 228, MINRES 236,
diagonal PCG 226 and Gauss-Seidel 19,136. Ordinary Jacobi diverges; damped
Jacobi and steepest descent do not reach the target within 20,000 iterations.
These outcomes are explicitly distinguished in the draft.

## Submission and remaining work

Lucas's request to finish the draft authorizes delivery of the finished
progress document to the drafts channel. A human group member still needs to
submit the PDF through Blackboard; this agent has made no Blackboard submission.
Hermes can use this verified numerical section and its raw data in the shared
consolidation. Any later edits should keep the canonical Markdown, PDF and
drafts-channel copy synchronized.

The professor's provided assembly routine remains unidentified. General
geometries, holes, stronger preconditioning and a systematic discretization
error study remain future work, as stated in the document. The final report
is due 20 November and must use the required Overleaf template.
