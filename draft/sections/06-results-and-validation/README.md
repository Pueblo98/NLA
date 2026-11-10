# Section 6: Results, validation and discussion

**Status: initial working draft for team review, not final cross-object findings.**
Hermes is the drafter for this request. Follow the [shared writing rules](../../WRITING_RULES.md) and [Section 6 roadmap](../../ROADMAP.md#6-results-validation-and-discussion). Sections 1–5 are unchanged.

The draft interprets the existing Section 4 solver benchmark and adds a **square-only diagnostic extension** using the unchanged bundled FEM implementation. It does not claim execution or approval of Section 5's proposed rectangle, perforated square, load-patch or shortened-clamp experiments. Section 5 was reviewed on its actual review branch, not just the placeholder currently on main; exact source revisions and continuity decisions are in [review-notes.md](review-notes.md).

## Files

- `section.tex`: independent section body, without a preamble, for later inclusion.
- `main.tex`, `build.sh`, `references.bib`: portable standalone preview with section number 6.
- `preview.pdf`: the compiled preview, synchronized with the delivered source; build and inspection evidence belongs in `verification.md`.
- `generate_evidence.py`, `test_evidence.py`, `requirements.txt`: square-only numerical reproduction and verification.
- `reproduction/`: frozen, unchanged Section 4 copies of the existing assembly, structured plate and load/support routines. These are a reproducibility snapshot, not a second editable FEM implementation.
- `data/`: raw matrices, loads and displacement arrays, scalar observations, diagnostic results and the generated table.
- `review-notes.md`: earlier-section review, provenance and unresolved decisions.

## Compile

From this directory run `sh build.sh`, using Tectonic or pdfLaTeX/BibTeX. An optional `TECTONIC_BIN=/path/to/tectonic` selects an existing compiler. Python is not needed to compile the committed evidence table. For Overleaf, upload the module contents and select `main.tex`.

The wrapper is A4, 11 pt, with 25 mm margins. Required packages are `amsmath`, `amssymb`, `graphicx`, `booktabs` and `url`; bibliography style is `amsplain`. When combining modules, include the section body rather than its preamble, resolve its relative data paths, and retain only one copy of shared bibliography keys `saad-iterative` and `nla-square-code`. This preview does not establish the final `clean,onecolumn` layout or the assembled report's ten-page limit.

## Reproduce the new checks

Use a virtual environment with `requirements.txt`, then run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q test_evidence.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python generate_evidence.py
```

The script extends the **Section 4 structured square**, with 5, 10, 20 and 40 cells per side. It retains material, full left clamp, thickness and full right-edge traction. Its refinement study is not the Triangle-mesh study proposed in Section 5. No new assembly algorithm or iterative solver is introduced, and no historical timings are overwritten.

The two new fixed-matrix load tests use the 20-cell mesh and relative reduced-load change `0.001`. One scales the baseline load. The other integrates a linearly varying horizontal right-edge traction increment with zero resultant, scaled to the same load-vector norm. This redistribution changes moment and is not the finite-patch location experiment from Section 5. Neither perturbation seeks a worst-case direction. The separate roller-supported affine test is exact-solution verification for that boundary condition only.

Full definitions, environment and implementation hashes accompany the numerical output. Absolute successive-mesh differences are compared against conditional algebraic uncertainty estimates from actual observable weights and eigenvalue estimates. These are not certified continuum-error bounds. A numerically converged equilibrium is not automatically a physically valid small-strain approximation.

## Remaining scope and attribution

The additional objects, location and support variants need team selection, execution and validation before this becomes the full Section 6 described by the roadmap. Material and thickness studies are not currently specified or measured. Permission to substitute the team's FEM routine remains open. Earlier sections are still evolving and require another integration check when their sources change.

The project team is credited for the reused implementation and Section 4 measurements. This initial section, new diagnostic wrapper, tests and build checks are AI-assisted work by Hermes; subagent assistance is drafting/technical review, not human team approval. Actual member contributions and the required report-level AI-use disclosure must be confirmed for submission.
