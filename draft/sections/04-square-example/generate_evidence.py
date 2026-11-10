"""Reproduce Section 4 only. Bundled code is an unchanged snapshot of main 9736c8e.
Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python generate_evidence.py
Outputs are data/ and figures/. No historical timing values are imported.
"""
from pathlib import Path
import csv
import hashlib
import json
import os
import platform
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'reproduction'))
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.linalg import cholesky, solve_triangular, lu_factor, lu_solve, inv, eigvalsh
from scipy.sparse.linalg import splu, cg
from plate import force_driven
from progress_benchmark import iterative, METHODS, TOL, CAP, known_answer_checks

DATA, FIG = ROOT / 'data', ROOT / 'figures'
DATA.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
known_answer_checks()


def checks(s, x):
    d = s['d'].copy()
    d[s['free']] = x
    raw = s['K'] @ d - s['f']
    reaction = np.zeros_like(d)
    reaction[s['constrained']] = raw[s['constrained']]
    total = (s['f'] + reaction).reshape(-1, 2)
    xy = s['nodes']
    result = dict(relative_residual=float(np.linalg.norm(raw[s['free']])/np.linalg.norm(s['b'])),
                  maximum_support_displacement_m=float(np.max(np.abs(d[s['constrained']]))),
                  reaction_sum_N=reaction.reshape(-1, 2).sum(axis=0).tolist(),
                  force_imbalance_N=total.sum(axis=0).tolist(),
                  moment_imbalance_Nm=float(np.sum(xy[:, 0]*total[:, 1]-xy[:, 1]*total[:, 0])))
    return d, result

small = force_driven(2)
A, b = small['A'].toarray(), small['b']
L = cholesky(A, lower=True)
y = solve_triangular(L, b, lower=True)
x = solve_triangular(L.T, y)
xs = {'Cholesky': x, 'Pivoted LU': lu_solve(lu_factor(A), b), 'Explicit inverse': inv(A) @ b}
dsmall, csmall = checks(small, x)
for name, a in dict(small_A_N_per_m=A, small_b_N=b, small_x_m=x,
                    small_L=L, small_y=y, small_nodes_m=small['nodes'],
                    small_triangles=small['triangles'], small_free_dofs=small['free']).items():
    np.savetxt(DATA / (name+'.csv'), a, delimiter=',', fmt='%.17g')
ev = eigvalsh(A)
assert ev[0] > 0
np.testing.assert_allclose(A,A.T,rtol=0,atol=1e-6)
small_result = dict(params=small['params'], unknowns=len(b),
                    condition_number=float(ev[-1]/ev[0]),
                    eigenvalues_min_max=[float(ev[0]),float(ev[-1])],
                    scaled_first_row=(A[0]/1e9).tolist(),
                    free_nodes=[1,2,4,5,7,8],
                    displacements_mm=(x.reshape(-1,2)*1e3).tolist(),
                    direct_residuals={k:float(np.linalg.norm(b-A@v)/np.linalg.norm(b)) for k,v in xs.items()},
                    max_direct_difference=float(max(np.linalg.norm(v-x)/np.linalg.norm(x) for v in xs.values())),
                    validation=csmall)

large = force_driven(20)
A, b = large['A'], large['b']
reference = splu(A.tocsc()).solve(b)
dlarge, clarge = checks(large, reference)
rows, histories = [], {}
for method in METHODS:
    x, k, status, hist = iterative(A,b,method)
    times=[]
    for repeat in range(3):
        start=perf_counter()
        xt, kt, st, _=iterative(A,b,method,history=False)
        times.append(perf_counter()-start)
        assert kt == k and st == status
        np.testing.assert_allclose(xt,x,rtol=1e-12,atol=1e-16)
    rho=float(np.linalg.norm(b-A@x)/np.linalg.norm(b))
    _, validation=checks(large,x)
    row=dict(method=method, iterations=k, status=status, accepted=bool(np.isfinite(rho) and rho<TOL),
             relative_residual=rho, reference_difference=float(np.linalg.norm(x-reference)/np.linalg.norm(reference)),
             timing_runs_seconds=times,best_seconds=min(times),validation=validation)
    rows.append(row)
    histories[method]=hist
    assert len(hist)==k+1
    print(json.dumps({key:val for key,val in row.items() if key!='validation'}),flush=True)

# Independent geometric/load invariants and support-only reaction checks.
for s, x in [(small, xs['Cholesky']), (large, reference)]:
    pts=s['nodes'][s['triangles']]
    a,bv=pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]
    twice_area=a[:,0]*bv[:,1]-a[:,1]*bv[:,0]
    assert (twice_area>0).all()
    np.testing.assert_allclose(twice_area.sum()/2,1,rtol=0,atol=1e-14)
    expected=np.zeros_like(s['f']).reshape(-1,2)
    right=s['side']['right']
    edge_force=1e6/s['params']['ny']
    expected[right,0]=edge_force
    expected[right[[0,-1]],0]=edge_force/2
    np.testing.assert_allclose(s['f'],expected.ravel(),rtol=1e-14,atol=1e-8)
    _, v=checks(s,x)
    assert v['maximum_support_displacement_m']==0
    assert np.linalg.norm(v['force_imbalance_N'])<1e-6
    assert abs(v['moment_imbalance_Nm'])<1e-6
    assert v['relative_residual']<1e-10

# Keep selected actual CG iterates for interpreting the algebraic convergence.
snapshots={0: np.zeros_like(b)}
count=0
# A and b still denote the large reduced system.
def save_iterate(xk):
    global count
    count+=1
    if count in (10,50,100):
        snapshots[count]=xk.copy()
cgx,info=cg(A,b,rtol=TOL,atol=0,maxiter=CAP,callback=save_iterate)
snapshots[count]=cgx.copy()
np.savez_compressed(DATA/'cg_iterates.npz',**{f'k{k}':v for k,v in snapshots.items()})
np.savez_compressed(DATA/'large_reference.npz',nodes=large['nodes'],triangles=large['triangles'],
                    displacement_m=dlarge,free=large['free'])

plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(9,3.4),layout='constrained')
ax=axes[0]
xy=small['nodes']
ax.triplot(xy[:,0],xy[:,1],small['triangles'],color='#6c7d8d',lw=1)
ax.scatter(xy[:,0],xy[:,1],s=14,color='#24364a',zorder=3)
for i,(xx,yy) in enumerate(xy):
    ax.text(xx+.025,yy+.025,str(i),fontsize=9)
ax.plot([0,0],[0,1],color='#c04730',lw=4,label='clamp: both components zero')
for yy in np.linspace(.08,.92,5):
    ax.annotate('',xy=(1.19,yy),xytext=(1.01,yy),arrowprops={'arrowstyle':'->','color':'#176a91','lw':1.5})
ax.text(.65,1.16,'traction: 100 MPa →',fontsize=9)
ax.set(xlim=(-.12,1.28),ylim=(-.1,1.25),xlabel='x [m]',ylabel='y [m]',title='(a) Small mesh and boundary conditions',aspect='equal')
ax=axes[1]
amp=200
moved=large['nodes']+amp*dlarge.reshape(-1,2)
ax.triplot(large['nodes'][:,0],large['nodes'][:,1],large['triangles'],color='#c7cdd2',lw=.35)
ax.triplot(moved[:,0],moved[:,1],large['triangles'],color='#176a91',lw=.4)
ax.plot([],[],color='#c7cdd2',label='original')
ax.plot([],[],color='#176a91',label='deformed, ×200')
ax.set(xlabel='x [m]',ylabel='y [m]',title='(b) Large-mesh equilibrium',aspect='equal')
ax.legend(loc='upper left',fontsize=8)
fig.savefig(FIG/'square_geometry.pdf')
plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(9,2.8),layout='constrained')
colors={'CG':'#176a91','PCG (diagonal)':'#bd6031','Gauss-Seidel':'#368768','Jacobi':'#ac2c4d'}
for name in ['CG','PCG (diagonal)','Gauss-Seidel','Jacobi']:
    h=histories[name]
    axes[0].semilogy(range(len(h)),h,label=name,color=colors[name],lw=1.1)
axes[0].axhline(TOL,color='black',ls='--',lw=.8)
axes[0].set(xlabel='iteration / complete sweep',ylabel='relative residual ρ',xlim=(0,CAP),ylim=(1e-9,1e11),title='(a) Selected residual histories')
axes[0].set_xscale('symlog',linthresh=1)
axes[0].set_xticks([0,10,100,1000,20000],labels=['0','10','100','1000','20000'])
axes[0].legend(fontsize=7,ncol=2,loc='upper right')
for k,xk in snapshots.items():
    dk=large['d'].copy();dk[large['free']]=xk
    axes[1].plot(large['nodes'][large['side']['right'],1],dk.reshape(-1,2)[large['side']['right'],0]*1e3,label=f'CG k={k}',lw=1)
axes[1].plot(large['nodes'][large['side']['right'],1],dlarge.reshape(-1,2)[large['side']['right'],0]*1e3,color='black',ls='--',lw=1.2,label='LU reference')
axes[1].set(xlabel='right-edge height y [m]',ylabel='horizontal displacement [mm]',title='(b) Iterates approach the same solution')
axes[1].legend(fontsize=6.5,ncol=2)
for ax in axes:ax.grid(alpha=.18)
fig.savefig(FIG/'square_convergence.pdf')
plt.close(fig)

cpu=platform.processor()
if Path('/proc/cpuinfo').exists():
    cpu=next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')),cpu)
environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                 matplotlib=matplotlib.__version__,platform=platform.platform(),cpu=cpu,
                 thread_variables={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})
result=dict(source_revision='9736c8e9cf26630a6772786a74972ec8ff57db75',environment=environment,
            small=small_result,large=dict(params=large['params'],nodes=len(large['nodes']),triangles=len(large['triangles']),
            unknowns=len(reference),validation=clarge,
            right_edge_u_mm=(dlarge.reshape(-1,2)[large['side']['right'],0]*1e3).tolist()),
            tolerance=TOL,iteration_cap=CAP,solvers=rows,
            cg_snapshots={str(k):dict(relative_residual=float(np.linalg.norm(large['b']-large['A']@v)/np.linalg.norm(large['b'])),
                                    reference_difference=float(np.linalg.norm(v-reference)/np.linalg.norm(reference))) for k,v in snapshots.items()})
(DATA/'results.json').write_text(json.dumps(result,indent=2)+'\n')
(DATA/'histories.json').write_text(json.dumps(histories)+'\n')
with (DATA/'solver_comparison.csv').open('w',newline='') as f:
    keys=['method','iterations','status','accepted','relative_residual','reference_difference','best_seconds']
    writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
    writer.writerows({k:r[k] for k in keys} for r in rows)
def latex_number(value):
    mantissa, exponent = f'{value:.3e}'.split('e')
    return rf'${mantissa}\times10^{{{int(exponent)}}}$'

latex_rows = []
for row in rows:
    outcome = 'Pass' if row['accepted'] else ('Guard' if row['status']=='divergence_guard' else 'Cap')
    label = row['method'].replace('Gauss-Seidel', 'Gauss--Seidel').replace('PCG (diagonal)', 'Diagonal PCG')
    latex_rows.append(f"{label} & {row['iterations']} & {latex_number(row['relative_residual'])} & {latex_number(row['reference_difference'])} & {row['best_seconds']:.3g} & {outcome}" + r' \\')
table_start = r'''\begin{tabular}{lrrrrl}
\toprule
Method & Iterations & $\rho$ & $e_{\rm ref}$ & Time [s] & Outcome\\
\midrule
'''
(DATA/'solver_rows.tex').write_text(table_start+'\n'.join(latex_rows)+'\n'+r'\bottomrule'+'\n'+r'\end{tabular}'+'\n')
print('SMALL:',json.dumps(small_result,indent=2))
print('LARGE VALIDATION:',json.dumps(clarge))
print('ENVIRONMENT:',json.dumps(environment))
print('PASS: positive triangle areas, unit area, exact nodal load pattern, supports, force/moment equilibrium, direct residuals, solver repeat consistency.')
