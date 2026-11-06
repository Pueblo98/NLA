"""Synthetic CSR handoff check; run after check_system_tools.py."""
import numpy as np
from scipy.sparse import csr_matrix, issparse
from scipy.sparse.linalg import spsolve
from system_tools import reduce_system

# Three coupled DOFs, unsorted constraints and nonzero prescribed motion.
# The exact displacement and support reactions are specified independently.
K = csr_matrix([[4., -1., -1.], [-1., 4., -2.], [-1., -2., 3.]])
f = np.array([5., 3., -2.])
K_before = K.copy()
f_before = f.copy()
A, b, free, d = reduce_system(K, f, [2, 0], [-.5, 1.])
assert issparse(A), "reduction unexpectedly densified K"
np.testing.assert_array_equal(free, [1])
np.testing.assert_allclose(b, [3.])
d[free] = spsolve(A, b)
np.testing.assert_allclose(d, [1., .75, -.5])
np.testing.assert_allclose(K @ d - f, [-1.25, 0., -2.])
np.testing.assert_array_equal(K.toarray(), K_before.toarray())
np.testing.assert_array_equal(f, f_before)

# Sparse and dense reduction must agree, including returned index ordering.
Ad, bd, fd, dd = reduce_system(K.toarray(), f, [2, 0], [-.5, 1.])
np.testing.assert_allclose(A.toarray(), Ad)
np.testing.assert_allclose(b, bd)
np.testing.assert_array_equal(free, fd)
np.testing.assert_allclose(d[[2, 0]], dd[[2, 0]])
print("PASS: CSR reduction, sparse solve, reactions, unchanged inputs, dense agreement")
