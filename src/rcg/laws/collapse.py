"""A CSL-type collapse rival: no self-gravity term, but extra position diffusion
at the rate Adler argues for.

IMPORT: the point-particle heating d<p^2>/dt = hbar^2 lambda (m/m0)^2 / (2 r_C^2)
is Bassi-Lochan-Satin-Singh-Ulbricht, Rev. Mod. Phys. 85, 471 (2013) eq. 61, with
no geometric reduction for a particle larger than r_C -- which OVERSTATES this
rival's heating, deliberately, since it is used here to exclude it on thermal
grounds alone (see experiments/realistic/stage2_virtual.py)."""
from .. import constants as K
from . import _common
from .prediction import build

CSL_LAMBDA, CSL_RC = 1e-8, 1e-7   # Adler's parameters, m0 = 1 amu


def D_csl(m):
    return K.HBAR ** 2 * CSL_LAMBDA * (m / K.AMU) ** 2 / (2 * CSL_RC ** 2)


def csl_lambda_bound(m, D_env):
    """The largest CSL lambda this platform's own thermal budget leaves room
    for, i.e. the bound a reviewer could extract without the self-gravity
    question being asked at all."""
    return float(D_env * 2 * CSL_RC ** 2 / (K.HBAR ** 2 * (m / K.AMU) ** 2))


def predict(platform, L_ro, L_anc, rule="i", eta_det=0.8):
    r = _common.raw(
        platform, L_ro, L_anc, rule=rule, eta_det=eta_det, extra_D=D_csl(platform.m)
    )
    return build(
        "collapse", r, f_main=0.0, W=0.0, G2=r["gam"], S_imp=_common.s_imp(L_ro, eta_det)
    )
