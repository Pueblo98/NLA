"""Scoped Section 6 checks; reuse the unchanged Section 4 finite elements.
Run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1.
No solver timings or proposed Section 5 object families are generated.
"""
from pathlib import Path
import csv
import hashlib
import json
import os
import platform
import sys
import numpy as np
import scipy
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh, splu, norm as sparse_norm

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'reproduction'))
from plate import force_driven


def linear_edge_load(nodes, edges, q):
    """Exactly integrate linear nodal line loads q [N/m] against P1 traces."""
    forces = np.zeros_like(nodes, dtype=float)
    for a, b in edges:
        length = np.linalg.norm(nodes[b] - nodes[a])
        forces[a] += length * (2*q[a] + q[b]) / 6
        forces[b] += length * (q[a] + 2*q[b]) / 6
    return forces.ravel()


def observable_weights(nodes, right):
    """Full-DOF weights: integrated mean ux and boundary-interpolated midpoint."""
    ids = np.asarray(right)[np.argsort(nodes[right, 1])]
    y = nodes[ids, 1]
    length = y[-1] - y[0]
    weights = {key: np.zeros(2*len(nodes))
               for key in ('mean_ux', 'midpoint_ux', 'midpoint_uy')}
    dy = np.diff(y)
    weights['mean_ux'][2*ids[:-1]] += dy/(2*length)
    weights['mean_ux'][2*ids[1:]] += dy/(2*length)
    midpoint = (y[0] + y[-1])/2
    j = np.searchsorted(y, midpoint, side='right') - 1
    alpha = (midpoint-y[j])/(y[j+1]-y[j])
    for component, key in enumerate(('midpoint_ux', 'midpoint_uy')):
        weights[key][2*ids[j]+component] = 1-alpha
        weights[key][2*ids[j+1]+component] = alpha
    return weights


def equilibrium(s, x, f=None):
    """Only constrained components of Kd-f are reactions; free errors stay visible."""
    f = s['f'] if f is None else f
    d = s['d'].copy()
    d[s['free']] = x
    raw = s['K'] @ d - f
    reaction = np.zeros_like(d)
    reaction[s['constrained']] = raw[s['constrained']]
    xy = s['nodes']
    forces = f.reshape(-1, 2)
    total = (f + reaction).reshape(-1, 2)
    force_scale = np.linalg.norm(forces, axis=1).sum()
    length = np.linalg.norm(np.ptp(xy, axis=0))
    moment = lambda v: float(np.sum(xy[:, 0]*v[:, 1]-xy[:, 1]*v[:, 0]))
    checks = dict(force_scale_N=float(force_scale), characteristic_length_m=float(length),
                  applied_force_N=forces.sum(axis=0).tolist(), applied_moment_Nm=moment(forces),
                  reaction_force_N=reaction.reshape(-1, 2).sum(axis=0).tolist(),
                  reaction_moment_Nm=moment(reaction.reshape(-1, 2)),
                  force_imbalance_N=total.sum(axis=0).tolist(), moment_imbalance_Nm=moment(total),
                  normalized_force_imbalance=float(np.linalg.norm(total.sum(axis=0))/force_scale),
                  normalized_moment_imbalance=float(abs(moment(total))/(force_scale*length)),
                  maximum_support_displacement_m=float(np.max(np.abs(d[s['constrained']]))),
                  free_full_residual_norm_N=float(np.linalg.norm(raw[s['free']])))
    return d, reaction, checks


def spectrum(A):
    """Extremal Ritz estimates with deterministic start and checked defects."""
    i = np.arange(1, A.shape[0]+1, dtype=float)
    v0 = np.sin(i) + .3*np.cos(2*i)
    v0 /= np.linalg.norm(v0)
    values, vectors, defects, absolute = [], [], [], []
    for which in ('SA', 'LA'):
        ev, vec = eigsh(A, k=1, which=which, v0=v0, tol=1e-11, maxiter=100000)
        value, vector = float(ev[0]), vec[:, 0]
        defect = float(np.linalg.norm(A@vector-value*vector))
        relative = defect/(abs(value)*np.linalg.norm(vector))
        assert value > 0 and relative < 1e-7
        values.append(value)
        vectors.append(vector)
        absolute.append(defect)
        defects.append(float(relative))
    return dict(lambda_min=values[0], lambda_max=values[1],
                condition_estimate=values[1]/values[0],
                absolute_eigenpair_defects=absolute, relative_eigenpair_defects=defects), np.array(vectors)


def sparse_arrays(name, A):
    A = A.tocsr()
    return {name+'_data': A.data, name+'_indices': A.indices,
            name+'_indptr': A.indptr, name+'_shape': np.array(A.shape)}


def run_evidence(data=ROOT/'data', make_figure=True):
    """Execute the four square cases, n20 sensitivity checks, and separate patch test."""
    data = Path(data)
    data.mkdir(parents=True, exist_ok=True)
    rows, csv_rows = [], []
    saved20 = None
    for n in (5, 10, 20, 40):
        s = force_driven(n)
        A, b = s['A'], s['b']
        lu = splu(A.tocsc())
        x = lu.solve(b)
        residual = b-A@x
        residual_norm = float(np.linalg.norm(residual))
        d, reaction, validation = equilibrium(s, x)
        spec, vectors = spectrum(A)
        weights = observable_weights(s['nodes'], s['side']['right'])
        observables = {}
        for key, w in weights.items():
            value = float(w@d)
            uncertainty = float(np.linalg.norm(w[s['free']])*residual_norm/spec['lambda_min'])
            difference = abs(value-rows[-1]['observables'][key]['value_m']) if rows else None
            observables[key] = dict(value_m=value, algebraic_uncertainty_estimate_m=uncertainty,
                                    successive_absolute_difference_m=difference)
        row = dict(n=n, params=s['params'], nodes=len(s['nodes']), triangles=len(s['triangles']),
                   unknowns=len(b), residual_norm_N=residual_norm,
                   relative_residual=float(residual_norm/np.linalg.norm(b)),
                   relative_symmetry_defect=float(sparse_norm(A-A.T)/sparse_norm(A)),
                   spectrum=spec, observables=observables, validation=validation)
        assert row['relative_residual'] < 1e-10
        assert row['relative_symmetry_defect'] < 1e-14
        assert validation['normalized_force_imbalance'] < 1e-10
        assert validation['normalized_moment_imbalance'] < 1e-10
        assert validation['maximum_support_displacement_m'] == 0
        np.savez_compressed(data/f'square_n{n}.npz', **sparse_arrays('A', A), **sparse_arrays('K', s['K']),
                            nodes_m=s['nodes'], triangles=s['triangles'], free=s['free'],
                            constrained=s['constrained'], prescribed_m=s['prescribed'],
                            right=s['side']['right'], f_N=s['f'], b=b, x=x, displacement_m=d,
                            reaction_N=reaction, residual_N=residual, eigenvectors=vectors,
                            eigenvalues=np.array([spec['lambda_min'], spec['lambda_max']]),
                            **{'w_'+key:w for key, w in weights.items()})
        rows.append(row)
        flat = dict(n=n, nodes=row['nodes'], triangles=row['triangles'], unknowns=len(b),
                    relative_residual=row['relative_residual'], condition_estimate=spec['condition_estimate'],
                    lambda_min_N_per_m=spec['lambda_min'], lambda_max_N_per_m=spec['lambda_max'],
                    normalized_force_imbalance=validation['normalized_force_imbalance'],
                    normalized_moment_imbalance=validation['normalized_moment_imbalance'])
        for key, obs in observables.items():
            flat.update({key+'_'+label:value for label, value in obs.items()})
        csv_rows.append(flat)
        print('REFINEMENT', json.dumps(flat), flush=True)
        if n == 20:
            saved20 = (s, lu, x, spec)

    s, lu, x, original_spec = saved20
    A, b = s['A'], s['b']
    diagonal = A.diagonal()
    D = diags(1/np.sqrt(diagonal))
    S = (D@A@D).tocsr()
    scaled_spec, scaled_vectors = spectrum(S)
    lo, hi = scaled_spec['lambda_min'], scaled_spec['lambda_max']
    omega = .5  # Match the measured damping in Sections 3 and 4.
    scaling = dict(original_spectrum=original_spec, scaled_spectrum=scaled_spec,
                   jacobi_spectral_radius=max(abs(1-lo), abs(1-hi)),
                   damping_omega=omega,
                   damped_jacobi_spectral_radius=max(abs(1-omega*lo), abs(1-omega*hi)))
    np.savez_compressed(data/'scaled_n20.npz', **sparse_arrays('S', S), diagonal=diagonal,
                        eigenvectors=scaled_vectors, eigenvalues=np.array([lo, hi]))
    print('SCALING', json.dumps(scaling), flush=True)

    right = s['side']['right']
    edges = np.column_stack([right[:-1], right[1:]])
    q = np.zeros_like(s['nodes'])
    q[:, 0] = 2*s['nodes'][:, 1]/s['params']['Ly'] - 1
    raw_increment = linear_edge_load(s['nodes'], edges, q)
    amplitude = .001*np.linalg.norm(b)/np.linalg.norm(raw_increment[s['free']])
    perturbations = []
    for name, delta_f in [('proportional', .001*s['f']),
                          ('linear_redistribution', amplitude*raw_increment)]:
        delta_b = delta_f[s['free']]
        changed_b = b+delta_b
        changed_x, delta_x = lu.solve(changed_b), lu.solve(delta_b)
        actual_delta = changed_x-x
        changed_residual = changed_b-A@changed_x
        increment_residual = delta_b-A@delta_x
        d, reaction, validation = equilibrium(s, changed_x, s['f']+delta_f)
        relative_b = float(np.linalg.norm(delta_b)/np.linalg.norm(b))
        relative_x = float(np.linalg.norm(actual_delta)/np.linalg.norm(x))
        xy, forces = s['nodes'], delta_f.reshape(-1, 2)
        mismatch = float(np.linalg.norm(actual_delta-delta_x))
        p = dict(name=name, relative_rhs_change=relative_b, relative_displacement_change=relative_x,
                 amplification=relative_x/relative_b,
                 superposition_mismatch_norm_m=mismatch,
                 superposition_mismatch_relative_to_delta_x=mismatch/float(np.linalg.norm(delta_x)),
                 changed_residual_norm_N=float(np.linalg.norm(changed_residual)),
                 changed_relative_residual=float(np.linalg.norm(changed_residual)/np.linalg.norm(changed_b)),
                 increment_residual_norm_N=float(np.linalg.norm(increment_residual)),
                 increment_relative_residual=float(np.linalg.norm(increment_residual)/np.linalg.norm(delta_b)),
                 added_force_N=forces.sum(axis=0).tolist(),
                 added_moment_Nm=float(np.sum(xy[:, 0]*forces[:, 1]-xy[:, 1]*forces[:, 0])),
                 line_load_amplitude_N_per_m=float(amplitude) if name == 'linear_redistribution' else None,
                 validation=validation)
        assert p['changed_relative_residual'] < 1e-10 and p['increment_relative_residual'] < 1e-10
        assert p['superposition_mismatch_relative_to_delta_x'] < 1e-8
        assert validation['normalized_force_imbalance'] < 1e-10
        assert validation['normalized_moment_imbalance'] < 1e-10
        perturbations.append(p)
        np.savez_compressed(data/f'perturbation_{name}_n20.npz', delta_f_N=delta_f, delta_b=delta_b,
                            changed_f_N=s['f']+delta_f, changed_b=changed_b, changed_x=changed_x,
                            delta_x=delta_x, actual_delta_x=actual_delta, displacement_m=d,
                            reaction_N=reaction, changed_residual_N=changed_residual,
                            increment_residual_N=increment_residual)
        print('PERTURBATION', json.dumps(p), flush=True)

    roller = force_driven(4, support='roller')
    rx = splu(roller['A'].tocsc()).solve(roller['b'])
    rd, rr, rv = equilibrium(roller, rx)
    exact = roller['params']['p']/roller['params']['E'] * roller['nodes']*np.array([1., -roller['params']['nu']])
    error = float(np.linalg.norm(rd-exact.ravel())/np.linalg.norm(exact))
    assert error < 1e-11
    roller_check = dict(n=4, params=roller['params'], relative_nodal_error=error, validation=rv,
                        note='Separate affine roller patch test; not the clamped refinement benchmark.')
    np.savez_compressed(data/'roller_n4.npz', nodes_m=roller['nodes'], displacement_m=rd,
                        exact_displacement_m=exact.ravel(), reaction_N=rr)
    print('ROLLER', json.dumps(roller_check), flush=True)

    import matplotlib
    source_paths = [ROOT/'generate_evidence.py', ROOT/'test_evidence.py', ROOT/'requirements.txt']
    source_paths += [ROOT/'reproduction'/name for name in ('plate.py', 'elasticity.py', 'system_tools.py')]
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    section4 = ROOT.parent/'04-square-example'
    unchanged = {name: (ROOT/'reproduction'/name).read_bytes() == (section4/'reproduction'/name).read_bytes()
                 for name in ('plate.py', 'elasticity.py', 'system_tools.py')}
    assert all(unchanged.values())
    timing_paths = [section4/'data'/name for name in ('results.json', 'solver_comparison.csv')]
    result = dict(environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                                   matplotlib=matplotlib.__version__, platform=platform.platform(),
                                   thread_variables={k:os.environ.get(k) for k in
                                                     ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')}),
                  code_sha256=hashes, section4_copies_byte_identical=unchanged,
                  unchanged_section4_timing_source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in timing_paths},
                  definitions=dict(
                      scope='Structured unit-square force_driven clamp, P1/CST plane stress; no Section 5 object families or new timing benchmarks.',
                      physical_inputs='Lx=Ly=1 m; E=200e9 Pa; nu=0.3; t=0.01 m; p=100e6 Pa; q=t*p=1e6 N/m; bl-tr diagonals.',
                      solver='scipy.sparse.linalg.splu(A.tocsc()); n20 reuses one factorization for baseline and both perturbation solves.',
                      residual='True reduced residual r=b-Ax; relative residual ||r||_2/||b||_2. Full free residual also recorded separately.',
                      reactions='R_c=(Kd-f)_c; R_free=0. Total force and moment use f+R, not unmasked Kd-f.',
                      equilibrium='Fscale=sum_i ||f_i||_2; Lchar=||max(nodes)-min(nodes)||_2. ||sum(f+R)||_2/Fscale; |sum(x Fy-y Fx)|/(Fscale Lchar). Moments about (0,0); changed cases use changed full f.',
                      symmetry='||A-A.T||_F/||A||_F.',
                      spectrum='eigsh k=1, which=SA and LA, tol=1e-11, maxiter=100000. v0_i=sin(i)+0.3 cos(2i), i=1..N, normalized. Positive Ritz values and ||Av-lambda v||_2/(|lambda| ||v||_2)<1e-7 required; estimates, not certified spectral enclosures.',
                      observables='mean_ux is exact P1 right-edge trace integral / edge length. Midpoint ux,uy at (1,0.5) are linearly interpolated on the boundary, including odd n=5.',
                      uncertainty='eta_w=||w_free||_2 ||b-Ax||_2/lambda_min_est in m. Algebraic uncertainty ESTIMATES, NOT certified bounds; no discretization/model-error bound.',
                      refinement='Successive ABSOLUTE observable differences in m, including near-zero midpoint uy. No continuum solution or observed-order claim.',
                      scaling='P=diag(A); S=P^(-1/2) A P^(-1/2); estimated kappa_2=lambda_max/lambda_min for A and S.',
                      jacobi='rho(I-P^-1 A)=max(|1-lambda_min(S)|,|1-lambda_max(S)|). Damped omega=0.5, matching Sections 3 and 4; rho=max(|1-omega*lambda_min(S)|,|1-omega*lambda_max(S)|). Spectral calculation only, not a new iterative benchmark.',
                      perturbations='Proportional delta_f=.001 f; redistribution delta_q_x=C(2y/Ly-1), delta_q_y=0, exact consistent linear-edge integration and C chosen so ||delta_b||_2/||b||_2=.001. Same A. Redistribution adds zero net force but nonzero moment.',
                      change_norm='||x_changed-x||_2/||x||_2 uses the FREE nodal-displacement Euclidean norm, NOT a spatial continuum norm. Amplification divides by ||delta_b||_2/||b||_2. These two directions are not a worst-case sensitivity claim.',
                      superposition='||x_changed-x-delta_x||_2/||delta_x||_2; delta_x is separately solved with the same LU.',
                      roller='Separate n=4 force_driven(support=roller): ux=p*x/E, uy=-nu*p*y/E. Relative full-nodal Euclidean error; not an exact solution for the clamp.'),
                  refinement=rows, diagonal_scaling_n20=scaling, perturbations_n20=perturbations,
                  roller_exact_check=roller_check)
    (data/'evidence.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    with (data/'refinement.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(csv_rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(csv_rows)
    if make_figure:
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7), layout='constrained')
        axes[0].plot([r['n'] for r in rows], [r['observables']['mean_ux']['value_m']*1e3 for r in rows], 'o-')
        axes[0].set(xlabel='cells per side n [1]', ylabel='mean right-edge ux [mm]')
        axes[1].loglog([r['n'] for r in rows], [r['spectrum']['condition_estimate'] for r in rows], 'o-')
        axes[1].set(xlabel='cells per side n [1]', ylabel='estimated condition number [1]')
        axes[1].set_xticks([5, 10, 20, 40], labels=['5', '10', '20', '40'])
        axes[1].xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        for ax in axes:
            ax.grid(alpha=.2)
        (ROOT/'figures').mkdir(exist_ok=True)
        fig.savefig(ROOT/'figures/refinement.pdf')
        plt.close(fig)
    print('PASS: four square refinements, checked eigenpairs, supports/equilibrium, two perturbations, separate roller exact-solution check.', flush=True)
    return result


if __name__ == '__main__':
    run_evidence()
