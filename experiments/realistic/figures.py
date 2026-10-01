"""The realistic-conditions experiment's four figures.

Three come straight from results/realistic.json. The resolvability map (fig 2)
and the Q/T-needed curve (fig 4) are surfaces of R_closed(w0, Q, T, wsn2) evaluated
on a fine grid -- too large to usefully store as a results file, so this script
imports stage3_map.R_closed, the same closed form results/realistic.json's own
'map' section used, rather than re-deriving it. Every SCATTERED point (the three
platforms, the corner) is read from the json.
"""
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
import numpy as np                                                  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from rcg import constants as K        # noqa: E402
from rcg import law as _law           # noqa: E402
from rcg import laws as L             # noqa: E402
from rcg import platforms as P        # noqa: E402
from rcg.models import gaussian as G  # noqa: E402

import stage3_map                      # noqa: E402

RESULTS = ROOT / "results" / "realistic.json"
OUT_DIR = ROOT / "build" / "figures"

# "theory" is the internal key this law is registered under (rcg.laws.theory,
# rcg.laws.LAWS["theory"], results/*.json's own field names) and stays that way
# everywhere it is a dict key or a variable name below. DISP is only for the
# few places a key becomes VISIBLE text (a legend entry, a title, a caption
# built from an f-string), so a reader sees "this law" -- the name used
# throughout the paper and docs -- rather than the internal key leaking out.
DISP = {"theory": "this law", "mc_sn": "mc_sn", "uncond_sn": "uncond_sn", "qm": "qm"}


def disp(law):
    return DISP.get(law, law)


def main():
    with open(RESULTS) as fh:
        D = json.load(fh)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
         "figure.dpi": 140, "savefig.bbox": "tight"}
    )

    # ---------------------------------------------------- fig 1: where f is nonzero
    nb = np.logspace(-3, 3, 400)
    pur = 1.0 / (2 * nb + 1)
    eta = np.sqrt(np.clip(2 * pur - 1, 0, 1))
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    ax.semilogx(nb, _law.f_rule_i(eta), label=r"rule (i), $f=\eta$")
    ax.semilogx(nb, _law.f_rule_ii(eta), label="rule (ii)")
    ax.axvline(0.5, color="k", ls="--", lw=0.8)
    ax.annotate(r"$\bar n = 1/2$", xy=(0.52, 0.6), fontsize=8)
    for key, row in D["stage1_platforms"]["baseline"].items():
        ax.plot([row["nbar"]], [row["eta_eff"]], "o", ms=6)
        ax.annotate(key, xy=(row["nbar"], row["eta_eff"]), xytext=(0, 7),
                    textcoords="offset points", fontsize=7, ha="center")
    ax.set_xlabel(r"thermal occupation $\bar n$")
    ax.set_ylabel("$f$, the law's weight on the unconditioned state")
    ax.set_title("where a record leaves anything to switch")
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(OUT_DIR / "realistic-1-baseline.pdf")
    fig.savefig(OUT_DIR / "realistic-1-baseline.png")
    plt.close(fig)

    # --------------------------------------------- fig 2: resolvability map
    fz = np.logspace(-4, 6.2, 190)
    Ts = np.logspace(-6, 2.7, 175)
    FZ, TT = np.meshgrid(fz, Ts)
    wsn2 = P.omega_sn_sq(P.MATERIALS["osmium"])
    fig, axs = plt.subplots(1, 3, figsize=(9.2, 3.0), sharey=True)
    for ax, Q in zip(axs, (1e8, 1e10, 1e12)):
        Rm = np.vectorize(lambda f_, T_: stage3_map.R_closed(2 * np.pi * f_, Q, T_, wsn2))(FZ, TT)
        pc = ax.pcolormesh(FZ, TT, np.log10(Rm), shading="auto", cmap="viridis",
                            vmin=-12, vmax=4)
        ax.contour(FZ, TT, np.log10(Rm), levels=[0], colors="r", linewidths=1.6)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(r"$\omega_0/2\pi$ [Hz]")
        ax.set_title(f"$Q = 10^{{{int(np.log10(Q))}}}$")
    axs[0].set_ylabel("temperature [K]")
    for key, p in P.PLATFORMS.items():
        for ax in axs:
            ax.plot([p.w0 / (2 * np.pi)], [p.T], "w*", ms=10, mec="k", mew=0.7,
                    clip_on=False, zorder=5)
    fig.colorbar(pc, ax=axs, label=r"$\log_{10} R$  (red: $R=1$)", pad=0.02)
    fig.savefig(OUT_DIR / "realistic-2-resolvability.pdf")
    fig.savefig(OUT_DIR / "realistic-2-resolvability.png")
    plt.close(fig)

    # --------------------------------------- fig 3: the spectra, and the residual
    p = P.PLATFORMS["osmium-paul"]
    L_env = p.D_env / K.HBAR ** 2
    ss = {law: L.predict(law, p, 1e-3 * L_env, 0.0) for law in
          ("theory", "mc_sn", "uncond_sn", "qm")}
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(8.0, 3.2))
    w = np.linspace(p.w0 - 0.02, p.w0 + 0.02, 6000)
    styles = {"theory": ("-", 2.6, "C0"), "mc_sn": ("--", 1.8, "C1"),
              "qm": (":", 1.2, "C3"), "uncond_sn": ("-", 1.1, "C2")}
    for law, s_ in ss.items():
        ls, lw, c = styles[law]
        ax.semilogy(w - p.w0, L.spectrum(s_, w), ls, lw=lw, color=c, label=disp(law))
    ax.axvline(ss["theory"].w_q - p.w0, color="k", ls="-.", lw=0.7)
    ax.annotate(r"$\omega_q$", xy=(ss["theory"].w_q - p.w0, 2e-19), fontsize=8)
    ax.set_xlabel(r"$\omega - \omega_0$ [rad/s]")
    ax.set_ylabel(r"$S_{xx}$ [m$^2$/(rad/s)]")
    ax.set_title("this law, mc_sn and qm coincide")
    ax.legend(frameon=False, fontsize=8)

    wq = ss["theory"].w_q
    split = wq - p.w0
    u = np.logspace(-1, 5.4, 1400)
    w2 = p.w0 + u * split
    base = L.spectrum(ss["qm"], w2)
    for law, c in (("theory", "C0"), ("mc_sn", "C1")):
        bx.loglog(u, (L.spectrum(ss[law], w2) - base) / base, lw=1.5, color=c, label=disp(law))
    bx.axvline(1.0, color="k", ls="-.", lw=0.8)
    # Two annotations here used to collide: the first's text ran rightward far
    # enough (at this fontsize, over the plot's ~6 decades of x) to overlap the
    # second's rotated label. Fixed by keeping both short AND putting them in
    # Y-bands that do not overlap, so neither depends on guessing the other's
    # exact text width in data coordinates.
    bx.annotate(r"$\omega_q$:" "\n" "resolved peak", xy=(1.0, 3e-7),
                xytext=(4, 0), textcoords="offset points", fontsize=7,
                va="center")
    for law, c, y_lab in (("mc_sn", "C1", 1e-6), ("theory", "C0", 1e-6)):
        u_law = ss[law].G2 / split
        bx.axvline(u_law, color=c, ls=":", lw=1.0)
        bx.annotate(f"{disp(law)}'s own\nhalf width", xy=(u_law, y_lab), xytext=(5, 0),
                    textcoords="offset points", fontsize=6.5, color=c,
                    va="bottom", ha="left")
    bx.set_xlabel(r"offset above $\omega_0$, in units of the split")
    bx.set_ylabel("excess over qm, relative")
    bx.set_title("the excess is flat across the split")
    bx.legend(frameon=False, fontsize=8, loc="upper right")
    fig.savefig(OUT_DIR / "realistic-3-spectra.pdf")
    fig.savefig(OUT_DIR / "realistic-3-spectra.png")
    plt.close(fig)

    # ----------------------------------------------- fig 4: Q/T needed, by material
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    fz = np.logspace(-4, 2, 200)
    for mat in ("osmium", "tungsten", "gold", "silicon"):
        wsn2m = P.omega_sn_sq(P.MATERIALS[mat])
        ax.loglog(fz, 8 * (2 * np.pi * fz) * K.KB / (K.HBAR * wsn2m), label=mat)
    ax.set_xlabel(r"$\omega_0/2\pi$ [Hz]")
    ax.set_ylabel(r"$Q/T$ needed for $R=1$  [K$^{-1}$]")
    ax.axhline(1e10 / 1e-3, color="k", ls="--", lw=0.8)
    ax.annotate(r"$Q=10^{10}$ at 1 mK", xy=(1e-4, 1.4e13), fontsize=7)
    ax.set_title("what the record-broadened peak costs")
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(OUT_DIR / "realistic-4-feasibility.pdf")
    fig.savefig(OUT_DIR / "realistic-4-feasibility.png")
    plt.close(fig)

    # --------------------------------------- fig 5: resolvability vs mass, flat
    mi = D["stage3_map"]["mass_independence"]
    spread = mi["spread"]
    rbar = float(np.mean(mi["R"]))
    rel = (np.array(mi["R"]) - rbar) / rbar   # the only axis that can show this
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(8.2, 3.0))
    ax.semilogx(mi["masses"], mi["R"], "o-", color="C0")
    ax.set_xlabel("oscillator mass [kg]")
    ax.set_ylabel("resolvability $R$")
    ax.set_ylim(0, 1.6 * rbar)
    ax.set_title("flat by eye over fourteen orders")
    bx.semilogx(mi["masses"], rel, "o-", color="C3")
    bx.axhline(0, color="k", lw=0.6)
    bx.set_xlabel("oscillator mass [kg]")
    bx.set_ylabel(r"$(R - \bar R)/\bar R$")
    bx.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    bx.set_title("the residual: %.1e, floating-point noise" % spread)
    fig.suptitle("")
    fig.savefig(OUT_DIR / "realistic-5-mass-independence.pdf")
    fig.savefig(OUT_DIR / "realistic-5-mass-independence.png")
    plt.close(fig)

    # ------------------------------------------------- fig 6: the Q window
    boundary = D["stage3_map"]["boundary"]
    temps = (1e-3, 1e-2, 1e-1, 1.0)
    fig, ax = plt.subplots(figsize=(4.8, 3.4))
    for k, T in enumerate(temps):
        fzs, los, his = [], [], []
        for key, rows in boundary.items():
            fz = float(key[:-2])
            a, b = rows[k]
            if a is not None:
                fzs.append(fz)
                los.append(a)
                his.append(b)
        order = np.argsort(fzs)
        fzs = np.array(fzs)[order]
        los = np.array(los)[order]
        his = np.array(his)[order]
        if len(fzs) == 0:
            continue
        ax.fill_between(fzs, los, his, alpha=0.25, color=f"C{k}")
        ax.loglog(fzs, los, "-", color=f"C{k}", lw=1.3, label=f"T = {T:g} K")
        ax.loglog(fzs, his, "-", color=f"C{k}", lw=1.3)
    ax.set_xlabel(r"$\omega_0/2\pi$ [Hz]")
    ax.set_ylabel("$Q$")
    ax.set_title("the feasible window: a floor and a ceiling")
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(OUT_DIR / "realistic-6-q-window.pdf")
    fig.savefig(OUT_DIR / "realistic-6-q-window.png")
    plt.close(fig)

    print("six figures written to", OUT_DIR)


if __name__ == "__main__":
    main()
