"""The computational check: T1-T9, with the controls that prove the code can
tell the laws apart.

Computes every number the original experiment produced and writes results/check.json.
The prose that interprets these numbers lives in docs-src/tests.md.njk, filled in by
`make docs`; this script's job is only the arithmetic.
"""
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from rcg import law, records                       # noqa: E402
from rcg.models import branches as mb, two_mass as tm  # noqa: E402

ETAS = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
RESULTS_DIR = ROOT / "results"

# The pilot's own stored targets (lib/representations/self_gravity_records_settings.py
# in the theory's source repository; see PROVENANCE.md), at its own resolution
# (nx=2048) rather than the sweeps' nx=512. Calibrating against these, before
# anything else is built on the law, is stage 0 of the original check.
PILOT = dict(nx=2048, lx=200.0, d=20.0, sigma=3.0, g=0.5, rs=1.0, dt=0.02, t_final=30.0)
PILOT_TARGET_I = {1.0: 0.3402, 0.8: 0.2671, 0.5: 0.1633, 0.2: 0.0643, 0.0: -0.0000}
PILOT_TARGET_II = {1.0: 0.3402, 0.8: 0.1299, 0.5: 0.0429, 0.2: 0.0064, 0.0: -0.0000}


def pilot_calibration():
    """Regenerate the pilot's own numbers from the pilot's own model, before
    anything else is built on the law. The model is rcg.models.branches.Branches
    at the pilot's own grid resolution, not the sweeps' smaller one."""
    B = mb.Branches(PILOT)
    rows = []
    worst = 0.0
    for e in sorted(PILOT_TARGET_I, reverse=True):
        di = B.run("rule_i", e)["drift"]
        dii = B.run("rule_ii", e)["drift"]
        worst = max(worst, abs(di - PILOT_TARGET_I[e]), abs(dii - PILOT_TARGET_II[e]))
        rows.append(dict(eta=e, rule_i=di, target_i=PILOT_TARGET_I[e],
                          rule_ii=dii, target_ii=PILOT_TARGET_II[e]))
    return dict(rows=rows, worst=worst)


def outcome_sourced_drift(B, basis):
    """The measurement-conditioned law: source by the state conditioned on the
    OUTCOME. With a perfect record, a z-basis outcome is a definite branch and an
    x-basis outcome is a superposition."""
    if basis == "z":
        return B.run("collapse", 0.0)["drift"]
    return B.run("sn", 1.0)["drift"]


def main():
    OUT = {}
    OUT["pilot_calibration"] = pilot_calibration()
    print(f"pilot calibration: worst difference {OUT['pilot_calibration']['worst']:.2e} "
          f"(nx={PILOT['nx']})")
    B = mb.Branches()
    print(f"the grid model runs at nx = {mb.GRID['nx']} for the sweeps")

    # ---------------------------------------------------------------- T1
    sn = B.run("sn", 1.0)["drift"]
    r1_i, r1_ii = B.run("rule_i", 1.0)["drift"], B.run("rule_ii", 1.0)["drift"]
    r0_i, r0_ii = B.run("rule_i", 0.0)["drift"], B.run("rule_ii", 0.0)["drift"]
    coll = B.run("collapse", 1.0)["drift"]
    OUT["T1"] = dict(sn=sn, rule_i_1=r1_i, rule_ii_1=r1_ii, rule_i_0=r0_i,
                      rule_ii_0=r0_ii, collapse=coll)
    print(f"T1  no record: rule(i)={r1_i:+.6f} rule(ii)={r1_ii:+.6f} sn={sn:+.6f}"
          f"   perfect record: rule(i)={r0_i:+.6f} rule(ii)={r0_ii:+.6f}")

    # ---------------------------------------------------------------- T2
    curve = []
    for e in ETAS:
        di, dii = B.run("rule_i", e)["drift"], B.run("rule_ii", e)["drift"]
        curve.append(dict(eta=e, f_i=float(law.f_rule_i(e)), drift_i=di,
                           f_ii=float(law.f_rule_ii(e)), drift_ii=dii))
    mi = np.diff([c["drift_i"] for c in curve])
    mii = np.diff([c["drift_ii"] for c in curve])
    OUT["T2"] = curve
    print(f"T2  monotonic: rule(i) {(mi < 0).all()}  rule(ii) {(mii < 0).all()}"
          f"   largest step {max(abs(mi).max(), abs(mii).max()):.4f}")

    # ---------------------------------------------------------------- T3
    comp = []
    for e1, e2 in ((0.8, 0.6), (0.9, 0.9), (0.5, 0.5), (0.7, 0.3), (1.0, 0.4)):
        ee = records.nested_record([e1, e2]).eta_eff()
        comp.append(dict(eta1=e1, eta2=e2, product=e1 * e2, eta_eff=ee))
    mult = []
    for nm, f in (("i", law.f_rule_i), ("ii", law.f_rule_ii)):
        for e1, e2 in ((0.8, 0.6), (0.8, 0.8), (0.5, 0.5)):
            a, b = float(f(e1)) * float(f(e2)), float(f(e1 * e2))
            mult.append(dict(rule=nm, eta1=e1, eta2=e2, prod=a, joint=b))
    OUT["T3"] = dict(overlap=comp, multiplicative=mult)
    worst3 = max(abs(c["eta_eff"] - c["product"]) for c in comp)
    print(f"T3  composition exact to {worst3:.1e}")

    # ---------------------------------------------------------------- T4
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
    worst4 = 0.0
    for trial in range(20):
        m = records.Register().attach_env(0.5, dim=4, seed=trial)
        before = m.eta_eff()
        A = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
        Q, _ = np.linalg.qr(A)
        m.apply_to_registers(Q)
        worst4 = max(worst4, abs(m.eta_eff() - before))
    dz, dx = outcome_sourced_drift(B, "z"), outcome_sourced_drift(B, "x")
    OUT["T4"] = dict(
        worst_2d=worst, worst_4d=worst4, outcome_z=dz, outcome_x=dx,
        theory_i=B.run("rule_i", 0.0)["drift"], theory_ii=B.run("rule_ii", 0.0)["drift"],
    )
    print(f"T4  no signalling: 2d {worst:.2e}  4d {worst4:.2e}  outcome-sourced signals by "
          f"{abs(dx - dz):.4f}")

    # ---------------------------------------------------------------- T5
    m_unread = records.nested_record([0.5])
    eta_unread = m_unread.eta_eff()
    OUT["T5"] = dict(eta_unread=eta_unread, pull=B.run("rule_i", 0.5)["drift"])
    print(f"T5  unread eta_eff = {eta_unread:.12f}")

    # ---------------------------------------------------------------- T6
    m_er = records.nested_record([0.3])
    eta_before = m_er.eta_eff()
    U_inv = records.record_unitary(0.3)[:4, :4]
    psi = m_er.psi.copy()
    m_er.psi = (np.linalg.inv(U_inv) @ psi.reshape(-1)).reshape(-1)
    eta_after = m_er.eta_eff()
    steps = int(mb.GRID["t_final"] / mb.GRID["dt"])

    def write_then_erase(s):
        return 0.3 if s < steps // 2 else 1.0

    d_er = B.run("rule_i", 0.3, record=write_then_erase)["drift"]
    d_held = B.run("rule_i", 0.3)["drift"]
    d_none = B.run("rule_i", 1.0)["drift"]
    OUT["T6"] = dict(eta_before=eta_before, eta_after=eta_after, drift_erased=d_er,
                      drift_held=d_held, drift_none=d_none)
    print(f"T6  erasure: eta {eta_before:.6f} -> {eta_after:.6f}   drift {d_er:+.6f} between "
          f"{d_held:+.6f} and {d_none:+.6f}")

    # ---------------------------------------------------------------- T7
    t7 = []
    for e in (0.9, 0.5, 0.2, 0.0):
        a = records.nested_record([e]).eta_eff()
        b = records.Register().attach_env(e, dim=4, seed=11).eta_eff()
        t7.append(dict(eta=e, register=a, environment=b))
    OUT["T7"] = t7
    print(f"T7  register vs environment, worst difference "
          f"{max(abs(r['register'] - r['environment']) for r in t7):.1e}")

    # ---------------------------------------------------------------- T8
    th = tm.two_mass("theory")
    qu = tm.two_mass("quantized")
    OUT["T8"] = dict(theory=th, quantized=qu)
    print(f"T8  theory negativity max {max(a['negativity'] for a in th):.1e}   "
          f"quantized concurrence max {max(b['concurrence'] for b in qu):.3f}")

    # ---------------------------------------------------------------- T9
    t9 = []
    for nm in ("rule_i", "rule_ii"):
        for e in (1.0, 0.5, 0.0):
            r = B.run(nm, e)
            a, b = B.weights(nm, e)
            rel = abs(r["energy1"] - r["energy0"]) / max(abs(r["energy0"]), 1e-30)
            c4 = dict(mb.GRID)
            c4["dt"] = mb.GRID["dt"] / 4
            r4 = mb.Branches(c4).run(nm, e)
            rel4 = abs(r4["energy1"] - r4["energy0"]) / max(abs(r4["energy0"]), 1e-30)
            t9.append(dict(rule=nm, eta=e, alpha=a, beta=b, e0=r["energy0"], e1=r["energy1"],
                            rel=rel, rel_quarter=rel4))
    half = steps // 2  # noqa: F841 (parity with the original script's local)
    r_a = B.run("rule_i", 0.3, t_final=mb.GRID["t_final"] / 2)
    r_b = B.run("rule_i", 1.0, t_final=mb.GRID["t_final"] / 2)
    r_er = B.run("rule_i", 0.3, record=write_then_erase)
    OUT["T9_limit"] = dict(
        within_recorded=abs(r_a["energy1"] - r_a["energy0"]) / abs(r_a["energy0"]),
        within_none=abs(r_b["energy1"] - r_b["energy0"]) / abs(r_b["energy0"]),
        across_erasure=abs(r_er["energy1"] - r_er["energy0"]) / abs(r_er["energy0"]),
    )
    OUT["T9"] = t9
    print(f"T9  worst drift {max(t['rel'] for t in t9):.1e}, divides by "
          f"{np.mean([t['rel'] / t['rel_quarter'] for t in t9]):.2f} at dt/4")

    # ------------------------------------------------------------ controls
    sn_etas = [B.run("sn", e)["drift"] for e in (1.0, 0.5, 0.0)]
    OUT["controls"] = dict(
        sn_flat=sn_etas,
        quantized_max=max(b["concurrence"] for b in qu),
        outcome_spread=abs(dx - dz),
    )
    print(f"controls  sn spread {max(sn_etas) - min(sn_etas):.1e}   "
          f"quantized max concurrence {max(b['concurrence'] for b in qu):.3f}   "
          f"outcome spread {abs(dx - dz):.4f}")

    # -------------------------------------------------- the discriminators
    SCEN = (
        ("record held, unread, eta = 0.5", 0.5, False),
        ("the same record, coherently erased", 0.5, True),
        ("a 4-dim environment, no register, eta = 0.5", 0.5, False),
    )
    disc = []
    for name, e, erased in SCEN:
        eff = 1.0 if erased else e
        ti = B.run("rule_i", eff)["drift"] / r1_i
        tii = B.run("rule_ii", eff)["drift"] / r1_i
        s_n = B.run("sn", 1.0)["drift"] / r1_i
        outc = B.run("sn", 1.0)["drift"] / r1_i
        quant = B.run("quantized", 1.0)["drift"] / r1_i
        disc.append(dict(scenario=name, theory_i=ti, theory_ii=tii, sn=s_n, outcome=outc,
                          quant=quant))
    OUT["discriminators"] = disc

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "check.json", "w") as fh:
        json.dump(OUT, fh, indent=1, default=float)
    print(f"\nwritten to {RESULTS_DIR / 'check.json'}")
    return OUT


if __name__ == "__main__":
    main()
