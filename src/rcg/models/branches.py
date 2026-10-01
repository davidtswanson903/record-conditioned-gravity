"""Two branch amplitudes on a grid, each evolving in its own record-conditioned
potential -- exactly what the law says: each description's geometry is sourced by
its own conditioned state. No sampling and no fitting anywhere; a split-step
Fourier propagation on a grid of a few hundred to a few thousand points.
"""
import numpy as np

from .. import law as _law

GRID = dict(nx=512, lx=200.0, d=20.0, sigma=3.0, g=0.5, rs=1.0, dt=0.02, t_final=30.0)


class Branches:
    """Two branch amplitudes, each evolving in its own record-conditioned
    potential, under a softened 1/r kernel on a periodic grid."""

    def __init__(self, c=None):
        self.c = dict(GRID) if c is None else dict(c)
        c = self.c
        self.x = np.linspace(-c["lx"] / 2, c["lx"] / 2, c["nx"], endpoint=False)
        self.dx = self.x[1] - self.x[0]
        self.k = 2 * np.pi * np.fft.fftfreq(c["nx"], self.dx)
        wrapped = np.minimum(np.abs(self.x), c["lx"] - np.abs(self.x))
        self.kf = np.fft.fft(
            np.fft.ifftshift(-c["g"] / np.sqrt(wrapped ** 2 + c["rs"] ** 2))
        )

    def pot(self, n):
        return np.real(np.fft.ifft(np.fft.fft(n) * self.kf)) * self.dx

    def packet(self, centre):
        p = np.exp(-(self.x - centre) ** 2 / (4 * self.c["sigma"] ** 2))
        return p / np.sqrt(np.sum(np.abs(p) ** 2) * self.dx / 0.5)

    def run(self, rule, eta, t_final=None, record=None):
        """Propagate; returns the drift of A's centre toward B, the cross-branch
        potential energy, and the total energy before and after. `record` is an
        optional callable(step) -> eta, so a record can be written or erased
        part-way through."""
        c = self.c
        t_final = c["t_final"] if t_final is None else t_final
        pa, pb = self.packet(-c["d"] / 2), self.packet(+c["d"] / 2)
        kin = np.exp(-0.5j * self.k ** 2 * c["dt"])
        steps = int(t_final / c["dt"])
        e0 = None
        for s in range(steps):
            e = eta if record is None else record(s)
            na, nb = np.abs(pa) ** 2, np.abs(pb) ** 2
            va = self.pot(_law.n_r(rule, e, na, nb))
            vb = self.pot(_law.n_r(rule, e, nb, na))
            if e0 is None:
                e0 = self.energy(pa, pb, rule, e)
            pa = np.fft.ifft(kin * np.fft.fft(np.exp(-1j * va * c["dt"]) * pa))
            pb = np.fft.ifft(kin * np.fft.fft(np.exp(-1j * vb * c["dt"]) * pb))
        na, nb = np.abs(pa) ** 2, np.abs(pb) ** 2
        e = eta if record is None else record(steps - 1)
        drift = float(np.sum(self.x * na) / np.sum(na) + c["d"] / 2)
        cross = float(np.sum(self.pot(nb) * na) * self.dx)   # A's energy in B's own field
        return dict(
            drift=drift, cross=cross, energy0=e0, energy1=self.energy(pa, pb, rule, e)
        )

    def weights(self, rule, eta):
        """n_r^A = alpha n_A + beta n_B: the law's own two coefficients, read off
        from the two-argument form."""
        one, zero = np.ones(1), np.zeros(1)
        a = float(_law.n_r(rule, eta, one, zero)[0])
        b = float(_law.n_r(rule, eta, zero, one)[0])
        return a, b

    def energy(self, pa, pb, rule, eta):
        """The CONSERVED energy of the branch-resolved nonlinear system.

        The dynamics is i d_t psi_A = (-(1/2) d^2 + K*(alpha n_A + beta n_B)) psi_A
        and its mirror. That is Hamiltonian for

            E = T_A + T_B + (alpha/2)(<n_A K n_A> + <n_B K n_B>) + beta <n_A K n_B>

        since dE/dn_A = alpha K*n_A + beta K*n_B = V_A exactly, and likewise for B.
        Summing <V_A n_A> + <V_B n_B> instead double-counts the self terms by two
        and the cross term by two, and reports a spurious one-to-twelve-per-cent
        drift that belongs to the functional rather than the integrator.
        """
        alpha, beta = self.weights(rule, eta)
        kin = 0.0
        for p in (pa, pb):
            pk = np.fft.fft(p)
            kin += float(np.sum(0.5 * self.k ** 2 * np.abs(pk) ** 2) / len(self.x) * self.dx)
        na, nb = np.abs(pa) ** 2, np.abs(pb) ** 2
        Ka, Kb = self.pot(na), self.pot(nb)
        self_t = 0.5 * alpha * float(np.sum(Ka * na + Kb * nb) * self.dx)
        cross_t = beta * float(np.sum(Ka * nb) * self.dx)
        return kin + self_t + cross_t

    def force_profile(self, rule, eta, separations):
        """The cross-branch force on A at each separation, from the law's own
        weight on the other branch alone."""
        out = []
        for d in separations:
            c = dict(self.c)
            c["d"] = d
            b = Branches(c)
            na = np.abs(b.packet(-d / 2)) ** 2
            nb = np.abs(b.packet(+d / 2)) ** 2
            other = _law.n_r(rule, eta, na, nb) - _law.n_r(rule, eta, na, 0 * nb)
            v = b.pot(other)
            dv = np.gradient(v, b.dx)
            out.append(-float(np.sum(dv * na) * b.dx / np.sum(na) / b.dx * b.dx))
        return np.array(out)
