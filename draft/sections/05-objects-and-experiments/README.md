# Section 5: Additional objects and experimental design

**Status: initial proposal for team review, not agreed experiments or computed findings.**
Hermes drafted this section at Simon's request. Earlier sections remain unchanged.
Follow the [shared writing rules](../../WRITING_RULES.md) and [Section 5 roadmap](../../ROADMAP.md#5-additional-objects-and-experimental-design).

## Deliverables

- [preview.pdf](preview.pdf): compiled standalone section.
- [section.tex](section.tex): section body without a preamble, ready for later inclusion.
- [main.tex](main.tex): A4, 11 pt, 25 mm margins preview wrapper, with section number 5.
- [cases.json](cases.json): proposed physical inputs, ordered boundaries, hole seed, boundary splits, mesh settings and comparison register.
- [figures/objects.pdf](figures/objects.pdf): schematic generated from the case specification, not a mesh or deformation result.
- [make_figure.py](make_figure.py): optional figure regeneration with matplotlib.
- [check_spec.py](check_spec.py): standard-library checks of the proposed input specification, not FEM validation.
- [review-notes.md](review-notes.md): consistency review and outstanding decisions.
- [verification.md](verification.md): build, layout and input-check evidence.

## Build and integrate

Run `sh build.sh` with Tectonic or pdfLaTeX/BibTeX installed. Alternatively set
`TECTONIC_BIN=/path/to/tectonic`. The script compiles the exact source and copies
`build/main.pdf` to `preview.pdf`. The committed figure means Python is not needed
for LaTeX compilation. To regenerate it, install matplotlib in a suitable Python
environment and run `python make_figure.py`. Run `python check_spec.py` to check
input consistency. Its assertions cover these rectangular polygons only; it is
not a general polygon or generated-mesh validator.

The section requires amsmath, graphicx, booktabs, tabularx and array. The preview
also uses url. Include `section.tex`, resolve its figure path, and merge the
bibliography into the report using `amsplain`; `shewchuk-triangle` already exists
in earlier modules and should have one canonical entry. Do not copy the preview
preamble into the final course template. The final `clean,onecolumn` template and
ten-page limit must be checked for the assembled report, not inferred from this
standalone preview.

## Execution handoff

`cases.json` is an input specification, not an executable experiment runner.
Before meshing, insert the listed left/right boundary split coordinates into the
ordered outer polygon and encode every consecutive pair, including closing
pairs and hole boundaries, as constrained segments. Use the supplied hole seed
and `pq25a...` options. These switches and hole handling were checked against the
[Python Triangle API](https://rufat.be/triangle/API.html). Do not use a convex-hull
fill that closes the opening. Archive generated nodes, triangles, boundary
markers, package version, options and measured quality; the mesh families need
not be nested.

For every object, run the baseline at three area limits. At the middle limit,
reuse the same mesh for magnitude, location and support variants. Reuse baseline
records where configurations coincide rather than counting them as independent
measurements. For load-location comparisons, compare the three equal-length
patches to one another; a comparison against the full-edge baseline changes
concentration as well as location. Integrate forces per boundary edge and select
support components from fixed coordinate intervals, not fixed node counts.

Retain Section 3's exact common protocol, including all eight currently described
iterative methods, the untimed LU reference, strict independently recomputed
residual, minimum of three setup-inclusive timings and native termination status.
Full GMRES can be expensive on the larger proposed meshes. Record resource-limited
runs as not completed; do not silently change restart, cap, methods or timing
scope to manufacture a comparable table. Any revised protocol needs an explicit
Section 3 update before fresh measurements.

## Decisions still required

1. Team approval of the rectangle and square-opening candidates, dimensions and
   chosen force/support ranges. The existing illustrative figures did not select
   these objects; the new proposals have explicit comparison questions.
2. Actual constrained meshing and FEM execution. No new displacement, convergence,
   conditioning or timing result is claimed by this draft.
3. Course-provided assembly routine or explicit permission to substitute the
   current implementation, inherited from Section 2.
4. A specified directional load-perturbation experiment for the sensitivity work
   in Section 6. The magnitude study tests scaling, not worst-direction sensitivity.
5. Small-strain/small-rotation validity and mesh quality for the proposed cases,
   especially the concentrated patch load and shorter clamp. The draft's peak
   corner-stress exclusion does not validate the physical model.
6. Cross-section review after ongoing edits to Sections 2–4 and final template
   integration. No earlier section or numerical result was changed here.

This draft, figure script and specification were AI-assisted by Hermes. Human
review, actual member contributions and the required AI-use disclosure remain
part of final report integration. A review branch is publication for discussion,
not team approval or a merge into main.
