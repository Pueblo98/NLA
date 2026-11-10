"""Check the delivered evidence and exact compiled preview (requires PyMuPDF)."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
import pymupdf

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
r=json.loads((DATA/'results.json').read_text())
hist=json.loads((DATA/'histories.json').read_text())
for s in r['solvers']:
    assert s['accepted']==(np.isfinite(s['relative_residual']) and s['relative_residual']<r['tolerance'])
    assert len(hist[s['method']])==s['iterations']+1
    assert len(s['timing_runs_seconds'])==3
    assert s['best_seconds']==min(s['timing_runs_seconds'])
A=np.loadtxt(DATA/'small_A_N_per_m.csv',delimiter=',')
b=np.loadtxt(DATA/'small_b_N.csv',delimiter=',')
x=np.loadtxt(DATA/'small_x_m.csv',delimiter=',')
L=np.loadtxt(DATA/'small_L.csv',delimiter=',')
y=np.loadtxt(DATA/'small_y.csv',delimiter=',')
np.testing.assert_allclose(L@L.T,A,rtol=0,atol=2e-6)
assert np.linalg.norm(L@y-b)/np.linalg.norm(b)<1e-14
assert np.linalg.norm(L.T@x-y)/np.linalg.norm(y)<1e-14
assert np.linalg.norm(A@x-b)/np.linalg.norm(b)<1e-14
np.testing.assert_array_equal(91*A[0]/1e9,[270,-65,-100,30,-70,65,0,-65,0,0,0,0])
np.testing.assert_array_equal(b,[0,0,250000,0,0,0,500000,0,0,0,250000,0])
for name,digest in json.loads((ROOT/'reproduction/source_hashes.json').read_text()).items():
    assert hashlib.sha256((ROOT/'reproduction'/Path(name).name).read_bytes()).hexdigest()==digest
log=(ROOT/'build/main.log').read_text()
for word in ['Overfull','Underfull','undefined','Missing character']:
    assert word not in log,word
pdf=pymupdf.open(ROOT/'preview.pdf')
texts=[]
issues=[]
margin=25*72/25.4
for i,page in enumerate(pdf):
    texts.append(page.get_text())
    page.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(ROOT/f'build/final-{i+1}.png')
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<margin-3 or x1>page.rect.width-margin+3:
                    issues.append([i+1,span['text'],span['bbox']])
assert not issues,issues
text='\n'.join(texts)
assert '??' not in text
for term in ['A simple square demonstration','Cholesky','Gauss','convergence','References']:
    assert term in text,term
report=dict(pages=len(pdf),page_size_points=list(pdf[0].rect),
            pdf_sha256=hashlib.sha256((ROOT/'preview.pdf').read_bytes()).hexdigest(),
            pdf_bytes=(ROOT/'preview.pdf').stat().st_size,
            horizontal_margin_violations=issues,
            compiler_warning_checks='No overfull/underfull boxes, undefined references or missing characters',
            evidence_checks='PASS: source hashes, timings, strict acceptance, histories, Cholesky arrays, displayed load and coupled first row',
            numerical_environment=r['environment'])
(ROOT/'build/verification.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'build/extracted.txt').write_text(text)
print(json.dumps(report,indent=2))
