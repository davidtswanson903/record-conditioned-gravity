"""The five comparison laws, each predicting a main resonance and (where it has
one) a second, record-conditioned resonance, from the same underlying Gaussian
filter (rcg.models.gaussian).

    law         main peak at              second peak, weight       its half width
    theory      sqrt(w0^2 + f wsn^2)       V_all  (every record)     gam + 8 L_tot V_all
    mc_sn       w0                         V_det  (readout alone)    gam + 8 eta L_ro V_det
    uncond_sn   sqrt(w0^2 + wsn^2)         -- (the whole state moves)  gam
    qm          w0                         -- (no self-gravity term)   gam
    collapse    w0                         -- (extra diffusion instead) gam

Common interface: predict(platform, L_ro, L_anc, rule='i', eta_det=0.8) -> Prediction.
"""
import numpy as np

from . import collapse, quantum, sn_conditioned, sn_unconditional, theory
from .prediction import Prediction

LAWS = {
    "theory": theory.predict,
    "mc_sn": sn_conditioned.predict,
    "uncond_sn": sn_unconditional.predict,
    "qm": quantum.predict,
    "collapse": collapse.predict,
}


def predict(law, platform, L_ro, L_anc, rule="i", eta_det=0.8):
    return LAWS[law](platform, L_ro, L_anc, rule=rule, eta_det=eta_det)


def spectrum(pred, w):
    """The full measured PSD: both Lorentzians plus the imprecision floor, in
    m^2/(rad/s). The MAIN peak's width is the platform's bare damping gam (the
    law's conditioning narrows only the SECOND peak); the second peak's width is
    its own G2."""
    w = np.asarray(w, dtype=float)
    out = (
        2.0 * (pred.V_unc - pred.W) * pred.gam / ((w - pred.w_main) ** 2 + pred.gam ** 2)
    ) + pred.S_imp
    if pred.W > 0:
        out = out + 2.0 * pred.W * pred.G2 / ((w - pred.w_q) ** 2 + pred.G2 ** 2)
    return out


def grid(preds):
    """A frequency grid that resolves every feature in play.

    A single uniform grid cannot do this: the main line can be 1e-15 rad/s wide
    while the second peak is 1e-3, so a grid fine enough for the first needs 1e12
    points. The integrand used by tau_separate is zero wherever the two spectra
    agree, so the grid is the union of a local patch around each feature of each
    prediction instead."""
    parts = []
    for p in preds:
        feats = [(p.w_main, max(p.gam, 1e-300))]
        if p.W > 0:
            feats.append((p.w_q, max(p.G2, 1e-300)))
        for c, wdt in feats:
            parts.append(np.linspace(max(c - 300 * wdt, 1e-12 * c), c + 300 * wdt, 6001))
    return np.unique(np.concatenate(parts))


def tau_separate(predA, predB):
    """Time to tell prediction A from prediction B at five sigma, with the shape
    of the background known exactly -- a bound on any protocol, from the Whittle
    log-likelihood ratio: SNR^2 = (tau/4pi) integral dw ((S_A-S_B)/S_A)^2."""
    w = grid([predA, predB])
    SA, SB = spectrum(predA, w), spectrum(predB, w)
    r = ((SA - SB) / SA) ** 2
    integ = float(np.trapezoid(r, w))
    if integ <= 0:
        return float("inf"), integ
    # One oscillation period is the floor: no spectrum is measured in less than a
    # cycle. Nothing stronger belongs here -- in particular NOT the ringdown time
    # of the narrowest line, since telling a resonance at 0.7 rad/s from one at
    # 0.006 rad/s does not require resolving either line's width.
    floor = 2.0 * np.pi / max(predA.w_q, predA.w_main, predB.w_q, predB.w_main)
    return max(100.0 * np.pi / integ, floor), integ


def fmt_time(t):
    from .. import constants as K

    if not np.isfinite(t):
        return "never"
    if t > 1e3 * K.YEAR:
        return f"{t / K.YEAR:.2e} yr"
    if t > K.YEAR:
        return f"{t / K.YEAR:.3g} yr"
    if t > 3600:
        return f"{t / 3600:.3g} h"
    return f"{t:.3g} s"
