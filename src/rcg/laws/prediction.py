"""The common shape every comparison law returns: a main resonance and (where the
law has one) a second, record-conditioned resonance, built from the same
underlying Gaussian filter (see rcg.models.gaussian)."""
from dataclasses import dataclass

import numpy as np

from ..models import gaussian as G


@dataclass(frozen=True)
class Prediction:
    law: str
    w0: float
    gam: float           # the platform's bare mechanical damping -- the MAIN peak's width
    w_main: float         # where the main resonance sits
    W: float              # the second peak's weight (a variance); 0 if the law has none
    G2: float              # the second peak's half width (meaningless if W == 0)
    w_q: float             # where a fully resolved second peak would sit
    split: float            # w_q - w_main, formed to stay accurate at any w0
    f: float                 # the law's weight on the unconditioned density (0 unless 'theory')
    V_unc: float              # the unconditioned variance
    V_all: float               # the variance conditioned on every record
    V_det: float                 # the variance conditioned on the readout alone
    eta_eff: float                # the record overlap the adapter reads off V_unc's purity
    purity: float                   # the unconditioned state's purity
    S_imp: float                     # the readout's imprecision floor, 0 if no readout

    @property
    def resolvability(self):
        """The second peak's distance from the main line, divided by its own half
        width. Below one it is a shoulder, not a peak, and no integration time
        recovers it."""
        return self.split / self.G2 if self.W > 0 else float("nan")


def build(law, r, f_main, W, G2, S_imp=0.0):
    """Assemble a Prediction from `laws._common.raw`'s shared quantities and one
    law's own choice of (f_main, W, G2)."""
    w0, wsn2 = r["w0"], r["wsn2"]
    w_q = float(np.sqrt(w0 ** 2 + wsn2))
    w_main = float(np.sqrt(w0 ** 2 + f_main * wsn2))
    # formed as a product over a sum, not by subtracting two square roots: at a
    # few hundred kHz the difference is 1e-9 of either term and a literal
    # subtraction returns the rounding error, sign and all.
    split = float((1.0 - f_main) * wsn2 / (w_q + w_main))
    return Prediction(
        law=law,
        w0=w0,
        gam=r["gam"],
        w_main=w_main,
        W=W,
        G2=G2,
        w_q=w_q,
        split=split,
        f=r["f"],
        V_unc=r["V_unc"][0],
        V_all=r["V_all"][0],
        V_det=r["V_det"][0],
        eta_eff=r["eta"],
        purity=G.purity(r["V_unc"]),
        S_imp=S_imp,
    )
