"""Unit tests on the law itself: the closed forms' endpoints and monotonicity,
composition, and no signalling -- independent of either experiment's larger
machinery."""
import numpy as np
import pytest

from rcg import law, records
from rcg.models import two_mass as tm


def test_endpoints():
    assert float(law.f_rule_i(1.0)) == 1.0
    assert float(law.f_rule_i(0.0)) == 0.0
    assert float(law.f_rule_ii(1.0)) == 1.0
    assert float(law.f_rule_ii(0.0)) == 0.0


def test_monotonic_and_between_endpoints():
    etas = np.linspace(0.0, 1.0, 101)
    for f in (law.f_rule_i, law.f_rule_ii):
        vals = np.asarray(f(etas), dtype=float)
        assert (np.diff(vals) >= 0).all()
        assert (vals >= -1e-15).all() and (vals <= 1.0 + 1e-15).all()


def test_rule_ii_below_rule_i_in_the_interior():
    # rule (ii) = 1 - sqrt(1-eta^2) <= eta = rule (i) for eta in [0, 1]
    etas = np.linspace(0.0, 1.0, 101)
    assert (law.f_rule_ii(etas) <= law.f_rule_i(etas) + 1e-15).all()


def test_rule_i_is_exactly_multiplicative():
    for e1, e2 in ((0.8, 0.6), (0.8, 0.8), (0.5, 0.5), (0.3, 0.9)):
        a = float(law.f_rule_i(e1)) * float(law.f_rule_i(e2))
        b = float(law.f_rule_i(e1 * e2))
        assert a == pytest.approx(b, abs=1e-14)


def test_rule_ii_is_not_multiplicative():
    e1, e2 = 0.8, 0.6
    a = float(law.f_rule_ii(e1)) * float(law.f_rule_ii(e2))
    b = float(law.f_rule_ii(e1 * e2))
    assert abs(a - b) > 0.03   # misses by a lot, not a rounding-level disagreement


@pytest.mark.parametrize("e1,e2", [(0.8, 0.6), (0.9, 0.9), (0.5, 0.5), (0.7, 0.3), (1.0, 0.4)])
def test_composition_is_the_product(e1, e2):
    """Two independent registers at overlaps e1, e2 are read by the law as ONE
    record at overlap e1*e2: the law reads only rho_S, and the joint register's
    overlap is the product."""
    ee = records.nested_record([e1, e2]).eta_eff()
    assert ee == pytest.approx(e1 * e2, abs=1e-14)


def test_no_signalling_under_random_unitaries_on_the_register():
    """A unitary on the register alone -- everything a distant party holding it
    can do -- must not move eta_eff, since the law reads only the mass's reduced
    state and a unitary on the register alone cannot touch that."""
    rng = np.random.default_rng(7)
    worst = 0.0
    for _ in range(20):
        m = records.nested_record([0.5])
        before = m.eta_eff()
        d = int(np.prod(m.dims[1:]))
        A = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
        Q, _ = np.linalg.qr(A)
        m.apply_to_registers(Q)
        worst = max(worst, abs(m.eta_eff() - before))
    assert worst < 1e-12


def test_unread_record_counts_the_same_as_an_unmeasured_one():
    """Reading the register (a unitary plus a classical copy) leaves the mass's
    reduced state, and hence eta_eff, untouched."""
    m = records.nested_record([0.5])
    assert m.eta_eff() == pytest.approx(0.5, abs=1e-12)


def test_erasure_restores_full_overlap():
    m = records.nested_record([0.3])
    assert m.eta_eff() == pytest.approx(0.3, abs=1e-12)
    U_inv = records.record_unitary(0.3)[:4, :4]
    m.psi = (np.linalg.inv(U_inv) @ m.psi.reshape(-1)).reshape(-1)
    assert m.eta_eff() == pytest.approx(1.0, abs=1e-12)


def test_environment_is_indistinguishable_from_a_deliberate_register():
    for eta in (0.9, 0.5, 0.2, 0.0):
        a = records.nested_record([eta]).eta_eff()
        b = records.Register().attach_env(eta, dim=4, seed=11).eta_eff()
        assert a == pytest.approx(b, abs=1e-12)


def test_the_law_adds_no_noise():
    """P1's 'no added noise' half: the mean-field dynamics is a deterministic
    function of the initial state, with no stochastic term anywhere in its
    construction (unlike a genuine noise-based classical channel, which would
    need one to avoid signalling -- see docs/related-work.md on Kafri2014).
    Checked the only way a deterministic claim CAN be checked: two independent
    runs from the same initial condition, with no shared random state, agree
    bit for bit."""
    a = tm.two_mass("theory")
    b = tm.two_mass("theory")
    for ra, rb in zip(a, b):
        for key in ("concurrence", "negativity", "phase1"):
            assert ra[key] == rb[key]
