"""Stage 0: the adapter, from two branches to a real oscillator, checked against
the idealized law.

Three things are checked here, numerically: eta_eff recovers the two-branch
overlap exactly; the adapter's f reduces to the law's own f exactly; and the
Gaussian filter reproduces both of its required limits (equipartition, and the
ground state). See rcg.models.gaussian's module docstring for the derivation.
"""
import numpy as np

from rcg import constants as K
from rcg import law
from rcg.models import gaussian as G


def two_branch_rho(eta):
    return 0.5 * np.array([[1.0, eta], [eta, 1.0]])


def run():
    out = {}

    # 1. eta_eff recovers the two-branch overlap
    rows = []
    worst = 0.0
    for eta in (1.0, 0.9, 0.7, 0.5, 0.3, 0.1, 0.0):
        rho = two_branch_rho(eta)
        tr2 = float(np.trace(rho @ rho))
        rec = float(np.sqrt(max(0.0, 2 * tr2 - 1)))
        worst = max(worst, abs(rec - eta))
        rows.append(dict(eta=eta, tr_rho2=tr2, eta_eff=rec, error=abs(rec - eta)))
    out["eta_eff_check"] = dict(rows=rows, worst=worst)

    # 2. the adapter's f reduces to the law's f
    rows2 = []
    worst2 = 0.0
    for eta in (1.0, 0.8, 0.5, 0.2, 0.0):
        rho = two_branch_rho(eta)
        e = float(np.sqrt(max(0.0, 2 * float(np.trace(rho @ rho)) - 1)))
        a_i, a_ii = float(law.f_rule_i(e)), float(law.f_rule_ii(e))
        t_i, t_ii = float(law.f_rule_i(eta)), float(law.f_rule_ii(eta))
        worst2 = max(worst2, abs(a_i - t_i), abs(a_ii - t_ii))
        rows2.append(dict(eta=eta, f_i_direct=t_i, f_i_adapter=a_i,
                           f_ii_direct=t_ii, f_ii_adapter=a_ii))
    out["f_reduction_check"] = dict(rows=rows2, worst=worst2)

    # 3. the three limits, and the second-peak width surprise
    m, w0, Q, T = 1e-14, 2 * np.pi * 10.0, 1e10, 0.1
    gam = w0 / Q
    D = m * gam * K.KB * T
    conditionings = {}
    for name, mu in (
        ("none", 0.0),
        ("readout_eta0.8", 0.8 * 1e-3 * D / K.HBAR ** 2),
        ("every_record", D / K.HBAR ** 2),
    ):
        V = G.cov_steady(m, w0, gam, D, mu)
        r = max(G.residual(m, w0, gam, D, mu, V))
        sc = max(abs(2 * V[1] / m), abs(V[2] / m), abs(2 * D))
        conditionings[name] = dict(Vx=V[0], purity=G.purity(V), residual=r / sc)
    V0 = G.cov_steady(m, w0, gam, D, 0.0)
    Va = G.cov_steady(m, w0, gam, D, D / K.HBAR ** 2)
    nbar_test = K.KB * T / (K.HBAR * w0)
    mu_t = D / K.HBAR ** 2
    lw = G.linewidth_q(gam, mu_t, Va[0])
    jr = G.jacobian_rates(m, w0, gam, mu_t, Va)
    out["filter_check"] = dict(
        m=m, w0=w0, Q=Q, T=T,
        conditionings=conditionings,
        equipartition=K.KB * T / (m * w0 ** 2), V_unconditional=V0[0],
        ground_state=K.HBAR / (2 * m * w0), V_conditioned=Va[0],
        purity_formula=1.0 / (2 * nbar_test + 1), purity_filter=float(G.purity(V0)),
        linewidth_closed=lw, jacobian_rates=list(jr),
    )
    return out
