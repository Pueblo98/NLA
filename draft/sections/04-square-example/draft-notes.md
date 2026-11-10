# Section 4: A simple square demonstration

Status: Hermes working draft for team review. Neither final prose nor an agreed selection of later experimental objects. Earlier sections are unchanged.

## Current sources and continuity

Follow ../../WRITING_RULES.md and the Section 4 entry of ../../ROADMAP.md. Before drafting, Sections 1, 2 and 3 were read at main 9736c8e9cf26630a6772786a74972ec8ff57db75. Section 3's committed preview PDF was also read. A subsequent fetch found main a4debf1 with an additional Section 3 paragraph review, but no change to those section sources. That review's distinction between load sensitivity and algorithmic stability is respected here; this section does not make a floating-point stability claim or invoke an unimplemented zero-reference fallback. This run has a nonzero load.

The opening continues Section 3's final square-example handoff. Material/assembly derivations stay in Section 2; algorithm explanations stay in Section 3. The existing force-driven square is used for a reproducible demonstration, separately from the grip-driven case and roller-supported exact-solution test. Sections 1–3 were checked again after drafting for overlap and notation consistency.

## Deliverables and building

- `section.tex`: independent section body for inclusion in the combined report.
- `main.tex`: standalone A4, 11 pt article preview, 25 mm margins, matching existing previews. Required packages: amsmath, amssymb, graphicx, booktabs, url; bibliography style: amsplain.
- `preview.pdf`: compiled from this source; see verification.md for exact checks.
- `figures/`: computed geometry/deformation and convergence figures.
- `data/`: full small-system arrays, large-reference nodal displacements, selected CG iterates, all eight residual histories, all three timing repeats, and native/independent acceptance statuses.

Build with `sh build.sh` using Tectonic, or pdfLaTeX and BibTeX. An optional `TECTONIC_BIN` environment variable selects an existing Tectonic executable. No local absolute paths are embedded in the build. Upload the module contents to Overleaf and select main.tex, or include section.tex from the eventual master and merge its bibliography entry. Resolve figure/data paths relative to that master's working directory.

## Reproduction and provenance

The `reproduction/` directory is an explicitly frozen, byte-identical snapshot of four existing project source files at 9736c8e, not a new editable implementation of FEM or the solver algorithms. `source_hashes.json` records their original paths and SHA-256 values. Upstream code changes must be deliberately resnapshotted before regenerating evidence.

In a fresh virtual environment, install `requirements.txt`, then run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python generate_evidence.py
sh build.sh
```

This reruns only the small and 20-by-20-cell square demonstrations, without rewriting repository benchmark results or executing a broader refinement study. It generates plots, CSV/JSON data and the LaTeX solver-table rows together. Exact timing values vary by machine/load; machine and software details are recorded in data/results.json. Histories are not included in timed calls; native stopping checks and setup are, following Section 3. Sparse LU is an untimed reference. No measurements are imported from historical progress reports.

The main text's displayed small solution is rounded; full precision is in the CSV files. `small_A_N_per_m.csv` and `small_b_N.csv` use SI units. `small_L.csv` is the lower Cholesky factor, `small_y.csv` solves Ly=b, and `small_x_m.csv` solves L^T x=y. Free degree-of-freedom indices and node/triangle arrays identify their ordering. `large_reference.npz` contains the full displacement vector in metres. `cg_iterates.npz` contains only free components, in the ordering saved in large_reference.npz.

Checks include known-answer solver tests, positive element areas and unit total area, the expected nodal force distribution, exactly imposed supports, positive small-system eigenvalues, independent true residuals, and constrained-support-only force/moment balance for direct solutions. Accepted iterative solutions' balance defects are retained separately and are not silently substituted for the direct-reference check.

## Review and integration still needed

- Team review of the case choice and Section 4 prose remains pending. The original force-driven example is attributed to Ernesto in the project's plate.py; this draft does not claim the team selected it as the final main case.
- The course-provided assembly routine has not been located; permission to use the team's implementation is unresolved.
- Sections 2 and 3 are evolving. Recheck their final notation and protocol before combining. No proposed edits to them were applied as part of this Section 4 task.
- The final `clean,onecolumn` course template is not present in the checked-out repository. This standalone preview does not certify final template compliance or the combined ten-page limit. Consolidate references, shorten overlap across sections and check the final report there; do not shrink typography to force a fit.
- This is not a continuum-error, mesh-convergence, material-validity or cross-object study. No exact solution of the clamped square is claimed. The 200x deformation is a display scale only.
- Report-level member contributions need the team's confirmation. This section's prose, reproduction wrapper, new figures and build checks were prepared with Hermes AI assistance; the final report must include the required AI-use disclosure. Existing assembly and solver code remains attributed to the project team.
