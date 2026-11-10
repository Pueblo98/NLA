# Section 5 consistency review

## Source basis and scope

Read `draft/WRITING_RULES.md`, `draft/ROADMAP.md` and all four preceding section
bodies from main revision `8aefb2a5d5fc6745b358c32c537afc14160828d1` before drafting.
After drafting, checked that those files were unchanged and reread their earlier
full contents, including Section 4's closing paragraph beside Section 5's opening.
A fresh fetch before publication found no intervening main changes.

This is a drafting and input-specification task, not a rerun of Section 4 or an
implementation of general-object meshing. Existing sections and code are intact.

## Continuity checks

- **Section 1:** preserve the general introduction and distinction between filled
  triangles and physical bars. No new opening or repeated model derivation.
- **Section 2:** retain the homogeneous isotropic plane-stress model, metres,
  pascals, constant thickness, boundary-load integration and sufficiently
  supported matrix. Do not conflate the unsupported stiffness with the reduced
  positive-definite system. General `triangle` meshing remains proposed.
- **Section 3:** reuse its protocol rather than repeat or revise algorithms,
  tolerances, cap, restart convention, timing statistic or reference role.
  Load scaling is explicitly not a directional sensitivity experiment.
- **Section 4:** retain its baseline material, thickness, left clamp, full-edge
  rightward traction and absence of body forces. Its final limitation leads to
  the proposed mesh/geometry study. The structured square demonstration is not
  treated as a matched-mesh control for newly triangulated objects.

## Controls and limitations

The rectangle changes length and material area. The opening changes shape and
material area. These confounders are stated rather than describing either study
as an equal-area geometry experiment. Mesh comparisons preserve physical regions
and use integrated edge forces; mesh density and unknown count are not equated.

Location comparisons use three equal-length patches, each at the same total
force. Comparing one of these patches against the full-edge baseline also
changes load concentration and is explicitly excluded as a pure location test.
The full and central-half clamps both remove planar rigid motion on each proposed
connected object. This argument is not a check of a generated stiffness matrix.

The figure is a new schematic of proposed inputs, not evidence that the shapes
were selected or executed. Sharp-corner peak stresses are not convergence
observables. Mesh differences, solver errors and continuum accuracy remain
separate. The geometric and input checks do not establish small-strain validity.

## Existing cross-section issue to reconcile later

Section 3's final sentence refers to a separate exact affine test in Section 4,
but the current Section 4 report body does not describe that test. Its supporting
numerical material may supply it, but the prose cross-reference should be
reconciled by those section owners. Section 5 does not rely on that claim and
does not silently edit earlier sections to fix it.

Section 2's README still says Sections 3–7 have only scope READMEs, which no
longer describes the current source tree. The current section bodies, not that
historical statement, were used for this review.

## Independent drafting review and targeted follow-up

A background drafting subagent found the design consistent with Sections 2–4
and acceptable as an initial proposal, subject to two execution clarifications.
It did not inspect the PDF and did not modify files. The follow-up explicitly
assigns physical observables to the checked same-mesh LU reference and records
absolute successive-mesh differences for all three specified scalar observables.
Conditional algebraic uncertainty estimates guard against interpreting unresolved
small differences as mesh effects; zero-component relative ratios are not used.

The companion specification now gives proposed acceptance thresholds and
normalizations for symmetry, SPD diagnostics, reference residual, prescribed
values, total force and total moment. They are not inferred from Section 4's
observed errors and are not claimed implemented or passed. The smaller-system
Cholesky and larger-system eigenpair checks supplement the structural SPD
argument; eigenvalue estimates are explicitly not certified spectral bounds.
These are limited corrections to this draft, not approval of the whole report.

## Open integration decisions

The README records object approval, meshing/execution, assembly permission,
directional perturbation design, physical validity and final-template checks.
No independent agent review constitutes team approval. Member contribution and
AI-use statements must be completed for the assembled report.
