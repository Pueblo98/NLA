# Reproducible Section 3 review inputs

These are unchanged copies of the Section 3 files from Hermes's PR #4 at commit `81cbef470047c21096ef83c7fc6924344fadb6d7`. They are evidence for a review, not a competing section draft or a merge of that PR. `inputs/manifest.json` records GitHub blob identifiers; all seven file bytes were checked against those identifiers.

The [review](../../draft/sections/03-solvers-and-protocol/paragraph-review-81cbef4.md) contains the findings and limitations. `suggested-edits.patch` proposes two changes to the canonical `draft/sections/03-solvers-and-protocol/section.tex` at that commit; it has not been applied to the snapshot or the canonical folder.

To regenerate the three inspected page images and extracted text from the repository root with the existing local dependencies:

```sh
PYTHONPATH=.build-deps python3 notes/section3-review-81cbef4/render_pdf.py
```

Render outputs and local tool caches are ignored. No PDF was edited and no LaTeX rebuild or numerical benchmark was completed in this review.
