# Verification of the initial Section 5 draft

## Exact-source PDF

Compiled the committed `main.tex`, `section.tex`, bibliography and generated
geometry PDF with **Tectonic 0.17.0** using:

```sh
TECTONIC_BIN=/path/to/tectonic sh build.sh
```

The final build exited 0. Its log contains no warnings, overfull/underfull boxes,
undefined references/citations or missing-character messages.

The final preview is **two A4 pages including its reference**, at 11 pt with
25 mm margins. Prose was shortened before layout changes; fonts, margins and
spacing were not reduced. A figure annotation was moved to avoid crossing a
dimension label. Both exact final pages were rendered and visually inspected:
the geometry, labels, table, equations and bibliography are readable without
clipping or overlapping labels. The section's local figure/table references and
citation resolve. Automated text-span bounds found no margin violations on
either page (small glyph tolerances allowed; page-number footers excluded).

SHA-256 of the inspected `preview.pdf`:

```text
ea812946552597092ef7512f83f8dc91a0d19e7e559158012ec21e197582bea8
```

This standalone build does not certify the final `clean,onecolumn` template or
the assembled report's ten-page limit.

## Specification checks actually executed

`python3 check_spec.py` exited 0. It checked the proposed polygon orientations,
rectangular-hole containment and seed, boundary split endpoints, force/traction
consistency, distinct support endpoints and area-limit options. Its calculated
material areas are 1, 2 and 0.96 square metres. Both the full-edge baseline and
each proposed load patch carry 1,000,000 N rightward. The maximum triangle areas
are 0.005, 0.00125 and 0.0003125 square metres.

These are checks of **inputs**, not generated meshes, stiffness matrices,
physical deformation or solver outcomes. No experimental result is claimed.
Actual mesh validity/quality, FEM execution, convergence, timing, conditioning,
small-strain validity and force/moment balance remain future execution work.

The figure was regenerated from `cases.json` with `make_figure.py` before the
final build. The mesher's documented `p`, `q`, `a` options and hole-seed handling
were read at <https://rufat.be/triangle/API.html>; the mesher was not run.

## Review follow-up verification

After the independent drafting review, clarified the physical solution source,
successive-mesh comparison and proposed acceptance criteria. Rebuilt the exact
revised source successfully: two pages, no compiler warnings and no text-margin
violations. Page 1's render is byte-identical to the previously inspected render;
the revised page 2 was visually inspected with its table and references intact.
The input checker passed again; it does not implement the newly proposed
matrix/reference/equilibrium acceptance criteria. Earlier section sources were
not changed. The hash above now identifies this reviewed revision.

## Cross-section review and publication scope

See `review-notes.md` for the before/after review against Sections 1–4 and the
existing Section 3/4 affine-test cross-reference issue. Only files under
`draft/sections/05-objects-and-experiments/` are intended for this publication.
The earlier sections, their numerical evidence and shared rules remain unchanged.
