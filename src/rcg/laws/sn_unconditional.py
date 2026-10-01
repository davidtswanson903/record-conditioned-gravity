"""Unconditional Schroedinger-Newton: the source is the mean density, whatever
records exist or do not. No second peak; the WHOLE state moves to
sqrt(w0^2 + w_SN^2), which is the frequency shift the literature bounds."""
from . import _common
from .prediction import build


def predict(platform, L_ro, L_anc, rule="i", eta_det=0.8):
    r = _common.raw(platform, L_ro, L_anc, rule=rule, eta_det=eta_det)
    return build(
        "uncond_sn", r, f_main=1.0, W=0.0, G2=r["gam"],
        S_imp=_common.s_imp(L_ro, eta_det),
    )
