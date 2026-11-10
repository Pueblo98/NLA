# Section 3. Numerical Methods and Comparison Protocol

**Status, 10 November 2026: drafting reported in Slack; Section 3 source and PDF are not yet present here. Implementation review available below.**

## Scope

Use [the Section 3 roadmap entry](../../ROADMAP.md#3-numerical-methods-and-comparison-protocol) as the source of truth for this section's purpose, required contents, boundaries and expected output. Do not duplicate or silently redefine that scope here.

Follow [the shared writing rules](../../WRITING_RULES.md), including the review of all previous sections after each section is completed. Existing full progress reports are [reference material](../../reference/), not an approved replacement for this section.

## Files to add when this section is requested

- `section.tex`: only this section's body, suitable for later inclusion in the combined report.
- `main.tex`: standalone preview wrapper.
- `references.bib` and `figures/`: references and assets actually used by this section.
- `preview.pdf`: compiled and visually checked against the current source.

Do not create these as empty report stubs or claim the section is completed. Record the agreed section owner, review status and unresolved decisions below when the section thread starts.

## Handoff status

- Thread roles: Hermes is drafting; darius-codex reports an existing draft. Coordinate against one identified source before integrating edits. Lucas's Codex has completed an implementation and saved-results audit.
- Review: [implementation and integration review](review-2026-11-10.md), covering actual stopping rules, preconditioning, timing scope, reference calculations, failure classification and error measures. This does not approve unavailable prose or PDF layout.
- Availability check: this checkout and read-only GitHub checks of `main` and `docs/section-draft-workspace` contain only this folder's README, before the addition of the present review. The source reported by darius-codex may be in another workspace or revision.
- Next action: darius-codex supplies the existing source path and branch/commit; Hermes coordinates edits and builds the exact source. Then review prose against Sections 1–2 and inspect the PDF before publishing `preview.pdf`. No Section 3 compilation or visual review has been performed here.
