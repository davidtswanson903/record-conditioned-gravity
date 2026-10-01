r"""The sourcing law: two interpolation rules for the record-conditioned density, in
closed form, with nothing fitted.

THE LAW, in symbols (the claim ids are the source theory's; PROVENANCE.md says where
that theory lives and nothing in this package needs it to be read).

    the source responds to the mass's state conditioned on the records that exist:
        n_r(x) = the MEAN density with no record, the RECORDED BRANCH alone with a
                 perfect one, and each branch normalized to weight one half.
    Two rules interpolate between those endpoints, in the overlap eta of the record
    two branches would leave (eta = 1: no record: eta = 0: a perfect one):

        rule (i)    n_r^A = eta (n_A + n_B) + (1 - eta) 2 n_A = (2 - eta) n_A + eta n_B
        rule (ii)   n_r^A = 2[(1 - P) n_A + P n_B],  P = (1 - sqrt(1 - eta^2)) / 2

f(eta) is the weight the law puts on the OTHER branch, normalized to its no-record
value of one half. Read off the two rules' own algebra, with nothing fitted:

    rule (i):   f(eta) = eta
    rule (ii):  f(eta) = 2P = 1 - sqrt(1 - eta^2)

Both satisfy f(1) = 1, f(0) = 0, and are continuous and monotonic.
"""
import numpy as np

from . import constants as K


# --------------------------------------------------------------- the two rules
def f_rule_i(eta):
    return np.asarray(eta, dtype=float)


def f_rule_ii(eta):
    e = np.asarray(eta, dtype=float)
    return 1.0 - np.sqrt(np.clip(1.0 - e * e, 0.0, None))


RULES = {"i": f_rule_i, "ii": f_rule_ii}


def n_r(rule, eta, n_own, n_other):
    """The record-conditioned density for the description on branch 'own'.

    `rule` is one of five laws compared throughout the computational check:
      'rule_i', 'rule_ii'   the two interpolation rules above
      'sn'                  unconditional Schroedinger-Newton: the mean, always
      'collapse'            the recorded branch only (a perfect record, always)
      'quantized'           no semiclassical source at all
    """
    if rule == "rule_i":
        return eta * (n_own + n_other) + (1 - eta) * 2 * n_own
    if rule == "rule_ii":
        P = (1 - np.sqrt(max(1 - eta ** 2, 0.0))) / 2
        return 2 * ((1 - P) * n_own + P * n_other)
    if rule == "sn":
        return n_own + n_other
    if rule == "collapse":
        return 2 * n_own
    if rule == "quantized":
        return 0 * n_own
    raise ValueError(rule)


# ------------------------------------------- the self-gravity frequency's import
def omega_sn_sq_from_shift(dwsn_times_w0):
    """wsn^2 = 2 * dwsn_times_w0.

    `dwsn_times_w0` is [G16]'s published level-splitting shift times the trap
    frequency it was computed at: a material constant independent of w0, since
    [G16] eq. 8 has the shift itself proportional to 1/w0. The adapter's own
    small-shift expansion (models.gaussian / experiments/realistic) gives
    w_q - w0 = wsn^2 / (2 w0); equating that to the published shift,
    Delta-omega_SN = dwsn_times_w0 / w0, gives wsn^2 = 2 w0 Delta-omega_SN
    = 2 dwsn_times_w0, with w0 cancelling exactly. See data/platforms.yaml for the
    table this reads, and docs/law.md for the one-paragraph derivation.

    IMPORT: omega_sc^2 = omega_0^2 + f(eta) omega_SN^2 places f(eta) in front of the
    whole Schroedinger-Newton frequency squared. That is the literature's oscillator
    result with the theory's weight inserted; it assumes the self-gravity term
    enters omega_sc^2 linearly in the source's cross-branch weight, which is not a
    consequence of the sourcing law. See LIMITS.md.
    """
    return 2.0 * dwsn_times_w0


def dwsn_times_w0_formula(atomic_mass_u, sigma_m):
    """[G16] eq. 8's own formula for the material constant above:
    sqrt(2/pi) G m_atom / (3 sigma^3). Used only to check the published table
    against its own equation (tests/test_equivalence.py)."""
    return float(
        np.sqrt(2 / np.pi) * K.GNEWT * atomic_mass_u * K.AMU / (3 * sigma_m ** 3)
    )


def independent_omega_sn_estimate(atomic_mass_u, sigma_m):
    """An independent closed form for the crystal-regime frequency,
    w_SN^2 = G m_atom / (6 sqrt(pi) sigma^3), NOT the one the pipeline uses.

    Not used by any experiment in this repository and feeds no emitted number; kept
    only so a reviewer can sanity-check the published table's order of magnitude
    against a second, independently-stated formula for the same physics."""
    return float(
        np.sqrt(K.GNEWT * atomic_mass_u * K.AMU / (6 * np.sqrt(np.pi) * sigma_m ** 3))
    )
