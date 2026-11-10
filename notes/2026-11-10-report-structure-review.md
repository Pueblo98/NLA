# Review of Simon and Hermes's seven-section outline

Lucas's Codex, 10 November 2026. Response to Simon's request for an assignment-compliance and readability review. This is a proposed outline and review, not a finished report or a claim of team approval.

## Verdict and sources

The progression from model to methods, square benchmark, further geometries and conclusions makes sense. The outline is not yet explicit enough to establish full coverage: it needs matrix analysis, validation, mesh refinement, experimental controls and the report's required opening and closing material. These can be integrated without adding many main sections.

Checked the supplied NLA-1/NLA-2 description on page 2, the report guidelines on pages 1–2, and the Lab 5 checklist. These course sources remain in `brief/`; they have not been copied into the public repository. No requirements from the other groups' PDE projects are being added here. The project description allows adaptation of its suggested workflow and solver selection with justification; its examples are not a requirement to run every named algorithm.

## Recommended structure

Before the numbered sections, include the title information and abstract. The abstract should summarize the problem, methods and actual findings.

1. **Introduction and objectives.** State the question, scope and motivation with cited background. Show the square and its supports/load in a small schematic so the reader has a concrete object from the start. Briefly explain that we seek static equilibrium. Reserve the detailed mechanics and assembly for Section 2.
2. **Mathematical model and discrete system.** Explain displacement → strain → stress → force balance, modelling assumptions, material parameters and units. Then explain boundary coordinates, triangular meshing, two displacement degrees of freedom per node, element assembly and sparse storage. Define supports and derive the reduced system $A x=b$, with $A=K_{FF}$ and $b=f_F-K_{FC}d_C$. Distinguish the unconstrained matrix's rigid-motion nullspace from the supported system's positive definiteness. Include symmetry, sparsity and the energy argument needed to justify solver selection. Introduce conditioning and explain how it will be measured rather than treating it as an incidental result.
3. **Numerical methods and comparison protocol.** Explain and justify the chosen direct and iterative solvers. Sparse LU, Cholesky on manageable systems, Gauss–Seidel, CG and PCG are a sensible core; existing comparisons with other methods can be retained selectively. Define the preconditioner, starting guess, residual norm, tolerances, iteration caps and failure classification. Use the same reduced system for method comparisons. Separate assembly, setup/factorization and solve costs, and compare solutions with a direct reference on the same mesh. An explicit inverse can illustrate the tiny example if desired; it is not needed as a production solver.
4. **Square benchmark: verification and solver behaviour.** Specify geometry, material, supports and load precisely. Show a small coupled system and a worked direct solve, followed by a larger system with convergence histories and a performance table. Label original/deformed plots and their displacement amplification factor. Check reactions, support values and agreement among solvers. Show the separate affine exact-solution test if used, making clear that its support conditions differ from the clamped benchmark. Solver iterations approximate one static equilibrium; they are not time steps in the body's motion.
5. **Additional geometries and experimental design.** Give ordered outer boundary coordinates, internal openings where relevant, mesh construction/refinement, supports and loading for each chosen object. Constrained Delaunay triangulation through `triangle` is the suggested route, not the only permitted route. State the question behind each geometry and the quantities held fixed in comparisons. Define load magnitudes, locations, support variants and material/thickness studies before presenting their results. A compact case table avoids repeating setup information in Section 6.
6. **Results, validation and discussion.** Organize around questions: effects of geometry/loads/supports; mesh resolution and conditioning; solver cost, accuracy and convergence; response to small load perturbations; and material/thickness dependence. Validate force balance including reactions, satisfaction of supports and solver agreement. Compare meshes under equivalent physical loading at matching physical locations or using consistent observables. Separate linear solver error on a fixed mesh from discretization error. Discuss numerical stability, unsuccessful runs and modelling/experimental limitations alongside the relevant evidence.
7. **Conclusions.** Answer the objectives using the measured results and state the main limitations and justified next steps. Do not introduce new experiments here.

After the numbered sections, include references, each person's contribution and AI-use disclosure. Use the required bibliography and citation system in the final LaTeX report.

## Flow and emphasis

The original Sections 1 and 2 overlap because both explain the mechanics and route to the equation. Make Section 1 a short introduction and combine the actual model derivation in Section 2. Introduce the square visually in the introduction, use it when defining variables, and return to it for the numerical benchmark. This keeps abstract notation connected to one physical example without repeating its full setup.

The proposed Section 5 works after the square if it is explicitly experimental design for the extended study. Describe each geometry and its purpose before showing its results; do not make the reader infer loads or supports from deformation plots.

Section 6 needs more than elasticity and thickness: the assignment's main focus is numerical linear algebra. Allocate substantial space to conditioning, sensitivity, solver comparison, refinement and validation. Use paired physical and numerical evidence, such as deformation plots alongside a residual history, performance table or mesh comparison. Explain what every figure establishes.

## Parameter-study controls

For a fixed mesh, geometry, Poisson ratio, support pattern and homogeneous prescribed displacements, the homogeneous linear elastic stiffness scales as $A=Et A_0$.

- With the assembled force vector fixed, $x=(Et)^{-1}A_0^{-1}b$, so increasing either $E$ or $t$ reduces displacement inversely.
- With physical edge traction (force per area) fixed, its equivalent nodal load also scales with $t$. Thickness then cancels from the displacement equation for this in-plane, plane-stress model. Holding force per boundary length fixed instead is a different loading experiment.
- Multiplying a matrix by a positive scalar leaves its 2-norm condition number unchanged. A body deforming less after a uniform change in $E$ or $t$ therefore does not by itself demonstrate improved conditioning. Changing Poisson ratio, geometry, mesh or supports can change matrix structure and conditioning.

These statements follow by substitution into the assembly/load formulas already documented in `drafts/Group02_Draft.md`, Section 3. They are modelling predictions to check, not new experimental findings. Nonzero imposed-displacement cases need their own interpretation because changing material parameters also changes the reduced right-hand side.

## Progress draft versus final report

For the Lab 5 progress draft, explicitly include objectives, model and boundary conditions, the matrix and unknowns, a small system with a direct solve, a larger iterative experiment, initial plots/tables with interpretation, questions for feedback, and a two-week plan. The checklist names illustrative methods; it does not require every one. Planned geometry work must be labelled as planned.

The current `drafts/Group02_Draft.md` already contains much of this coverage: Sections 2–3 formulate the model and matrix, Section 4 gives the small system, Sections 5–6 compare solvers, Section 7 discusses initial refinement, Section 8 covers validation/sensitivity/limitations, and Sections 9–10 contain feedback questions and the plan. Reuse and reorganize these contributions; absence from the new outline does not mean absence from the repository. More general geometries, broader support/load comparisons, a systematic mesh-error study and the self-contained notebook remain work identified in the saved draft.

For the final deliverable on 20 November, the report must be in English, use the course Overleaf template with `clean,onecolumn`, and fit within 10 pages including title and references; appendices are excluded. Do not shrink fonts or margins. Include numbered/referenced equations where needed, descriptive captions, axes, units, legends and error measures. Use `amsplain`, a `.bib` file and in-text `\cite` commands; identify reused code and disclose AI assistance. Deliver `Group02_Report.pdf` with one self-contained, self-explanatory `Group02_Notebook.ipynb`, including dependencies and data/source information. These are deliverable requirements, not extra report chapters.

The assembly currently used is the repository implementation. The professor's provided routine remains unidentified according to the saved draft; do not describe our implementation as the supplied routine. Retain that question for feedback until resolved.

## Thread handoff

For Simon and Hermes: keep the seven-section arc with the revised boundaries above. Make matrix analysis and validation visible in the outline, preserve the square as the running example, and define controlled experiments before reporting results. This note reviews structure and scope; it does not approve unseen report modules or replace the team's report source.
