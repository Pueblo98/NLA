"""Independent numerical checks for the scoped Section 6 evidence."""
import numpy as np
import pytest


def test_linear_edge_load_exact_integrals_and_resultants():
    from generate_evidence import linear_edge_load
    nodes = np.array([[1., 0.], [1., 2.]])
    # q_x(y) = y - 1: endpoint consistent forces are -1/3, +1/3 N.
    q = np.array([[-1., 0.], [1., 0.]])
    f = linear_edge_load(nodes, np.array([[0, 1]]), q).reshape(-1, 2)
    np.testing.assert_allclose(f, [[-1/3, 0.], [1/3, 0.]], atol=1e-15)
    np.testing.assert_allclose(f.sum(axis=0), 0., atol=1e-15)
    moment = np.sum(nodes[:, 0]*f[:, 1] - nodes[:, 1]*f[:, 0])
    assert moment == pytest.approx(-2/3)


@pytest.mark.parametrize('heights', [[0., .1, .4, .8, 1.], np.linspace(0., 1., 6)])
def test_affine_boundary_observables_nonuniform_and_odd_n(heights):
    from generate_evidence import observable_weights
    y = np.array(heights)
    nodes = np.column_stack([np.ones(len(y)), y])
    weights = observable_weights(nodes, np.arange(len(y)))
    d = np.column_stack([2 + 3*y, -1 + 4*y]).ravel()
    assert weights['mean_ux'] @ d == pytest.approx(3.5)
    assert weights['midpoint_ux'] @ d == pytest.approx(3.5)
    assert weights['midpoint_uy'] @ d == pytest.approx(1.)
    # Midpoint lies between nodes in both these meshes, not at the nearest node.
    assert np.count_nonzero(weights['midpoint_ux']) == 2


def test_reactions_do_not_mask_free_residual():
    from generate_evidence import equilibrium
    from scipy.sparse import csr_matrix
    # A two-node horizontal spring, intentionally wrong free displacement.
    K = csr_matrix([[1., 0., -1., 0.], [0., 1., 0., 0.],
                    [-1., 0., 1., 0.], [0., 0., 0., 1.]])
    s = dict(K=K, f=np.array([0., 0., 1., 0.]), free=np.array([2]),
             constrained=np.array([0, 1, 3]), d=np.zeros(4),
             nodes=np.array([[0., 0.], [1., 0.]]))
    d, reaction, checks = equilibrium(s, np.array([.75]))
    np.testing.assert_allclose(reaction, [-.75, 0., 0., 0.])
    assert checks['normalized_force_imbalance'] == pytest.approx(.25)
    assert checks['free_full_residual_norm_N'] == pytest.approx(.25)
    assert checks['force_scale_N'] == 1.


def test_square_evidence_end_to_end(tmp_path):
    from generate_evidence import run_evidence
    from scipy.sparse import csr_matrix
    import json
    result = run_evidence(tmp_path, make_figure=False)
    assert [r['n'] for r in result['refinement']] == [5, 10, 20, 40]
    previous = None
    for row in result['refinement']:
        assert row['unknowns'] == 2*row['n']*(row['n']+1)
        assert row['relative_residual'] < 1e-10
        assert row['relative_symmetry_defect'] < 1e-14
        assert row['spectrum']['lambda_min'] > 0
        assert max(row['spectrum']['relative_eigenpair_defects']) < 1e-7
        assert row['validation']['maximum_support_displacement_m'] == 0
        assert row['validation']['normalized_force_imbalance'] < 1e-10
        assert row['validation']['normalized_moment_imbalance'] < 1e-10
        arrays = np.load(tmp_path/f"square_n{row['n']}.npz")
        A = csr_matrix((arrays['A_data'], arrays['A_indices'], arrays['A_indptr']),
                       shape=tuple(arrays['A_shape']))
        np.testing.assert_allclose(A @ arrays['x'], arrays['b'], atol=1e-7)
        if row['n'] == 5:
            exact = np.linalg.eigvalsh(A.toarray())
            np.testing.assert_allclose([row['spectrum']['lambda_min'], row['spectrum']['lambda_max']],
                                       exact[[0, -1]], rtol=1e-10)
        assert np.all(arrays['reaction_N'][arrays['free']] == 0)
        for key, obs in row['observables'].items():
            w = arrays[f'w_{key}'][arrays['free']]
            expected = np.linalg.norm(w)*np.linalg.norm(arrays['b']-A@arrays['x'])/row['spectrum']['lambda_min']
            assert obs['algebraic_uncertainty_estimate_m'] == pytest.approx(expected)
            if previous is not None:
                difference = abs(obs['value_m']-previous['observables'][key]['value_m'])
                assert obs['successive_absolute_difference_m'] == pytest.approx(difference)
                assert difference > obs['algebraic_uncertainty_estimate_m']
        previous = row
    scaling = result['diagonal_scaling_n20']
    assert scaling['jacobi_spectral_radius'] > 1
    assert scaling['damping_omega'] == .5  # Section 3's actual measured protocol.
    assert scaling['damped_jacobi_spectral_radius'] < 1
    for p in result['perturbations_n20']:
        assert p['relative_rhs_change'] == pytest.approx(.001)
        assert p['superposition_mismatch_relative_to_delta_x'] < 1e-8
        assert p['changed_relative_residual'] < 1e-10
        assert p['increment_relative_residual'] < 1e-10
        assert p['validation']['normalized_force_imbalance'] < 1e-10
        assert p['validation']['normalized_moment_imbalance'] < 1e-10
        if p['name'] == 'proportional':
            assert p['relative_displacement_change'] == pytest.approx(.001, rel=1e-8)
            assert p['amplification'] == pytest.approx(1., rel=1e-8)
        else:
            np.testing.assert_allclose(p['added_force_N'], 0, atol=1e-10)
            assert abs(p['added_moment_Nm']) > 1.
    assert result['roller_exact_check']['relative_nodal_error'] < 1e-11
    assert b'\r' not in (tmp_path/'refinement.csv').read_bytes()
    assert json.loads((tmp_path/'evidence.json').read_text()) == result
    assert (tmp_path/'refinement.csv').is_file()
