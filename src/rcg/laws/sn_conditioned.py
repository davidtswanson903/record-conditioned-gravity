"""The measurement-conditioned alternative: the source is conditioned on what the
EXPERIMENTER'S readout alone has resolved, not on every record that exists. This
is the proposal's own discriminator law: a distant party's choice of measurement
basis moves this law's prediction (it signals), where the record-conditioned
law's does not (see tests/test_law.py and T4 in experiments/check)."""
from ..models import gaussian as G
from . import _common
from .prediction import build


def predict(platform, L_ro, L_anc, rule="i", eta_det=0.8):
    r = _common.raw(platform, L_ro, L_anc, rule=rule, eta_det=eta_det)
    if L_ro > 0:
        W = r["V_det"][0]
        G2 = G.linewidth_q(r["gam"], eta_det * L_ro, W)
    else:
        # no readout at all: nothing conditions the source on anything, so there
        # is no second peak. (A fixed-point artefact in the pipeline this package
        # replaces returned W = V_unc here instead; it was never exercised by any
        # emitted number, and this is the physical answer.)
        W, G2 = 0.0, r["gam"]
    return build("mc_sn", r, f_main=0.0, W=W, G2=G2, S_imp=_common.s_imp(L_ro, eta_det))
