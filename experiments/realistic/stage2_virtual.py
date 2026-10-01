"""Stage 2: the virtual experiment -- the whole protocol, under five laws, with
two observables (the raw PSD fails its own control; the second peak's
weight is heating-nulled and passes), and the controls the experiment required.
"""
import numpy as np

from rcg import constants as K
from rcg import laws as L
from rcg import platforms as P
from rcg.laws import collapse as collapse_law
from rcg.models import gaussian as G

ETA_DET = 0.8   # readout efficiency, ASSUMED; swept in stage 3


def _measurement_crossover(p, L_ro):
    """4 m Lambda_tot hbar against (m w0)^2, at the baseline setting (readout
    only, no ancilla) -- the ratio that decides which side of the crossover an
    added record's effect on the second peak's weight falls on."""
    D = p.D_env + K.HBAR ** 2 * L_ro
    L_tot = D / K.HBAR ** 2
    return 4 * p.m * L_tot * K.HBAR, (p.m * p.w0) ** 2


def run():
    out = {"eta_det": ETA_DET, "platforms": {}}

    for key, p in P.PLATFORMS.items():
        L_env = p.D_env / K.HBAR ** 2
        L_ro, L_anc = 1e-3 * L_env, L_env
        off = {law: L.predict(law, p, L_ro, 0.0) for law in L.LAWS}
        on = {law: L.predict(law, p, L_ro, L_anc) for law in L.LAWS}
        st = off["theory"]

        laws_block = {
            law: dict(w_main=s.w_main, W=s.W, G2=s.G2,
                      resolvability=(None if s.W <= 0 else s.resolvability))
            for law, s in off.items()
        }

        lockin = {}
        w_q = st.w_q
        for law in L.LAWS:
            s0, s1 = off[law], on[law]
            S0, S1 = float(L.spectrum(s0, w_q)), float(L.spectrum(s1, w_q))
            lockin[law] = dict(raw_off=S0, raw_on=S1, raw_frac=abs(S1 - S0) / S0,
                                W_off=s0.W, W_on=s1.W)

        sep = {}
        for law in L.LAWS:
            if law == "theory":
                continue
            t, integ = L.tau_separate(off["theory"], off[law])
            sep[law] = dict(integral=integ, tau=(None if not np.isfinite(t) else t))

        D_csl = collapse_law.D_csl(p.m)
        csl_bound = collapse_law.csl_lambda_bound(p.m, p.D_env)
        lhs, rhs = _measurement_crossover(p, L_ro)

        out["platforms"][key] = dict(
            nbar=G.n_bose(p.w0, p.T), purity=st.purity, eta_eff=st.eta_eff, f=st.f,
            w0=p.w0, w_sn=float(np.sqrt(p.wsn2)), split=st.split, L_env=L_env,
            laws=laws_block, lockin=lockin, sep=sep,
            csl_relative_to_env=D_csl / p.D_env, csl_lambda_bound=csl_bound,
            theory_W_off=off["theory"].W, theory_W_on=on["theory"].W,
            mc_sn_W_off=off["mc_sn"].W, mc_sn_W_on=on["mc_sn"].W,
            measurement_crossover_lhs=lhs, measurement_crossover_rhs=rhs,
        )

    # ---------------------------------------------------------------- controls
    p = P.PLATFORMS["osmium-paul"]
    L_env = p.D_env / K.HBAR ** 2
    L_ro = 1e-3 * L_env
    a_vals, b_vals = [], []
    for la in (1e-3, 1.0, 1e3):
        s0 = L.predict("qm", p, L_ro, 0.0)
        s1 = L.predict("qm", p, L_ro, la * L_env)
        wq = s0.w_q
        a = abs(float(L.spectrum(s1, wq)) - float(L.spectrum(s0, wq))) / float(L.spectrum(s0, wq))
        b = abs(s1.W - s0.W)
        a_vals.append(a)
        b_vals.append(b)

    u0 = L.predict("uncond_sn", p, L_ro, 0.0)
    u1 = L.predict("uncond_sn", p, L_ro, L_env)
    d2 = abs(u1.w_main - u0.w_main) / u0.w_main

    d3 = {}
    for law in L.LAWS:
        s0 = L.predict(law, p, L_ro, 0.0)
        s1 = L.predict(law, p, L_ro, 0.0)
        d3[law] = abs(float(L.spectrum(s1, s0.w_q)) - float(L.spectrum(s0, s0.w_q)))

    offs = {law: L.predict(law, p, L_ro, 0.0) for law in L.LAWS}
    vals = [float(L.spectrum(s, offs["theory"].w_q)) for s in offs.values()]
    spread = (max(vals) - min(vals)) / max(vals)

    out["controls"] = dict(
        qm_lockin_raw=float(max(a_vals)), qm_lockin_weight=float(max(b_vals)),
        uncond_sn_ancilla=float(d2), no_record_no_modulation=float(max(d3.values())),
        law_spread=float(spread),
        passes_on_observable_B=bool(max(b_vals) == 0.0 and d2 < 1e-12
                                     and max(d3.values()) == 0.0),
        passes_on_observable_A=bool(max(a_vals) < 1e-12),
    )
    return out
