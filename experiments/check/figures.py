"""The computational check's four figures, from results/check.json alone.

Nothing here is drawn by hand: every point is read from the json rcg's
experiments/check/run.py wrote.
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402
import numpy as np                                                 # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "check.json"
OUT_DIR = ROOT / "build" / "figures"


def main():
    with open(RESULTS) as fh:
        D = json.load(fh)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
         "figure.dpi": 140, "savefig.bbox": "tight"}
    )

    # ------------------------------------------------------------- fig 1: f(eta)
    c = D["T2"]
    eta = np.array([r["eta"] for r in c])
    d1 = D["T1"]["rule_i_1"]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ax[0].plot(eta, [r["f_i"] for r in c], "o-", label=r"rule (i): $f=\eta$")
    ax[0].plot(eta, [r["f_ii"] for r in c], "s-", label=r"rule (ii): $f=1-\sqrt{1-\eta^2}$")
    ax[0].set_xlabel(r"record overlap $\eta$")
    ax[0].set_ylabel(r"$f(\eta)$, the law's weight on the other branch")
    ax[0].legend(frameon=False)
    ax[0].set_title("the law, in closed form")
    ax[1].plot(eta, [r["drift_i"] / d1 for r in c], "o-", label="rule (i), measured")
    ax[1].plot(eta, [r["f_i"] for r in c], "k--", lw=0.8, label=r"$f_i(\eta)$")
    ax[1].plot(eta, [r["drift_ii"] / d1 for r in c], "s-", label="rule (ii), measured")
    ax[1].plot(eta, [r["f_ii"] for r in c], "k:", lw=0.8, label=r"$f_{ii}(\eta)$")
    ax[1].set_xlabel(r"record overlap $\eta$")
    ax[1].set_ylabel(r"drift / drift at $\eta=1$")
    ax[1].legend(frameon=False, fontsize=7)
    ax[1].set_title("the exact grid model's reading of it")
    fig.savefig(OUT_DIR / "check-1-f-eta.pdf")
    fig.savefig(OUT_DIR / "check-1-f-eta.png")
    plt.close(fig)

    # ------------------------------------------------------- fig 2: no signalling
    t4 = D["T4"]
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    labels = ["law,\nrule (i)", "law,\nrule (ii)", "outcome-sourced,\n$z$ basis",
              "outcome-sourced,\n$x$ basis"]
    vals = [t4["theory_i"], t4["theory_ii"], t4["outcome_z"], t4["outcome_x"]]
    cols = ["C0", "C0", "C3", "C3"]
    ax.bar(range(4), vals, color=cols)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("drift, perfect record")
    ax.set_title("a distant party's choice of basis")
    ax.set_ylim(0, max(vals) * 1.3)
    ax.annotate("identical", xy=(0.5, max(vals) * 0.10), ha="center", fontsize=8, color="C0")
    ax.annotate(
        "differ by %.3f" % abs(t4["outcome_x"] - t4["outcome_z"]),
        xy=(2.5, max(vals) * 1.12), ha="center", fontsize=8, color="C3",
    )
    fig.savefig(OUT_DIR / "check-2-no-signalling.pdf")
    fig.savefig(OUT_DIR / "check-2-no-signalling.png")
    plt.close(fig)

    # -------------------------------------------------- fig 3: the discriminators
    disc = D["discriminators"]
    rows = [r"record held" "\n" r"(unread), $\eta=0.5$",
            "the same record,\ncoherently erased",
            r"environment," "\n" r"no register, $\eta=0.5$"]
    series = [("rule (i)", "theory_i", "C0"), ("rule (ii)", "theory_ii", "C9"),
              ("Schrödinger–Newton", "sn", "C1"), ("outcome-conditioned", "outcome", "C3"),
              ("quantized gravity", "quant", "C7")]
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    w = 0.16
    xs = np.arange(len(disc))
    for k, (label, key, col) in enumerate(series):
        off = (k - (len(series) - 1) / 2) * w
        ax.bar(xs + off, [r[key] for r in disc], w, label=label, color=col)
    ax.set_xticks(xs)
    ax.set_xticklabels(rows, fontsize=8)
    ax.set_ylabel("pull between branches, relative to no record")
    ax.legend(frameon=False, fontsize=7, ncol=2)
    ax.set_ylim(-0.05, 1.35)
    ax.set_title("only this law's bars move when the record is erased")
    fig.savefig(OUT_DIR / "check-3-discriminators.pdf")
    fig.savefig(OUT_DIR / "check-3-discriminators.png")
    plt.close(fig)

    # ----------------------------------------------------------- fig 4: two masses
    th, qu = D["T8"]["theory"], D["T8"]["quantized"]
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    t = [r["t"] for r in qu]
    ax.plot(t, [r["negativity"] for r in qu], "o-", color="C3", label="quantized coupling")
    ax.plot(t, [r["negativity"] for r in th], "s-", color="C0", label="this law")
    ax.set_xlabel("time")
    ax.set_ylabel("negativity")
    ax.set_title("two unrecorded masses")
    ax.legend(frameon=False)
    ax.set_ylim(-0.02, 0.30)
    fig.savefig(OUT_DIR / "check-4-two-mass.pdf")
    fig.savefig(OUT_DIR / "check-4-two-mass.png")
    plt.close(fig)

    print("four figures written to", OUT_DIR)


if __name__ == "__main__":
    main()
