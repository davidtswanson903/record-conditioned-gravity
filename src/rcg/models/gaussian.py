r"""A continuously recorded Gaussian oscillator: filtering theory's steady state,
and the record-conditioned source's reduction to it.

THE ADAPTER, from two branches and one overlap to a real oscillator, in three
steps, each one forced rather than chosen:

  (a) HOW MUCH RECORD EXISTS. In the two-branch case the reduced state has
      Tr rho^2 = (1 + eta^2)/2 exactly, so eta = sqrt(2 Tr rho^2 - 1). That is
      basis-independent and defined for any state, so it is the adapter's handle:
          eta_eff = sqrt(max(0, 2 purity - 1)),   purity = hbar / (2 sqrt(det V))
      read off the UNCONDITIONED covariance, since that is the state whose
      mixedness the records caused.

  (b) WHAT THE SOURCE IS. The law reads: n_r = f(eta)*(the unconditioned density)
      + (1 - f(eta))*(the branch's own density). For a Gaussian state the
      'branch's own density' is the state conditioned on every record that
      exists -- the filtering solution at unit efficiency on every channel. So
          source mean  mu_s = f * mu_unc + (1 - f) * mu_all
      and in the two-branch limit this reproduces the law's own interpolation,
      term for term (tests/test_equivalence.py checks this to machine precision).

  (c) WHAT IT DOES. In the crystal regime the self-gravity term is
      (1/2) m w_SN^2 (x - mu_s)^2. With mu_s as in (b) and x = mu_all + delta:
          the conditional mean resonates at   w_c = sqrt(w0^2 + f w_SN^2)
          the fluctuation about it, at         w_q = sqrt(w0^2 +     w_SN^2)
      so the measured spectrum carries TWO peaks, the second weighted by the
      conditional variance of whichever state the law conditions on.

eta_eff is real only while Tr rho^2 >= 1/2, i.e. while the state carries at most
two branches' worth of mixedness. A thermal oscillator is far past that; the
adapter sets f = 0 there (the record is MORE than perfect, so the source is the
fully conditioned state), which is the only continuous reading but is an
extrapolation of the law past where it is stated for two branches. See LIMITS.md
and experiments/realistic/stage4_robust.py, which checks this extrapolation
against an independent reading (coherence at the lattice scale) and finds they
agree wherever the conclusion depends on it.

Everything below is closed form or a one-dimensional root; nothing is fitted.
"""
import numpy as np
from scipy.optimize import brentq

from .. import constants as K


# ------------------------------------------------- the conditional covariance
def cov_steady(m, w0, gam, D, mu):
    """Steady state of the Gaussian filter for a damped oscillator.

        dVx  = 2 Vxp/m - 8 mu Vx^2
        dVxp = Vp/m - m w0^2 Vx - gam Vxp - 8 mu Vx Vxp
        dVp  = -2 m w0^2 Vxp - 2 gam Vp + 2 D - 8 mu Vxp^2

    D   total momentum diffusion [kg^2 m^2 s^-3], every channel summed;
    mu  the MONITORED localization rate [m^-2 s^-1], i.e. the sum of eta_k Lambda_k
        over the channels whoever holds this description can read.

    mu = D/hbar^2 is 'every channel is a record, read at unit efficiency' -- the
    theory's own conditioning. mu = eta_det Lambda_readout is the experimenter's.
    mu = 0 is no conditioning at all.

    Eliminating Vxp and Vp leaves one quartic in Vx with positive coefficients, so
    the positive root is unique:
        64 m^2 mu^3 Vx^4 + 32 m^2 gam mu^2 Vx^3
      + 4 m^2 mu (w0^2 + gam^2) Vx^2 + gam m^2 w0^2 Vx - D = 0
    """
    hi = D / (gam * m ** 2 * w0 ** 2)                    # the mu = 0 value, the maximum
    if mu <= 0.0:
        Vx = hi
    else:
        # the root can sit twenty orders below hi, so it is found in log Vx: the
        # quartic's coefficients span eighty orders and a linear bracket's xtol
        # would swallow the answer whole.
        def ql(u):
            v = np.exp(u)
            return (
                64 * m ** 2 * mu ** 3 * v ** 4
                + 32 * m ** 2 * gam * mu ** 2 * v ** 3
                + 4 * m ** 2 * mu * (w0 ** 2 + gam ** 2) * v ** 2
                + gam * m ** 2 * w0 ** 2 * v
                - D
            )

        u_hi = np.log(hi)
        u_lo = u_hi - 160.0
        while ql(u_lo) > 0.0 and u_lo > u_hi - 700.0:     # widen if ever needed
            u_lo -= 80.0
        Vx = float(np.exp(brentq(ql, u_lo, u_hi, rtol=8.9e-16, xtol=1e-14, maxiter=500)))
    Vxp = 4 * m * mu * Vx ** 2
    Vp = (
        m ** 2 * w0 ** 2 * Vx
        + 4 * m ** 2 * gam * mu * Vx ** 2
        + 32 * m ** 2 * mu ** 2 * Vx ** 3
    )
    return Vx, Vxp, Vp


def residual(m, w0, gam, D, mu, V):
    """The three steady-state equations' own residuals, for a convergence check."""
    Vx, Vxp, Vp = V
    return (
        abs(2 * Vxp / m - 8 * mu * Vx ** 2),
        abs(Vp / m - m * w0 ** 2 * Vx - gam * Vxp - 8 * mu * Vx * Vxp),
        abs(-2 * m * w0 ** 2 * Vxp - 2 * gam * Vp + 2 * D - 8 * mu * Vxp ** 2),
    )


def purity(V):
    Vx, Vxp, Vp = V
    return K.HBAR / (2.0 * np.sqrt(Vx * Vp - Vxp ** 2))


def eta_eff(V):
    """How much record exists, on the two-branch state's own definition. Clipped
    into [0, 1]: purity above 1 is arithmetic, not physics."""
    return float(np.sqrt(min(1.0, max(0.0, 2.0 * purity(V) - 1.0))))


def linewidth_q(gam, mu, Vx):
    """How fast the conditional fluctuation is re-randomized: the Riccati's own
    damping of a perturbation in Vx, which sets the second peak's half width."""
    return gam + 8.0 * mu * Vx


def jacobian_rates(m, w0, gam, mu, V):
    """The Riccati's relaxation rates at the fixed point, as a cross-check on
    linewidth_q: -Re of the eigenvalues of d(dV/dt)/dV."""
    Vx, Vxp, _ = V
    J = np.array(
        [
            [-16 * mu * Vx, 2.0 / m, 0.0],
            [-m * w0 ** 2 - 8 * mu * Vxp, -gam - 8 * mu * Vx, 1.0 / m],
            [0.0, -2 * m * w0 ** 2 - 16 * mu * Vxp, -2 * gam],
        ]
    )
    return np.sort(-np.real(np.linalg.eigvals(J)))


# --------------------------------------------------------- decoherence channels
def n_bose(w0, T):
    """The thermal occupation. The high-temperature form kT/(hbar w0) is wrong by
    a factor of two at nbar ~ 1/2, exactly where f turns on, so the Bose factor is
    used everywhere in this package."""
    x = K.HBAR * w0 / (K.KB * T)
    return float(1.0 / np.expm1(x)) if x < 500 else 0.0


def D_thermal(m, gam, w0, T):
    """Momentum diffusion for a bath at T damping at gamma,
           D = m gamma hbar w0 (nbar + 1/2),
    Caldeira-Leggett's m gamma k T in the high-temperature limit and
    m gamma hbar w0 / 2 at T = 0. The high-temperature form alone puts the
    unconditional variance BELOW the ground state near nbar = 1/2 and hands back a
    purity above one. Lambda = D/hbar^2 is the bath's localization rate, and it is
    a POSITION record: the bath resolves where the mass is. (A bath that recorded
    momentum instead would need a different adapter -- an open edge; see LIMITS.md.)
    """
    return float(m * gam * K.HBAR * w0 * (n_bose(w0, T) + 0.5))


def D_heating(m, w0, nbar_dot):
    """An anomalous trap heating rate quoted in quanta per second.
    dE/dt = nbar_dot hbar w0 and d<p^2>/dt = 2D, so D = m nbar_dot hbar w0 / 2."""
    return float(m * nbar_dot * K.HBAR * w0 / 2.0)


def D_readout(m, w0, Lambda_ro):
    return float(K.HBAR ** 2 * Lambda_ro)


def Lambda_from_D(D):
    return float(D / K.HBAR ** 2)


def imprecision(Lambda_ro, eta_det):
    """The position imprecision PSD matching a monitored localization rate, from
    the filter's own information term: S_imp = 1/(8 eta Lambda). [m^2/(rad/s)]"""
    return 1.0 / (8.0 * eta_det * Lambda_ro)


def gamma_gas(m, radius, pressure_pa, T_gas, gas_amu=4.0):
    """Epstein free-molecular drag on a sphere, b = (16/3) R^2 P sqrt(2 pi m_g/kT).
    Free molecular flow is the right regime at laboratory vacuum (the mean free
    path is kilometres). IMPORT: the drag coefficient is kinetic theory's, with an
    accommodation coefficient of one."""
    b = (16.0 / 3.0) * radius ** 2 * pressure_pa * np.sqrt(
        2 * np.pi * gas_amu * K.AMU / (K.KB * T_gas)
    )
    return float(b / m)


# -------------------------------------------- the extrapolation, read a second way
def coherence(V, s):
    """The reduced state's off-diagonal decay at separation s, relative to the
    pure state of the same position variance. 1 means no record at that scale,
    0 means a perfect one. A second, independent reading of how much record
    exists, used to check eta_eff's extrapolation past rank 2 (LIMITS.md)."""
    Vx, Vxp, Vp = V
    Sigma = Vp - Vxp ** 2 / Vx
    excess = Sigma - K.HBAR ** 2 / (4 * Vx)
    if excess <= 0:
        return 1.0
    return float(np.exp(-excess * s ** 2 / (2 * K.HBAR ** 2)))


def coherence_length(V):
    """The separation at which the coherence has fallen by exp(-1/2)."""
    Vx, Vxp, Vp = V
    excess = Vp - Vxp ** 2 / Vx - K.HBAR ** 2 / (4 * Vx)
    return float(np.inf) if excess <= 0 else float(K.HBAR / np.sqrt(excess))


def thermal_length(m, T):
    return float(K.HBAR / np.sqrt(m * K.KB * T))
