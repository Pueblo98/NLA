# NLA Group 2: shared working context

Project: Elastic Deformation of Two-Dimensional Objects.
Repository: https://github.com/Pueblo98/NLA (owned by Pueblo98 / Pablo).

## Start of a task

1. Inspect git status and fetch origin. Do not overwrite another contributor's work.
2. Read this guide, docs/status.md and the documents relevant to your task.
3. Work on a task-specific branch; use a separate clone or worktree for concurrent agents.
4. State the scope, inputs and acceptance checks in an Issue or PR. Repository access does not make another agent automatically execute a task.

## Shared paths

- AGENTS.md: repository-wide working context (this file belongs at the root).
- docs/status.md: current handoff, blockers and unresolved decisions.
- docs/interfaces.md: canonical mesh / assembly / solver contract, to be contributed.
- docs/model.md: canonical physical model and assumptions, to be contributed.
- solvers/comparison-plan.md: existing solver experiment proposal; read its benchmark definition before implementing comparisons.
- mesh/, fem/, solvers/, validation/, notebook/, figures/: existing project directories.

Do not create competing shared model/interface documents under notes/. Scratch notes may remain local. Model and interface paths listed above are planned until their files exist.

## Scientific consistency

A unit-square displacement-driven benchmark and a force-loaded 2 by 1 rectangle are different experiments. Their geometry, boundary conditions and material assumptions must not be mixed. Confirm the shared baseline with the group and record the decision in docs/model.md and docs/status.md. Do not treat a proposal or chat recollection as a verified assignment requirement.

All solver comparisons must use the identical reduced matrix, RHS and DOF ordering. Retain the unreduced system and prescribed values for reaction recovery. Agree indexing, connectivity orientation, units, force-versus-traction conventions and array formats in docs/interfaces.md before integration.

## Validation and handoff

- Read the actual code and dependency setup before selecting a test command; no common executable test suite has been established by this documentation change.
- Run relevant tests before handing off executable work. Report commands, outcomes and blockers; never present planned tests as passes.
- Distinguish algebraic residuals, physical validation and discretization error.
- Commit only intended files; exclude credentials, private scratch files and course materials not cleared for publication. This repository was public at bootstrap.
- Prefer task branches and reviewed PRs; do not force-push or overwrite main. Do not change another contributor's runner configuration.
- Agent-specific authorization still applies: a collaborator's access is not permission to bypass their owner's approval policy.
- Update docs/status.md when handing off meaningful work, and link the actual Issue/PR and validation evidence.
