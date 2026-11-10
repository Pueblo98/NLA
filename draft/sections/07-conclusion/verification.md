# Section 7 build and review verification

## Source scope

- Source basis: `origin/main` at `b138327cb949b5bc63ed10233fec12e37200c9a4`.
- Read the canonical writing rules, roadmap and complete Sections 1–6 before drafting. After drafting, reread the unchanged earlier content and checked Section 6's closing paragraphs against Section 7's opening.
- A fresh remote fetch before publication returned the same main revision.
- `git diff --exit-code b138327 --` for the writing rules, roadmap and all six predecessor folders returned success with no changes.
- Section 7 synthesizes previously recorded evidence; no numerical experiment or timing was rerun. This verification is not a new physical-validation claim.

## Actual build

Command from the module folder:

```sh
TECTONIC_BIN=/home/kleon/school/nla-section3-tools/tectonic sh build.sh
```

Tectonic version: **0.17.0**. Build exit status: **0**. The absolute compiler path describes this machine only; `build.sh` also discovers an installed Tectonic or falls back to pdfLaTeX.

- Preview: **1 page**, A4, 11 pt article with 25 mm margins.
- Page dimensions reported by PyMuPDF: 595.2800 × 841.8900 PDF points.
- Extracted text contains the Section 7 heading and all four conclusion paragraphs.
- Compiler log: no warnings, missing characters, undefined references, overfull boxes or underfull boxes.
- Text-span check: no left/right margin violations, allowing 2 PDF points of tolerance.
- Rendered and visually inspected the exact preview. Heading, four paragraphs and footer are readable; no clipping or overlap was observed. No font or margin reduction was used to obtain one page.

SHA-256 of the delivered `preview.pdf`:

```text
6baf979a5030eb34ea2ed0bdb374a25a26fc87e6a3d2edb6e86d7f6ac7ec559f
```

## Portable build check

Copied only `main.tex`, `section.tex` and `build.sh` into a fresh temporary directory and ran the build there with the same installed compiler. The build succeeded. Its page count, extracted text and rendered page pixels matched the delivered preview. No sibling section sources, bibliography file, Python package or numerical data are needed to compile Section 7.

The final course `clean,onecolumn` template and assembled report's ten-page limit have not been checked by this standalone build. Team review, factual updates following new Section 6 results, member contributions and the final AI-use disclosure remain open as described in the README.
