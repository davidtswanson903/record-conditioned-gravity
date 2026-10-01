"""Stage 3: the feasibility map, and the closed form underneath it.

R = split / G2, the second peak's resolvability. In the weak-measurement regime
V_all is the ground state's and the best achievable record rate is the
oscillator's own bath, giving

    R = Q wsn^2 / (4 w0^2 (2 nbar + 1)) = Q hbar wsn^2 / (8 w0 kB T)   (classical limit)

Three things fall out of it and are checked against the full filter: R does not
depend on the mass; R improves as 1/w0 at fixed Q; R is bounded by Q/T.
"""
import numpy as np

from rcg import constants as K
from rcg import laws as L
from rcg import platforms as P
from rcg.models import gaussian as G

MATERIAL_NAMES = ("silicon", "gold", "tungsten", "osmium")


def R_closed(w0, Q, T, wsn2):
    nb = G.n_bose(w0, T)
    return float(Q * wsn2 / (4 * w0 ** 2 * (2 * nb + 1)))


class _Platform:
    """A throwaway platform-like object for scanning m/w0/Q/T off the grid, with
    the same fields rcg.laws._common.raw reads."""

    __slots__ = ("m", "w0", "gam", "D_env", "wsn2")

    def __init__(self, m, w0, Q, T, material):
        self.m = m
        self.w0 = w0
        self.gam = w0 / Q
        self.D_env = G.D_thermal(m, self.gam, w0, T)
        self.wsn2 = P.omega_sn_sq(P.MATERIALS[material])


def R_full(m, w0, Q, T, material):
    """The same number out of the full filter, with no approximation."""
    plat = _Platform(m, w0, Q, T, material)
    pred = L.predict("theory", plat, 0.0, 0.0)
    L_tot = (plat.D_env) / K.HBAR ** 2
    return pred.resolvability, dict(
        V_all=pred.V_all, V_unc=pred.V_unc, G2=pred.G2, f=pred.f,
        split=pred.split, L_tot=L_tot,
    )


def best_readout(m, w0, Q, T, material):
    """Sweep the readout strength: too weak and the imprecision floor buries the
    peak, too strong and the readout is itself the record that broadens it."""
    plat = _Platform(m, w0, Q, T, material)
    L_env = plat.D_env / K.HBAR ** 2
    best = None
    for L_ro in np.logspace(np.log10(L_env) - 6, np.log10(L_env) + 4, 61):
        s = L.predict("theory", plat, L_ro, 0.0)
        if s.W <= 0:
            continue
        height = 2 * s.W / s.G2
        vis = height / float(L.spectrum(s, s.w_q))
        rec = dict(L_ro=L_ro, R=s.resolvability, visibility=vis, height=height)
        if best is None or rec["R"] * min(1.0, rec["visibility"]) > \
                best["R"] * min(1.0, best["visibility"]):
            best = rec
    return best


def feasible(m, w0, Q, T, material):
    """All three of stage 3's conditions, plus the geometric gate in front."""
    plat = _Platform(m, w0, Q, T, material)
    b = best_readout(m, w0, Q, T, material)
    if b is None:
        return dict(ok=False, gate=False, R=float("nan"), why="no readout setting")
    th = L.predict("theory", plat, b["L_ro"], 0.0)
    L_anc = plat.D_env / K.HBAR ** 2
    th_on = L.predict("theory", plat, b["L_ro"], L_anc)
    taus = {}
    for law in ("mc_sn", "uncond_sn", "qm"):
        t, _ = L.tau_separate(th, L.predict(law, plat, b["L_ro"], 0.0))
        taus[law] = t
    t_lock, _ = L.tau_separate(th, th_on)
    gate = th.resolvability >= 1.0
    return dict(
        ok=bool(gate and t_lock < K.MONTH and max(taus.values()) < K.MONTH),
        gate=bool(gate), R=th.resolvability, tau_lockin=t_lock, taus=taus,
        L_ro=b["L_ro"], visibility=b["visibility"],
    )


def Q_window(w0, T, material, m=1e-6):
    """The range of Q meeting all three of stage 3's conditions. Scanned, not
    bisected: feasibility is NOT monotone in Q (too little and the second peak is
    a shoulder; too much and a periodogram gathers too few independent samples of
    it per unit time)."""
    ok = [q for q in np.logspace(3, 18, 61) if feasible(m, w0, q, T, material)["ok"]]
    return (min(ok), max(ok)) if ok else (None, None)


def run():
    out = {}

    # 1. the closed form against the full filter, and its validity conditions
    closed_vs_full = {}
    validity = {}
    for key, p in P.PLATFORMS.items():
        Q = p.Q
        rc = R_closed(p.w0, Q, p.T, p.wsn2)
        rf, d = R_full(p.m, p.w0, Q, p.T, p.material.name)
        closed_vs_full[key] = dict(closed=rc, full=rf, ratio=rc / rf)
        x = 4 * p.m * d["L_tot"] * K.HBAR / (p.m * p.w0) ** 2
        validity[key] = dict(weak_measurement_ratio=x,
                              small_shift_ratio=float(np.sqrt(p.wsn2)) / p.w0)
    out["closed_vs_full"] = closed_vs_full
    out["closed_form_validity"] = validity

    # 2. mass independence
    w0, Q, T = 2 * np.pi * 10.0, 1e10, 0.1
    rs = []
    for m in np.logspace(-18, -4, 8):
        r, _ = R_full(m, w0, Q, T, "osmium")
        rs.append(r)
    out["mass_independence"] = dict(
        masses=list(np.logspace(-18, -4, 8)), R=rs,
        spread=float((max(rs) - min(rs)) / max(rs)),
    )

    # 3. Q/T targets by material
    qt = {}
    for mat in MATERIAL_NAMES:
        wsn2 = P.omega_sn_sq(P.MATERIALS[mat])
        qt[mat] = dict(
            w_sn=float(np.sqrt(wsn2)),
            QT_10Hz=8 * (2 * np.pi * 10.0) * K.KB / (K.HBAR * wsn2),
            QT_1mHz=8 * (2 * np.pi * 1e-3) * K.KB / (K.HBAR * wsn2),
        )
    out["QT"] = qt

    # 4. the map: R over frequency and temperature, at three Q (osmium)
    wsn2_os = P.omega_sn_sq(P.MATERIALS["osmium"])
    gmap = {}
    for Q in (1e8, 1e10, 1e12):
        row = {}
        for T in (1e-3, 1e-2, 1e-1, 1.0, 300.0):
            vals = [R_closed(2 * np.pi * fz, Q, T, wsn2_os) for fz in (1e-3, 1e-2, 1.0, 10.0)]
            row[str(T)] = vals
        gmap[f"Q{Q:.0e}"] = row
    out["map"] = gmap

    # 5. the corner, and the Q window at several frequencies/temperatures
    corner = dict(m=1e-6, w0=2 * np.pi * 1e-3, Q=1e12, T=1e-3, material="osmium")
    fz = feasible(**corner)
    out["corner"] = dict(
        R=fz["R"], gate=fz["gate"], ok=fz["ok"],
        tau_lockin=(None if not np.isfinite(fz["tau_lockin"]) else fz["tau_lockin"]),
        taus={k: (None if not np.isfinite(v) else v) for k, v in fz["taus"].items()},
    )

    boundary = {}
    for fz_ in (1e-4, 1e-3, 1e-2, 1e-1, 1.0):
        row = []
        for T_ in (1e-3, 1e-2, 1e-1, 1.0):
            a, b = Q_window(2 * np.pi * fz_, T_, "osmium")
            row.append([a, b])
        boundary[f"{fz_:g}Hz"] = row
    out["boundary"] = boundary

    # 6. the three platforms through the same gate
    plats = {}
    for key, p in P.PLATFORMS.items():
        fz = feasible(p.m, p.w0, p.Q, p.T, p.material.name)
        plats[key] = dict(R=fz["R"], gate=bool(fz["gate"]), ok=bool(fz["ok"]))
    out["platforms_gate"] = plats

    # 7. the crystal regime: alpha for V_all and for V_unc
    alpha = {}
    for key, p in P.PLATFORMS.items():
        _, d = R_full(p.m, p.w0, p.Q, p.T, p.material.name)
        sig = p.material.sigma_m
        al_all = float(np.sqrt(2) * sig / np.sqrt(d["V_all"]))
        al_unc = float(np.sqrt(2) * sig / np.sqrt(d["V_unc"]))
        alpha[key] = dict(
            sqrtV_all=float(np.sqrt(d["V_all"])), alpha_all=al_all,
            sqrtV_unc=float(np.sqrt(d["V_unc"])), alpha_unc=al_unc,
            regime=("narrow" if al_all > 10 else
                    ("intermediate" if al_all > 1 else "wide (formula fails)")),
        )
    out["alpha"] = alpha
    return out
