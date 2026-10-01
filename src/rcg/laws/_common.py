"""Shared plumbing for the five comparison laws: the three steady-state
covariances every law is built from, computed once per call."""
from .. import constants as K
from .. import law as _law
from ..models import gaussian as G


def raw(platform, L_ro, L_anc, rule="i", eta_det=0.8, extra_D=0.0):
    """The quantities every law reads from: the platform's steady state under no
    conditioning, under conditioning on every record, and under conditioning on
    the readout alone, all at the same total diffusion D."""
    m, w0, gam = platform.m, platform.w0, platform.gam
    D = platform.D_env + K.HBAR ** 2 * (L_ro + L_anc) + extra_D
    L_tot = D / K.HBAR ** 2
    V_unc = G.cov_steady(m, w0, gam, D, 0.0)
    V_all = G.cov_steady(m, w0, gam, D, L_tot)
    V_det = G.cov_steady(m, w0, gam, D, eta_det * L_ro) if L_ro > 0 else V_unc
    eta = G.eta_eff(V_unc)
    f = float(_law.RULES[rule](eta))
    return dict(
        m=m,
        w0=w0,
        gam=gam,
        D=D,
        L_tot=L_tot,
        wsn2=platform.wsn2,
        V_unc=V_unc,
        V_all=V_all,
        V_det=V_det,
        eta=eta,
        f=f,
        L_ro=L_ro,
        eta_det=eta_det,
    )


def s_imp(L_ro, eta_det):
    return G.imprecision(L_ro, eta_det) if L_ro > 0 else 0.0
