# Section 4. Simple Square Demonstration

**Status: initial working draft available for review, not approved final prose.**

## Exact delivered draft

Published at Simon's request so the other agent can review the initial draft:

- [Compiled three-page PDF](preview.pdf), byte-identical to the Slack attachment.
- [Exact delivered LaTeX and reproduction ZIP](Section-4-LaTeX-and-Reproduction.zip).
- [Section source](section.tex) and [standalone wrapper](main.tex).
- [Draft notes and build instructions](draft-notes.md), preserving the source package's original README.
- [Build and evidence verification](verification.md).

The unpacked source and figures are included here for line-by-line review.
The package is the original delivered artifact, not a revision against subsequent
changes to Sections 2–3. Review its consistency with those current sections before
integration. Earlier sections and Lucas's numerical handoff/review files are
unchanged by this publication. Full prose, figure, citation and layout review
remains pending.

The notes below record the earlier handoff chronology; their missing-artifact
statements describe the state before this publication.

## Scope

Use [the Section 4 roadmap entry](../../ROADMAP.md#4-simple-square-demonstration) as the source of truth for this section's purpose, required contents, boundaries and expected output. Do not duplicate or silently redefine that scope here.

Follow [the shared writing rules](../../WRITING_RULES.md), including the review of all previous sections after each section is completed. Existing full progress reports are [reference material](../../reference/), not an approved replacement for this section.

## Files to add when this section is requested

- `section.tex`: only this section's body, suitable for later inclusion in the combined report.
- `main.tex`: standalone preview wrapper.
- `references.bib` and `figures/`: references and assets actually used by this section.
- `preview.pdf`: compiled and visually checked against the current source.

Do not create these as empty report stubs or claim the section is completed. Record the agreed section owner, review status and unresolved decisions below when the section thread starts.

## Handoff status

- Owner: Hermes (assigned by Simon in Slack).
- Numerical support: Lucas's Codex; completed rerun and handoff below.
- Draft/review: Hermes's source and preview remain pending in this checkout.
- Next action: integrate the chosen evidence into the section, review against
  Sections 1–3, and compile and inspect the exact source.

## Section-thread update, 10 November 2026

Simon assigned the Section 4 draft and compiled preview to Hermes in Slack;
Lucas asked Lucas's Codex to help. Hermes's in-progress source is not yet in
this checkout. Lucas's Codex has read Sections 1–3 and prepared a
[numerical handoff](numerical-handoff-2026-11-10.md), a reproducible
[verification script](verify_numerics.py), and checked arrays/results under
`numerical-review/`. The rerun covers the small direct solution, all eight
large-system solver outcomes, eigenpair defects, reactions and force/moment
balance. Selected CG displacement iterates are available for Hermes's figures.
These are supporting inputs, not a completed or approved Section 4 or a PDF
layout review.

## Review request after Slack delivery

Hermes reports delivering a three-page working PDF and portable source package
in Slack. They remain unavailable in this checkout and in the GitHub Section 4
directory checked on 10 November. Lucas requested a review; the
[preliminary review](review-2026-11-10.md) checks the available evidence and
records what remains to inspect on those exact artifacts. Source, figure,
build and PDF review remain pending receipt of the delivered files.
