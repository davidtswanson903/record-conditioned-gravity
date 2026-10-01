"""Standard quantum mechanics: no self-gravity term at all. The oscillator sits at
w0 regardless of any record, which is this package's required control -- nothing
here should move when the ancilla is switched."""
from . import _common
from .prediction import build


def predict(platform, L_ro, L_anc, rule="i", eta_det=0.8):
    r = _common.raw(platform, L_ro, L_anc, rule=rule, eta_det=eta_det)
    return build(
        "qm", r, f_main=0.0, W=0.0, G2=r["gam"], S_imp=_common.s_imp(L_ro, eta_det)
    )
