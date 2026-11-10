# Section 1: Existing introduction / building the model

**Starting state: the existing introduction from the introduction thread, copied without rewriting its prose or equations.** This reorganisation does not reopen its review or claim that the whole report is final.

## Editable files

- [section.tex](section.tex): the introduction body, with no document preamble. Edit this file when the introduction thread requests a revision.
- [main.tex](main.tex): standalone A4/11 pt preview wrapper, with 25 mm margins and references on a separate page.
- [references.bib](references.bib): the introduction's bibliography.
- [figures/triangulation.pdf](figures/triangulation.pdf) and [figures/triangulation.png](figures/triangulation.png): existing figure, unchanged.
- [preview.pdf](preview.pdf): previously compiled and checked exact-source preview. It is not the combined final report.
- [build.sh](build.sh) and [make_triangulation.py](make_triangulation.py): existing build/figure tools.

The scope is [Section 1 of the roadmap](../../ROADMAP.md#1-building-the-model-existing-introduction). Read [WRITING_RULES.md](../../WRITING_RULES.md); the shared rules Simon will provide are still pending. Detailed mechanics belong in Section 2, not in another rewrite of this opening.

## Rebuild after an authorised edit

From this folder:

```sh
sh build.sh
cp main.pdf preview.pdf
```

Tectonic or a LaTeX distribution with pdflatex and bibtex is required. Compile the exact current source, then check the figure, citations and pagination before replacing the preview. Build products such as `main.pdf` remain ignored; `preview.pdf` is the review artifact.

## Provenance

The introduction sources were copied from `drafts/modules/01-building-model/` at the reorganisation's base revision. The preview is the exact-source `aa7b405` compilation, previously checked as one body page plus one references page. The relocation check compares its source and figure hashes with that compiled source. The original files remain in the old location for historical full-draft builds; future section edits belong here.

Historical author/build notes are preserved at [reference/introduction-source-notes.md](../../reference/introduction-source-notes.md). No prose was rewritten during relocation.
