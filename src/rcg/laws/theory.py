"""The theory's own law: the source is conditioned on EVERY record that exists,
read not or unread, deliberate register or ordinary decoherence alike."""
from ..models import gaussian as G
from . import _common
from .prediction import build


def predict(platform, L_ro, L_anc, rule="i", eta_det=0.8):
    r = _common.raw(platform, L_ro, L_anc, rule=rule, eta_det=eta_det)
    G2 = G.linewidth_q(r["gam"], r["L_tot"], r["V_all"][0])
    return build(
        "theory", r, f_main=r["f"], W=r["V_all"][0], G2=G2,
        S_imp=_common.s_imp(L_ro, eta_det),
    )
