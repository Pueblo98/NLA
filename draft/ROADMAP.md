# NLA Report: Section Roadmap

**Version 1 | Structure baseline for review | 10 November 2026**

## Purpose and scope

This is the source-of-truth planning document for organising the report into separate section threads. It defines what each section should do, what it includes and what its thread should deliver. **It is not a report draft and contains no assembled results.**

The existing introduction was developed in another thread and is retained as Section 1. Do not rewrite it here. Its editable source in this workspace is `draft/sections/01-introduction/section.tex`; the previous `drafts/modules/01-building-model/` location is retained only for historical builds. The roadmap combines Simon's original seven-section progression with Hermes's and Lucas/Codex's coverage and readability recommendations. Review is still pending; numerical settings, final objects, solver selection and individual ownership are not decided by this document.

**Reading order:** intuitive framework → detailed mechanics and matrix construction → numerical methods → simple square demonstration → extended experimental design → results and interpretation → conclusions.

## 1. Building the Model: Existing Introduction

**Purpose:** Give the reader an intuitive route from elastic deformation to a linear algebra problem before introducing technical detail.

**Include, using the existing introduction:**

- The substantive modelling question and the project objectives, with the framework kept general across shapes.
- The physical chain from displacement to strain, stress and static equilibrium.
- Filled triangular elements, shared nodal displacement values and the meaning of the stiffness system and its support reduction.
- A short indication that we will study both deformation and the numerical effort needed to compute it.

**Boundary:** Keep particular materials, dimensions, loads and support arrangements for the case descriptions. Leave detailed field, interpolation and element-stiffness formulas to Section 2. Do not turn the introduction into a solver survey or repeat its explanation later.

**Section-thread output:** Link the existing introduction and its compiled preview. Check only whether a short objectives statement or transition is missing; any change goes back to the introduction's own thread.

## 2. Displacement, Forces and Matrix Construction

**Purpose:** Explain the mechanics and construction behind the system introduced in Section 1.

**Include:**

- Model assumptions, displacement components, strain, the material stress-strain law and force balance. State the chosen plane-stress or plane-strain interpretation, units and limits of the model.
- Boundary-respecting triangular meshes, two displacement components per node, interpolation, element contributions and sparse assembly. Identify the provided assembly routine, or explicitly resolve permission to use an alternative.
- Applied loads, prescribed displacements, free/constrained indices, the reduced system and recovery of support reactions.
- Sparsity, symmetry and the distinction between rigid-body modes of the unsupported matrix and positive definiteness after sufficient supports. Explain conditioning and how it will be estimated.

**Boundary:** Explain the construction once, without repeating Section 1's intuitive opening. Do not present solver rankings or experimental findings here. Case-specific parameter values belong with Sections 4 and 5.

**Section-thread output:** A self-contained methods module with defined notation, essential equations and an explanatory diagram if useful. Readers should understand what the matrix, unknowns and loads represent before Section 3.

## 3. Numerical Methods and Comparison Protocol

**Purpose:** Explain the chosen solution methods and establish fair comparisons before showing results.

**Include:**

- Selected direct and iterative methods, why they suit the supported matrix and how each works at an understandable mathematical level. Explain any preconditioner.
- A common system, initial guess, residual definition, tolerances, stopping criteria, iteration budgets and treatment of non-convergence. State restart and iteration-count conventions where relevant.
- Execution time, iteration count, residual, accuracy against a same-mesh reference and numerical stability. Define setup/factorization versus solve costs and the timing repetition/statistic used.
- The distinction between algebraic solver error and finite-element discretization error. Establish the validation checks used later.

**Boundary:** This is the method and measurement specification, not the main results table. The brief permits justified solver selection; its examples are not a requirement to implement every named algorithm.

**Section-thread output:** A focused solver explanation and one comparison protocol reused in Sections 4 and 6. Clearly distinguish measured methods from an untimed reference.

## 4. Simple Square Demonstration

**Purpose:** Make the model and methods concrete using the simplest controlled case before introducing other objects.

**Include:**

- A schematic and complete specification of geometry, material, units, mesh, loads and supports. State whether loading is traction, total force or prescribed displacement.
- A small mesh with identifiable displacement unknowns, the coupled matrix/load system and a worked direct solution. Provide complete arrays separately if they are too large for the main text.
- A larger square case showing selected iterative approximations, residual histories and an interpretable comparison under Section 3's protocol.
- Original/deformed views, displacement units and any amplification factor. Demonstrate support satisfaction, force balance including reactions and agreement between solvers.

**Boundary:** Solver iterations approximate one static equilibrium; they are not physical time steps. Keep different load/support cases separate. Use this section to teach the workflow, leaving the systematic cross-case and refinement interpretation to Section 6.

**Section-thread output:** One reproducible square example with a small worked system, convergence evidence, deformation visualisation and basic validation. Every figure should explain what the reader learns from it.

## 5. Additional Objects and Experimental Design

**Purpose:** Introduce the other objects and explain what each comparison is intended to reveal before presenting its outcome.

**Include:**

- Several selected two-dimensional objects, each with a modelling reason, ordered boundary coordinates and internal openings where applicable. Identify illustrative shapes separately from selected experiments.
- Mesh generation and refinement settings, material values, support components and load magnitudes/locations for every case. Check that meshes respect boundaries and holes and that supports remove rigid motion.
- A compact case register stating the question, changed factor, fixed quantities and measured response for each comparison.
- Studies of geometry, mesh resolution, load magnitude, load location and supports. Material/elasticity and thickness studies supplement this scope rather than replace it.

**Boundary:** This is experimental design, not findings. Do not preselect a hole or L-shape just because a diagram exists. For thickness changes, specify fixed total force versus fixed traction; use separate interpretations for imposed-displacement cases. Preserve equivalent physical loads and support regions under refinement.

**Section-thread output:** Agreed objects, a case register and controlled experiment specifications ready to execute. Clearly label proposed work.

## 6. Results, Validation and Discussion

**Purpose:** Answer the project questions using the chosen experiments, explaining both physical response and numerical behaviour.

**Include:**

- Interpreted deformation comparisons across the objects, loads, supports and agreed material/thickness variations.
- Solver convergence, cost, accuracy, numerical stability and failure cases, linked to symmetry, positive definiteness, conditioning and preconditioning.
- Sensitivity to small load perturbations and mesh-refinement comparisons under equivalent physical loading, using matching physical points or consistent field measures.
- Force balance including constrained support reactions, satisfaction of prescribed displacements and solver agreement. Distinguish solver error, discretization error and any separate exact-solution verification.
- Limitations, uncertainty and unexpected behaviour. Distinguish completed measurements, imported/reported results, analytical predictions and unfinished experiments.

**Boundary:** Do not repeat Section 3's method descriptions or Section 5's full case specifications. Reference them. Agreement between solvers on one mesh is not evidence of continuum accuracy; less deformation alone does not imply better conditioning.

**Section-thread output:** A small set of meaningful plots/tables with raw-data and script references, validation evidence and conclusions limited to what was actually tested.

## 7. Conclusion

**Purpose:** Give direct answers to the objectives introduced at the start.

**Include:** The main physical findings, justified solver/method recommendations, what refinement and validation establish, the most important limitations and feasible next steps.

**Boundary:** No new experiments, unexplained results or claims extending beyond the studied cases.

**Section-thread output:** A concise synthesis written after Section 6, not a second results section.

## Assignment Coverage Check

Checked directly against **NLA-1/NLA-2, page 2** of the uploaded *Group Project Descriptions: Numerical Linear Algebra and Partial Differential Equations*, Fall 2026.

- **Several objects, ordered boundaries and openings where applicable:** Section 5; comparisons in Section 6.
- **Geometry-respecting triangular meshes and progressive refinement:** construction in Section 2; small-to-large example in Section 4; design/results in Sections 5 and 6.
- **Assembly routine, material properties and supports removing rigid motion:** Section 2, specified for each case in Sections 4 and 5.
- **Load magnitudes, locations and support conditions:** designed in Section 5 and analysed in Section 6.
- **Original/deformed shapes and amplification labels:** Section 4 and relevant Section 6 figures.
- **Symmetry, positive definiteness, conditioning and load sensitivity:** definitions in Section 2; measured investigation in Section 6.
- **Appropriate solver selection; time, iterations, residuals, accuracy and stability:** protocol in Section 3; evidence in Sections 4 and 6.
- **Force balance, support satisfaction and solver agreement:** demonstrated in Section 4 and applied across the study in Section 6.
- **Equivalent loading across meshes; discretization error versus solver error:** defined in Section 3 and addressed in Sections 5 and 6.
- **Self-contained, self-explanatory Jupyter notebook:** whole-project integration deliverable covering model, methods and results. It is not replaced by the report or this roadmap.

The brief explicitly allows adapting its suggested workflow and solver selection with justification. The scope is elastic deformation, not the separate Poisson, heat or wave projects in the same PDF.

## Material Outside the Seven Main Sections

Plan for title information and a short abstract before the main text; references, individual contribution statements and AI-use disclosure afterwards. Feedback questions and a short work plan are additional progress-draft material, not extra main sections or permanent substitutes for results.

Lucas's review relays a final Overleaf `clean,onecolumn` template, a ten-page limit including title/references with appendices excluded, and bibliography requirements. These must be checked against the original **Group Project Guidelines**, which are separate from the uploaded project-description PDF. This roadmap does not independently certify those formatting rules or impose a new page allocation.

## How to Use the Separate Section Threads

Use thread titles **Section 1: Existing introduction**, **Section 2: Mechanics and matrix**, **Section 3: Solvers and protocol**, **Section 4: Square example**, **Section 5: Objects and experiment design**, **Section 6: Results and validation**, and **Section 7: Conclusion**.

At the start of each thread, paste that section's entry and link this roadmap. Record the current source, any decisions still needed and the proposed owner. Section 1 is reused; Section 2 fixes notation; Section 3 fixes the protocol; Sections 4 and 5 can then develop in parallel; Section 6 depends on their evidence; Section 7 follows the discussion.

Each thread should return only its requested section/module and supporting artifacts, with outstanding questions stated clearly. Cross-section structural changes should be recorded here, rather than silently redefining the plan in another thread. Do not assemble or rewrite the whole report in this planning thread.

## Requested Review Before Adopting This Baseline

The two agents Simon tagged should review **this roadmap, not produce another full draft**. Check that the Section 1/2 boundary avoids repetition, that Section 4 prepares the reader for Sections 5/6, that each assignment topic has a clear home and that planned experiments are not presented as completed work. Return concrete edits or a short approval with remaining decisions; only then update the shared baseline.


## Repository Location

The editable structural source is `draft/ROADMAP.md`. The existing `draft/ROADMAP.pdf` predates the writing-rules consolidation; its pending-rules notice is obsolete. Section work lives under `draft/sections/`. Read `draft/WRITING_RULES.md` before drafting: it is the only shared writing guide. Incorporate new rules there, and reread all earlier sections after completing or revising each section to remove repetition. Older complete progress drafts are in `draft/reference/` and are not the new section-by-section draft.
