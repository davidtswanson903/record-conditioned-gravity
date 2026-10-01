"""Stage 4: three challenges to the realistic-conditions result, each run rather
than argued.

(1) the adapter's f=0-on-a-thermal-oscillator extrapolation, read a second way
    (coherence at the lattice scale, rather than through the purity);
(2) whether unconditional Schroedinger-Newton is actually excluded by experiment
    (a claim withdrawn here -- see [Y25] in data/references.yaml);
(3) whether the record-broadening wall transfers to the measurement-conditioned
    proposals (it does not; a weaker, field-wide bound does, checked against
    [Y25]'s own reported run time).
"""
import numpy as np

from rcg import constants as K
from rcg import law as _law
from rcg import laws as L
from rcg import platforms as P
from rcg.laws import collapse as collapse_law
from rcg.models import gaussian as G


def scan_readout(p, law, n=229):
    """An absolute range, not one anchored on the platform's own environment
    rate: the readout a platform needs can sit twenty orders below it."""
    rows = []
    for L_ro in np.logspace(-6.0, 50.0, n):
        s = L.predict(law, p, L_ro, 0.0)
        if s.W <= 0:
            continue
        height = 2 * s.W / s.G2
        total = float(L.spectrum(s, s.w_q))
        rows.append(dict(G2=s.G2, W=s.W, R=s.resolvability, visibility=height / total,
                          L_ro=L_ro, tau_form=2 * np.pi / s.G2))
    return rows


def best_resolvable(p, law):
    """The largest resolvability reachable with the peak still at half
    visibility, and -- when nothing clears that -- the best visibility the
    readout can buy, so the caller can say which obstacle bit."""
    rows = scan_readout(p, law)
    ok = [r for r in rows if r["visibility"] >= 0.5]
    if ok:
        return max(ok, key=lambda r: r["R"])
    best = max(rows, key=lambda r: r["visibility"]) if rows else None
    if best is not None:
        best = dict(best, failed=True)
    return best


def run():
    out = {}

    # ---------------------------------------------------------------- (1)
    second_reading = {}
    for key, p in P.PLATFORMS.items():
        V = G.cov_steady(p.m, p.w0, p.gam, p.D_env, 0.0)
        sig = p.material.sigma_m
        lt = G.thermal_length(p.m, p.T)
        lc = G.coherence_length(V)
        ec = G.coherence(V, sig)
        f_pur = float(L.predict("theory", p, 0.0, 0.0).f)
        f_coh = float(_law.RULES["i"](ec))
        second_reading[key] = dict(
            thermal_length=lt, coherence_length=lc, sigma=sig, eta_coh=ec,
            neg_log_eta=0.5 * (sig / lc) ** 2,
            f_purity=f_pur, f_coherence=f_coh,
            agree=bool((f_pur < 1e-6) == (f_coh < 1e-6)),
        )
    out["second_reading"] = second_reading

    # ---------------------------------------------------------------- (3)
    walls = {}
    for key, p in P.PLATFORMS.items():
        L_env = p.D_env / K.HBAR ** 2
        nb = G.n_bose(p.w0, p.T)
        walls[key] = {}
        for law in ("theory", "mc_sn"):
            b = best_resolvable(p, law)
            cap = p.Q * p.wsn2 / (4 * p.w0 ** 2 * ((2 * nb + 1) if law == "theory" else 1.0))
            if b is None:
                walls[key][law] = None
            elif b.get("failed"):
                walls[key][law] = dict(R=b["R"], closed_cap=float(cap),
                                        visibility=b["visibility"], cleared=False)
            else:
                walls[key][law] = dict(R=b["R"], L_ro_over_Lenv=b["L_ro"] / L_env,
                                        closed_cap=float(cap), cleared=True,
                                        tau_form=b["tau_form"])
    out["walls"] = walls
    out["thermal_occupation_factor"] = {
        key: 2 * G.n_bose(p.w0, p.T) + 1 for key, p in P.PLATFORMS.items()
    }

    tmin = {}
    for key, p in P.PLATFORMS.items():
        t = np.pi * p.Q / p.w0
        tmin[key] = dict(Q=p.Q, f0=p.w0 / (2 * np.pi), t_min_days=float(t / K.DAY))
    y25_Q, y25_w0 = 5e4, 2 * np.pi * 0.6e-3
    tmin["Y25_torsion_balance"] = dict(
        Q=y25_Q, f0=y25_w0 / (2 * np.pi),
        t_min_days=float(np.pi * y25_Q / y25_w0 / K.DAY),
    )
    out["tmin"] = tmin

    # --------------------------------------------- CSL bound, reported alongside
    csl = {}
    for key, p in P.PLATFORMS.items():
        csl[key] = dict(
            D_csl_over_D_env=collapse_law.D_csl(p.m) / p.D_env,
            lambda_bound=collapse_law.csl_lambda_bound(p.m, p.D_env),
        )
    out["csl"] = csl
    return out
