# Visual progress report handoff

Prepared by Lucas's Codex on 10 November 2026 in response to Lucas's request
in the report-structure thread. This is a working progress report for review,
not an approved final report or a new drafts-channel submission.

## Files to review

- `drafts/Group02_Visual_Progress.md`: editable seven-section source.
- `drafts/Group02_Visual_Progress.pdf`: rendered 10-page review copy.
- `drafts/make_visual_progress_figures.py`: six figures, including explanatory
  diagrams, the saved small matrix, saved refinement data and the existing
  square before/after deformation.
- `drafts/build_visual_progress.py`: Markdown-to-PDF renderer, adapted from
  `drafts/build_draft.py`; writes review page images to the ignored
  `drafts/qa/visual-progress/` directory.
- `drafts/results/visual-progress-review.txt`: data and rendering check record.

The prior `Group02_Draft.md/.pdf` and opening module are unchanged. This file
pair is the proposed consolidated visual version; Hermes's and Darius's
separately reported assembled PDFs were not present in this checkout, so it
does not claim to incorporate unseen revisions from their workspaces.

## Structure and page map

1. Pages 1-2: aim and opening model, preserving the current opening's
   general physical explanation, force balance, triangulation figure and
   support reduction. The abstract and initial status summary precede this.
2. Page 3: displacement/strain illustration, stress law, triangle assembly,
   matrix properties and meaning of the condition number.
3. Page 4: solvers, common target, error definition and timing protocol.
4. Page 5: small square, actual matrix, direct solves and before/after shape.
5. Page 6: candidate additional objects and proposed experimental questions.
6. Pages 7-8: saved solver results, convergence, refinement and validation.
7. Page 9: preliminary conclusions, open questions and proposed work plan.

Page 10 contains sources, reproduction, provisional contribution statements,
AI-use disclosure and references. The standalone layout is for discussion;
the final report still needs the required Overleaf template and human review.

## Progress language and scientific distinctions retained

- Additional objects are candidates; outlines are not solved cases or meshes.
- New material/thickness sweeps are analytical predictions, not completed runs.
- The final geometry set, wider load/support comparisons, loading convention
  for thickness, stronger preconditioner and task ownership remain open.
- Only the 840-unknown force-driven case feeds the solver comparison. The
  prescribed-grip case remains separate.
- All eight solver statuses and the 20,000-iteration cap are preserved.
  Uncapped SD results from older notes are explicitly kept separate.
- LU is an untimed same-mesh reference. Timing scope and historical machine
  information remain attached to results.
- Solver error, mesh dependence, exact roller verification and random algebraic
  sensitivity are distinguished; no continuum-error order is claimed.
- The eight figure captions state schematic/computed status, displacement
  amplification and relevant units. Numerical iterations are static
  approximations, not physical time steps.

## Validation and rebuild

All eight solver rows were checked against CSV and JSON, including rounding,
acceptance, error and time. All three refinement rows match the saved data.
The small saved Cholesky solution satisfies its saved matrix/load. All seven
numbered sections and eight image paths are present. The PDF has 10 pages,
its extracted text stays within page margins, and all pages were inspected.
The refinement chart was redrawn to remove overlapping axis ticks.

One untimed sparse solve redraws the established square before/after plot;
the resulting maximum right-edge displacement matches the saved value at
relative tolerance `1e-10`. No iterative benchmark, parameter study or timing
table was rerun, and no original result file was overwritten.

With the dependencies from `drafts/requirements.txt`, run from `NLA/`:

```text
python drafts/make_visual_progress_figures.py
python drafts/build_visual_progress.py
```

This checkout uses its existing ignored `.build-deps/` packages. From the
workspace root, the equivalent commands are:

```text
PYTHONPATH=NLA/.build-deps MPLCONFIGDIR=NLA/.mplconfig python3 NLA/drafts/make_visual_progress_figures.py
PYTHONPATH=NLA/.build-deps MPLCONFIGDIR=NLA/.mplconfig python3 NLA/drafts/build_visual_progress.py
```

For Hermes and darius-codex: use this source and its page map when consolidating
the progress report, and compare with any newer opening or results available
only in your workspace. For pablo-agent and Frambuesa: review the physical
explanations and figure clarity, especially Section 2 and the proposed
comparisons in Section 5. Human contribution statements still need confirmation.
