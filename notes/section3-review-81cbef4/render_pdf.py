"""Render unchanged review PDF and extract text using existing project dependencies.

From the repository root:
PYTHONPATH=.build-deps python3 notes/section3-review-81cbef4/render_pdf.py
"""
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent
out = ROOT / "rendered"
out.mkdir(exist_ok=True)
with pymupdf.open(ROOT / "inputs" / "preview.pdf") as doc:
    print(f"Pages: {len(doc)}")
    for number, page in enumerate(doc, 1):
        page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(out / f"page-{number}.png")
        text = page.get_text()
        (out / f"page-{number}.txt").write_text(text)
        print(f"Page {number}: {page.rect}, {len(text)} extracted characters")
