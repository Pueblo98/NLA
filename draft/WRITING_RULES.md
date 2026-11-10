# Shared writing rules

This is the **only shared writing guide** for the report. Edit this file when the team changes a rule; do not create another writing-rules file or folder. It combines the existing rules and Darius's review from the section-one thread.

## Style, length and readability

- Use the existing [introduction](sections/01-introduction/section.tex) as the style baseline: explain the physical meaning, introduce the necessary equation, then define its symbols. Later sections may need more detail, but should keep the same direct prose.
- Write direct, plain academic prose in English. Explain the purpose and physical meaning before introducing notation; explain technical terms when first needed.
- Use short, connected paragraphs, each with one main idea. Use lists only for actual steps or items to compare. Avoid filler, dense jargon, awkward opening lists and unnecessary commas.
- Keep the agreed scope and length. Remove repetition before changing layout. The final report must use the required Overleaf template with `clean,onecolumn`, retain its fonts, margins and spacing, and fit within 10 pages including title and references (appendices excluded).

## Mathematical rigor

- State assumptions, define every new symbol, subscript and matrix block where first used, and justify key claims. Distinguish modelling assumptions, cited results and our computed findings.
- Include equations and derivations needed to understand and reproduce the section. Place detailed derivations in the section responsible for them, and refer back to established definitions instead of repeating them.
- Use consistent notation. When relating equivalent systems, show the correspondence explicitly, for example
  \[
  Ax=b\quad\Longleftrightarrow\quad K_{FF}d_F=f_F-K_{FC}d_C,
  \]
  with \(F\) and \(C\) denoting free and prescribed displacement components, and explain \(A=K_{FF}\), \(x=d_F\), \(b=f_F-K_{FC}d_C\) in words. Number equations referenced later.
- Describe mesh choices accurately. Nonuniform triangles are not inherently incorrect; mesh size and quality can affect the approximation. Support accuracy claims with mesh comparisons rather than appearance alone, and distinguish discretization error from linear solver error.

## Figures, evidence and attribution

- Add a useful picture when explaining geometry or triangulation. Refer to each figure and table in the text, give it a descriptive caption, and explain what it demonstrates. Label axes, units, curves and error measures; state any displacement amplification factor.
- Identify illustrative meshes as examples, separate from computed project results. Support numerical claims with reproducible evidence and state limitations.
- Write in our own words and cite sources where ideas, equations, algorithms, figures, data or code are used. Use the template's `amsplain` bibliography and `\cite{...}` commands; check that citations and bibliography entries match. Include member contributions and the required AI-use disclosure. Keep full code listings outside the report.

## Review after each section

1. Read the section's scope in [ROADMAP.md](ROADMAP.md) before writing. Work in its folder under [sections/](sections/).
2. After drafting or revising Section \(n\), reread **every earlier section, 1 through \(n-1\)** before calling it complete. For Section 2, this means rereading Section 1. Remove overlapping explanations and repeated derivations; use cross-references and check that notation, assumptions and claims remain consistent. Keep detailed mechanics in Section 2 rather than repeating the introduction.
3. Check concision, paragraph flow, definitions, evidence, citations and figure references. Record unresolved questions in the section's README.
4. Compile the exact revised source and inspect its PDF before claiming the layout is checked. Check figures, references, pagination and readability, and keep the source and preview synchronized.
5. Keep section drafts subject to team review. This consolidation does not reopen the introduction or mark any report section final.

## Consolidation record

Rechecked on 10 November 2026 after Lucas's follow-up: the checkout contains this guide only. There is no separate `writing_rules/WRITING_GUIDELINES.md`, root `WRITING_GUIDELINES.md`, `drafts/writing-rules.md` or `draft/reference/writing-rules-proposal.md` to delete. Darius's posted rules on style, rigor, brevity, readability and review of earlier sections are included above. If another copy arrives from a teammate's checkout, merge any additional rules here and remove that copy.

The roadmap PDF predates this consolidation; its pending-rules notice is superseded by this guide. Repository entry points and section READMEs link here.
