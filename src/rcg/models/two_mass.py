"""Two qubits, each standing for one mass's two-branch superposition: under the
theory's mean-field law (each mass moves in the OTHER's mean field, which is the
sourcing law's own relational form) and under a quantized two-body coupling.
"""
import numpy as np

PAIR = dict(a1=0.4, p1=0.3, a2=1.1, p2=-0.7, g=1.0, dt=1e-3, steps=2001, stride=500)


def qubit(a, p):
    return np.array([np.cos(a), np.exp(1j * p) * np.sin(a)], dtype=complex)


def concurrence(psi):
    y = np.array([[0, -1j], [1j, 0]])
    yy = np.kron(y, y)
    rho = np.outer(psi, psi.conj())
    r = rho @ yy @ rho.conj() @ yy
    v = np.sqrt(np.abs(np.sort(np.linalg.eigvals(r).real)[::-1]))
    return float(max(0.0, v[0] - v[1] - v[2] - v[3]))


def negativity(psi):
    """The negativity of a two-qubit pure state: the sum, in absolute value, of
    the negative eigenvalues of the partial transpose."""
    rho = np.outer(psi, psi.conj()).reshape(2, 2, 2, 2)
    rho_pt = rho.transpose(0, 3, 2, 1).reshape(4, 4)
    w = np.linalg.eigvalsh(rho_pt)
    return float(np.sum(np.abs(w[w < 0])))


def two_mass(law, c=PAIR):
    """Two masses as two qubits. 'quantized' applies exp(-i g t sz sz) on the
    pair; 'theory' lets each qubit move in the other's MEAN field, the sourcing
    law's own relational form. Returns a list of snapshots."""
    psi1, psi2 = qubit(c["a1"], c["p1"]), qubit(c["a2"], c["p2"])
    psi = np.kron(psi1, psi2)
    sz = np.array([1.0, -1.0])
    szsz = np.kron(sz, sz)
    out = []
    for s in range(c["steps"]):
        if s % c["stride"] == 0 and s > 0:
            out.append(
                dict(
                    t=s * c["dt"],
                    concurrence=concurrence(psi),
                    negativity=negativity(psi),
                    phase1=float(np.angle(psi1[1] / psi1[0]) if law == "theory" else 0.0),
                )
            )
        if law == "quantized":
            psi = np.exp(-1j * c["g"] * szsz * c["dt"]) * psi
        elif law == "theory":
            m1 = float(np.real(np.conj(psi1) @ (sz * psi1)))
            m2 = float(np.real(np.conj(psi2) @ (sz * psi2)))
            psi1 = np.exp(-1j * c["g"] * m2 * sz * c["dt"]) * psi1
            psi2 = np.exp(-1j * c["g"] * m1 * sz * c["dt"]) * psi2
            psi = np.kron(psi1, psi2)
        else:
            raise ValueError(law)
    return out
