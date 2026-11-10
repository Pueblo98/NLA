"""Render the visual seven-section progress report and its QA page images.

Run from NLA/: python drafts/build_visual_progress.py
The progress PDF uses a standalone layout; the final report must be transferred
to the course's required Overleaf template. No template-compliance claim is made.
"""
from pathlib import Path
import html
import re

import matplotlib
matplotlib.use("Agg")
from matplotlib import get_data_path, mathtext
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                               Preformatted, SimpleDocTemplate, Spacer, Table,
                               TableStyle)

HERE = Path(__file__).resolve().parent
QA = HERE / "qa" / "visual-progress"
QA.mkdir(parents=True, exist_ok=True)
fonts = Path(get_data_path()) / "fonts" / "ttf"
for name, filename in [("DejaVu", "DejaVuSans.ttf"), ("DejaVu-Bold", "DejaVuSans-Bold.ttf"),
                       ("DejaVu-Italic", "DejaVuSans-Oblique.ttf"), ("DejaVuMono", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                            italic="DejaVu-Italic", boldItalic="DejaVu-Bold")
WIDTH = A4[0] - 92
body = ParagraphStyle("body", fontName="DejaVu", fontSize=9.6, leading=13.3,
                      spaceAfter=7, textColor=colors.HexColor("#233043"),
                      allowWidows=0, allowOrphans=0)
heading = ParagraphStyle("heading", parent=body, fontName="DejaVu-Bold", fontSize=13,
                         leading=17, spaceBefore=8, spaceAfter=9, keepWithNext=True,
                         textColor=colors.HexColor("#17344f"))
title = ParagraphStyle("title", parent=heading, fontSize=22, leading=26, spaceAfter=15)
caption = ParagraphStyle("caption", parent=body, fontSize=8.2, leading=11, spaceAfter=10)
cell = ParagraphStyle("cell", parent=body, fontSize=8.3, leading=11.5, spaceAfter=0)
cache = {}
parser = mathtext.MathTextParser("path")


def equation(expr, size=10):
    key = (expr, size)
    if key not in cache:
        fn = QA / f"math_{len(cache):03d}.png"
        text = "$" + expr + "$"
        prop = matplotlib.font_manager.FontProperties(size=size)
        # Vector metrics at 72 dpi give point dimensions for ReportLab.
        metrics = parser.parse(text, dpi=72, prop=prop)
        mathtext.math_to_image(text, fn, prop=prop, dpi=220, format="png")
        cache[key] = (str(fn), float(metrics.width), float(metrics.height), float(metrics.depth))
    return cache[key]


def markup(text, size=10):
    parts = re.split(r"(\$[^$]+\$)", text)
    result = []
    for part in parts:
        if part.startswith("$") and part.endswith("$"):
            fn, w, h, depth = equation(part[1:-1], size)
            result.append(f'<img src="{fn}" width="{w}" height="{h}" valign="{-depth}"/>')
        else:
            result.append(html.escape(part))
    value = "".join(result)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", value)
    value = re.sub(r"`([^`]+)`", r'<font name="DejaVuMono" size="8">\1</font>', value)
    return value


def table(lines):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines]
    alignment = rows.pop(1)
    count = len(rows[0])
    widths = {2: [WIDTH*.68, WIDTH*.32], 3: [WIDTH*.22, WIDTH*.40, WIDTH*.38],
              5: [WIDTH*.27, WIDTH*.16, WIDTH*.21, WIDTH*.20, WIDTH*.16],
              6: [WIDTH*.14, WIDTH*.14, WIDTH*.16, WIDTH*.20, WIDTH*.16, WIDTH*.20]}[count]
    content = [[Paragraph(markup(value, 8.3), cell) for value in row] for row in rows]
    obj = Table(content, colWidths=widths, repeatRows=1, hAlign="LEFT")
    commands = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3edf5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), .6, colors.HexColor("#93aabd"))]
    for r in range(1, len(content)):
        if r % 2 == 0:
            commands.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#f3f6f9")))
    obj.setStyle(TableStyle(commands))
    return obj


subheading = ParagraphStyle("subheading", parent=heading, fontSize=10.5, leading=14,
                             spaceBefore=6, spaceAfter=7)


def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor("#bac6d1"))
    canvas.line(46, 38, A4[0]-46, 38)
    canvas.setFont("DejaVu", 8)
    canvas.setFillColor(colors.HexColor("#536579"))
    canvas.drawString(46, 25, "Group 02 · NLA · Progress report for discussion · 10 November 2026")
    canvas.drawRightString(A4[0]-46, 25, str(doc.page))


def main():
    lines = (HERE / "Group02_Visual_Progress.md").read_text().splitlines()
    story, index = [], 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line == "<!-- pagebreak -->":
            story.append(PageBreak())
        elif line.startswith("# "):
            story.append(Paragraph(markup(line[2:]), title))
        elif line.startswith("### "):
            story.append(Paragraph(markup(line[4:]), subheading))
        elif line.startswith("## "):
            story.append(Paragraph(markup(line[3:]), heading))
        elif line == "$$":
            expr = []
            index += 1
            while lines[index] != "$$":
                expr.append(lines[index])
                index += 1
            fn, w, h, _ = equation(" ".join(expr), 11)
            scale = min(1, WIDTH / w)
            obj = Image(fn, width=w*scale, height=h*scale)
            obj.hAlign = "CENTER"
            story.extend([Spacer(1, 4), obj, Spacer(1, 11)])
        elif line.startswith("|"):
            group = []
            while index < len(lines) and lines[index].startswith("|"):
                group.append(lines[index])
                index += 1
            story.extend([table(group), Spacer(1, 9)])
            continue
        elif line.startswith("!["):
            match = re.fullmatch(r"!\[(.*)\]\((.*)\)", line)
            path = HERE / match[2]
            with PILImage.open(path) as source:
                w, h = source.size
            heights = {"model_path.png": 90, "triangulation.png": 190,
                       "strain_intuition.png": 135, "small_square_matrix.png": 145,
                       "deformation_comparison.png": 175,
                       "geometry_candidates.png": 155, "progress_residuals.png": 180,
                       "refinement_summary.png": 145}
            factor = min(WIDTH/w, heights.get(path.name, 200)/h)
            obj = Image(str(path), width=w*factor, height=h*factor)
            obj.hAlign = "CENTER"
            story.append(KeepTogether([obj, Spacer(1, 5), Paragraph(markup(match[1], 8.2), caption)]))
        elif line.startswith("```"):
            code = []
            index += 1
            while not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            mono = ParagraphStyle("mono", fontName="DejaVuMono", fontSize=8.3, leading=12)
            story.extend([Preformatted("\n".join(code), mono), Spacer(1, 9)])
        elif line.startswith("- "):
            story.append(Paragraph("• " + markup(line[2:]), body))
        else:
            group = [line]
            while index+1 < len(lines) and lines[index+1].strip():
                index += 1
                group.append(lines[index])
            story.append(Paragraph(markup(" ".join(group)), body))
        index += 1
    doc = SimpleDocTemplate(str(HERE / "Group02_Visual_Progress.pdf"), pagesize=A4,
                            leftMargin=46, rightMargin=46, topMargin=38, bottomMargin=52,
                            title="Elastic Deformation of Two-Dimensional Objects — Group 02 Progress Draft",
                            author="NLA Group 02")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    import pymupdf
    pdf = pymupdf.open(HERE / "Group02_Visual_Progress.pdf")
    for n, page in enumerate(pdf, 1):
        page.get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4), alpha=False).save(QA / f"page-{n:02d}.png")
    from PIL import ImageOps, ImageDraw
    thumbnails = []
    for n in range(1, len(pdf) + 1):
        with PILImage.open(QA / f"page-{n:02d}.png") as source:
            thumb = ImageOps.contain(source.convert("RGB"), (300, 425))
        tile = PILImage.new("RGB", (316, 451), "#d8dfe4")
        tile.paste(thumb, ((316-thumb.width)//2, 18))
        ImageDraw.Draw(tile).text((8, 3), str(n), fill="black")
        thumbnails.append(tile)
    columns = 5
    sheet = PILImage.new("RGB", (columns*316, ((len(thumbnails)+columns-1)//columns)*451), "white")
    for i, tile in enumerate(thumbnails):
        sheet.paste(tile, ((i % columns)*316, (i // columns)*451))
    sheet.save(QA / "contact-sheet.png")
    print(f"Built and rendered {len(pdf)} pages: {HERE / 'Group02_Visual_Progress.pdf'}")


if __name__ == "__main__":
    main()
