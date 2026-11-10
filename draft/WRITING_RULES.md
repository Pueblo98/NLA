# Shared writing rules

Use this document for all report sections. Consolidated on 10 November 2026 at Lucas's request from the existing writing-rules proposal and Darius's review posted in the section-one Slack thread. It supersedes earlier notices that the shared rules were pending, including those in the roadmap and its PDF. Later team instructions should be incorporated here rather than in another guide.

## Style, length and readability

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
2. After drafting or revising a section, reread **all previous sections**. Remove overlapping explanations and repeated derivations; use cross-references and check that notation, assumptions and claims remain consistent. Keep detailed mechanics in Section 2 rather than repeating the introduction.
3. Check concision, paragraph flow, definitions, evidence, citations and figure references. Record unresolved questions in the section's README.
4. Compile the exact revised source and inspect its PDF before claiming the layout is checked. Check figures, references, pagination and readability, and keep the source and preview synchronized.
5. Keep section drafts subject to team review. This consolidation does not reopen the introduction or mark any report section final.

## Consolidation record

The duplicate proposals at `drafts/writing-rules.md` and `draft/reference/writing-rules-proposal.md` were merged here and removed. Darius's separate `WRITING_GUIDELINES.md` was not present in this checkout; the five rules in his Slack message (style, rigor, brevity, readability and review of previous sections) are incorporated above. If that file appears in a later update, compare it against this document, preserve any additional useful rule here, and remove the duplicate guide.

Workspace and section README references now point to this guide. The consolidation check found no broken targets among 55 relative links in the 11 affected guide and README documents.
