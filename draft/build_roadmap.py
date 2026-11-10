"""Render the planning Markdown only; no report content is assembled.
Run: uv run --with reportlab --with matplotlib --with pymupdf python build_roadmap.py
"""
from pathlib import Path
import hashlib
import html
import json
import re

from matplotlib import get_data_path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
import pymupdf

ROOT = Path(__file__).resolve().parent
MD = ROOT / 'ROADMAP.md'
PDF = MD.with_suffix('.pdf')
FONTS = Path(get_data_path()) / 'fonts/ttf'
for name, file in [('Roadmap','DejaVuSans.ttf'), ('Roadmap-Bold','DejaVuSans-Bold.ttf'), ('Roadmap-Italic','DejaVuSans-Oblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / file)))
pdfmetrics.registerFontFamily('Roadmap', normal='Roadmap', bold='Roadmap-Bold', italic='Roadmap-Italic', boldItalic='Roadmap-Bold')
body = ParagraphStyle('Body',fontName='Roadmap',fontSize=10.2,leading=13.5,spaceAfter=7,textColor=colors.HexColor('#253448'),allowWidows=0,allowOrphans=0)
heading = ParagraphStyle('Heading',parent=body,fontName='Roadmap-Bold',fontSize=12.2,leading=16,spaceBefore=10,spaceAfter=8,keepWithNext=True,textColor=colors.HexColor('#164666'))
title = ParagraphStyle('Title',parent=heading,fontSize=20,leading=25,spaceAfter=12)
bullet = ParagraphStyle('Bullet',parent=body,leftIndent=10,firstLineIndent=-8,spaceAfter=5)

def markup(text):
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`', r'<font color="#16536d">\1</font>', text)
    return text

source=MD.read_text()
story=[]
paragraph=[]
def flush():
    if paragraph:
        story.append(Paragraph(markup(' '.join(paragraph)),body))
        paragraph.clear()
for line in source.splitlines():
    if not line.strip(): flush()
    elif line=='<!-- pagebreak -->':
        flush();story.append(PageBreak())
    elif line.startswith('# '):
        flush();story.append(Paragraph(markup(line[2:]),title))
    elif line.startswith('## '):
        flush();story.append(Paragraph(markup(line[3:]),heading))
    elif line.startswith('- '):
        flush();story.append(Paragraph('• '+markup(line[2:]),bullet))
    else: paragraph.append(line)
flush()

def footer(c,doc):
    c.setStrokeColor(colors.HexColor('#b6c8d1'));c.line(46,37,A4[0]-46,37)
    c.setFont('Roadmap',8);c.setFillColor(colors.HexColor('#52677a'))
    c.drawString(46,24,'NLA section roadmap · Structure only · Review pending')
    c.drawRightString(A4[0]-46,24,str(doc.page))

doc=SimpleDocTemplate(str(PDF),pagesize=A4,leftMargin=46,rightMargin=46,topMargin=35,bottomMargin=50,title='NLA Report: Section Roadmap',author='Project planning thread')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
qa=ROOT/'qa';qa.mkdir(exist_ok=True)
with pymupdf.open(PDF) as document:
    text='\n'.join(p.get_text() for p in document)
    headings=re.findall(r'^## (\d+\. .+)$',source,re.M)
    assert len(headings)==7
    for h in headings: assert h in text,h
    assert 'It is not a report draft' in text
    assert 'Assignment Coverage Check' in text
    bad=[]
    for n,p in enumerate(document,1):
        for block in p.get_text('blocks'):
            if block[0]<43 or block[2]>p.rect.width-43 or block[1]<20 or block[3]>p.rect.height-12:
                bad.append((n,block[:4]))
        p.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2),alpha=False).save(qa/f'page-{n:02}.png')
    assert not bad,bad
    result={'pages':len(document),'seven_sections_present':True,'assignment_coverage_present':True,'text_within_bounds':True,'scope':'Planning roadmap only. Existing introduction reused; no full report assembled.','source_sha256':hashlib.sha256(MD.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'page_characters':[len(p.get_text()) for p in document]}
    (qa/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
print('MARKDOWN:',MD)
print('PDF:',PDF)
