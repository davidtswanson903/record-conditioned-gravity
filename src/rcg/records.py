"""Registers: the mass's branch label tensored with register and environment qubits,
as an exact state vector.

The law reads only the mass's REDUCED state. Nothing in this module computes a
source; it only produces the register overlap eta that `rcg.law` then reads. This
is the whole point of the no-signalling tests: a change to the register here is
visible to this module, and the question is whether it reaches eta_eff.
"""
import numpy as np


def record_unitary(eta, n_branch=2):
    """The record channel |x>|0> -> |x>|r_x>, with <r_L|r_R> = eta, as an isometry
    on the branch-label-tensor-qubit space. |r_L> = |0>, |r_R> = eta|0> + s|1>."""
    s = np.sqrt(max(1.0 - eta ** 2, 0.0))
    U = np.zeros((n_branch * 2, n_branch * 2), dtype=complex)
    # basis order: (branch, register) = (0,0),(0,1),(1,0),(1,1)
    U[0, 0], U[1, 1] = 1.0, 1.0           # branch L: register untouched
    U[2, 2], U[3, 2] = eta, s             # branch R: |0> -> eta|0> + s|1>
    U[2, 3], U[3, 3] = -s, eta            # unitary completion
    return U


class Register:
    """The mass's branch label tensored with registers; the law sees only rho_S."""

    def __init__(self, weights=(0.5, 0.5)):
        self.w = np.asarray(weights, dtype=float)
        self.psi = np.sqrt(self.w).astype(complex)   # on the branch space alone
        self.dims = [len(self.w)]

    def attach(self, eta):
        """Write a record of the branch into a fresh qubit at overlap eta."""
        s = np.sqrt(max(1.0 - eta ** 2, 0.0))
        r = np.zeros((len(self.w), 2), dtype=complex)
        r[0] = [1.0, 0.0]
        r[1] = [eta, s]
        self.psi = (
            (self.psi.reshape(-1, 1) * r.reshape(len(self.w), 2)).reshape(-1)
            if self.psi.size == len(self.w)
            else np.einsum(
                "b...,bj->b...j",
                self.psi.reshape([len(self.w)] + [2] * (len(self.dims) - 1)),
                r,
            ).reshape(-1)
        )
        self.dims = self.dims + [2]
        return self

    def attach_env(self, eta, dim=4, seed=0):
        """The same record, written into a `dim`-dimensional environment with a
        random basis: a generic decoherer rather than a deliberate register."""
        rng = np.random.default_rng(seed)
        A = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
        Q, _ = np.linalg.qr(A)
        s = np.sqrt(max(1.0 - eta ** 2, 0.0))
        r = np.zeros((len(self.w), dim), dtype=complex)
        r[0] = Q[:, 0]
        r[1] = eta * Q[:, 0] + s * Q[:, 1]
        self.psi = np.einsum(
            "b...,bj->b...j",
            self.psi.reshape([len(self.w)] + [2] * 0 + list(self.dims[1:])),
            r,
        ).reshape(-1)
        self.dims = self.dims + [dim]
        return self

    def apply_to_registers(self, U):
        """An arbitrary unitary on everything except the branch label."""
        t = self.psi.reshape(self.dims[0], -1)
        self.psi = (t @ U.T).reshape(-1)
        return self

    def rho_S(self):
        """The mass's reduced state, in the branch basis."""
        t = self.psi.reshape(self.dims[0], -1)
        return t @ t.conj().T

    def eta_eff(self):
        """The overlap the law reads off rho_S: the coherence normalized by the
        branch weights."""
        r = self.rho_S()
        w = np.real(np.diag(r))
        return float(np.abs(r[0, 1]) / np.sqrt(max(w[0] * w[1], 1e-300)))


def nested_record(etas, dim=2, seeds=None):
    """A chain of independent registers at overlaps `etas`; returns the Register."""
    m = Register()
    for i, e in enumerate(etas):
        if dim == 2:
            m.attach(e)
        else:
            m.attach_env(e, dim=dim, seed=(0 if seeds is None else seeds[i]))
    return m
