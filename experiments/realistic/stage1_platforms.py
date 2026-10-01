"""Stage 1: the three platforms, and what the adapter reads off each before
anything is switched -- the baseline that decides the experiment.
"""
import numpy as np

from rcg import constants as K
from rcg import law, platforms as P
from rcg.models import gaussian as G


def readings(p, Lambda_ro=0.0, Lambda_anc=0.0, eta_det=0.8, rule="i"):
    m, w0, gam = p.m, p.w0, p.gam
    D = p.D_env + K.HBAR ** 2 * (Lambda_ro + Lambda_anc)
    L_tot = G.Lambda_from_D(D)
    V_unc = G.cov_steady(m, w0, gam, D, 0.0)
    V_all = G.cov_steady(m, w0, gam, D, L_tot)
    V_det = G.cov_steady(m, w0, gam, D, eta_det * Lambda_ro)
    eta = G.eta_eff(V_unc)
    f = float(law.RULES[rule](eta))
    wsn2 = p.wsn2
    w_q = float(np.sqrt(w0 ** 2 + wsn2))
    w_c = float(np.sqrt(w0 ** 2 + f * wsn2))
    split = float((1.0 - f) * wsn2 / (w_q + w_c))
    return dict(
        V_unc=V_unc[0], V_all=V_all[0], V_det=V_det[0],
        purity_unc=G.purity(V_unc), eta_eff=eta, f=f,
        nbar=G.n_bose(w0, p.T), w_q=w_q, split_theory=split,
        G_theory=G.linewidth_q(gam, L_tot, V_all[0]),
    )


def run():
    out = {}

    # 0. the material constant, against its own formula
    mat_check = {}
    for mat in ("silicon", "tungsten", "osmium", "gold"):
        m = P.MATERIALS[mat]
        formula = law.dwsn_times_w0_formula(m.atomic_mass_u, m.sigma_m)
        mat_check[mat] = dict(
            table=m.dwsn_times_w0, formula=formula,
            error=abs(formula - m.dwsn_times_w0) / m.dwsn_times_w0,
            wsn=float(np.sqrt(P.omega_sn_sq(m))),
        )
    out["material_constant_check"] = mat_check

    # 1. the platforms, as loaded
    plats = {}
    for key, p in P.PLATFORMS.items():
        plats[key] = dict(
            m=p.m, radius_m=p.radius_m, w0=p.w0, T=p.T, gam=p.gam, Q=p.Q,
            D_env=p.D_env, Lambda_env=G.Lambda_from_D(p.D_env), notes=p.notes,
            material=p.material.name, citation=p.citation,
        )
    out["platforms"] = plats

    # 2. the baseline reading, before readout or ancilla
    baseline = {}
    for key, p in P.PLATFORMS.items():
        r = readings(p)
        baseline[key] = r
    out["baseline"] = baseline
    res = {k: baseline[k]["split_theory"] / baseline[k]["G_theory"] for k in baseline}
    out["resolvability_orders"] = sorted(
        int(round(-np.log10(abs(v)))) for v in res.values()
    )
    out["resolvability"] = res
    return out
