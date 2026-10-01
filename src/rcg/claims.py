"""The claims registry: one row per claim this repository makes, each with its
evidence, the script and output key that produce it, and its status. CLAIMS.md is
generated from this list; nothing is added to CLAIMS.md that is not added here.

`status` is one of:
    confirmed    -- checked by exact simulation, in this repository
    imported     -- taken from the literature, with an adapter stated
    cited        -- a fact about the literature, not computed here
    open         -- not established; see LIMITS.md
"""

CLAIMS = [
    dict(
        claim="The law's own weight f(eta) has the closed form eta (rule i) or "
              "1-sqrt(1-eta^2) (rule ii), with f(0)=0 and f(1)=1.",
        evidence="T1 (endpoints) and the closed forms in rcg.law",
        script="experiments/check/run.py",
        key="T1, T2",
        status="confirmed",
    ),
    dict(
        claim="Regenerating the originating theory's own stored calibration numbers "
              "from its own model reproduces them to 5e-5.",
        evidence="pilot_calibration",
        script="experiments/check/run.py",
        key="pilot_calibration",
        status="confirmed",
    ),
    dict(
        claim="Two independent records at overlaps eta1, eta2 are read by the law as "
              "one record at overlap eta1*eta2.",
        evidence="T3 (composition), exact to 5.6e-17",
        script="experiments/check/run.py",
        key="T3.overlap",
        status="confirmed",
    ),
    dict(
        claim="Rule (i)'s f is exactly multiplicative under composition "
              "(f(eta1)f(eta2) = f(eta1 eta2)); rule (ii)'s is not, and misses by an "
              "amount this repository quotes as a single, absolute figure wherever it "
              "is stated numerically (see docs/law.md), not interchangeably as a "
              "relative one.",
        evidence="T3 (multiplicativity) -- the one test that separates the two rules",
        script="experiments/check/run.py",
        key="T3.multiplicative",
        status="confirmed",
    ),
    dict(
        claim="The law does not signal: no local operation on a record moves the "
              "source, under either rule.",
        evidence="T4, to 2.2e-16 under 20 random unitaries on 2- and 4-dimensional "
                 "registers",
        script="experiments/check/run.py",
        key="T4",
        status="confirmed",
    ),
    dict(
        claim="No signalling does NOT distinguish the two rules: both pass T4 equally, "
              "so it cannot be the criterion that selects between them.",
        evidence="T4 passes for both rule_i and rule_ii",
        script="experiments/check/run.py",
        key="T4.theory_i, T4.theory_ii",
        status="confirmed",
    ),
    dict(
        claim="An unread record counts the same as a read one; a coherently erased "
              "record restores the unconditioned source; ordinary decoherence is "
              "indistinguishable from a deliberate register.",
        evidence="T5, T6, T7",
        script="experiments/check/run.py",
        key="T5, T6, T7",
        status="confirmed",
    ),
    dict(
        claim="Two unrecorded masses develop zero entanglement under the law's "
              "mean-field form, while a quantized two-body coupling in the same code "
              "reaches 0.53 concurrence -- the code can see entanglement when there is "
              "any.",
        evidence="T8",
        script="experiments/check/run.py",
        key="T8",
        status="confirmed",
    ),
    dict(
        claim="The law's mean-field dynamics adds no noise: it is a deterministic "
              "function of the initial state, with no stochastic term anywhere in its "
              "construction (unlike a genuine classical channel, which needs one to "
              "avoid signalling).",
        evidence="two independent runs of the two-mass dynamics from the same initial "
                 "state agree bit for bit, confirming no randomness is injected",
        script="tests/test_law.py",
        key="test_the_law_adds_no_noise",
        status="confirmed",
    ),
    dict(
        claim="No record configuration creates energy; the residual drift is the "
              "integrator's own (first order in the time step).",
        evidence="T9, worst drift 3.0e-4, falls by 4.03x at dt/4",
        script="experiments/check/run.py",
        key="T9",
        status="confirmed",
    ),
    dict(
        claim="The continuously-recorded-oscillator adapter reduces exactly to the "
              "two-branch law in the two-branch limit.",
        evidence="eta_eff_check, f_reduction_check",
        script="experiments/realistic/stage0_adapter.py",
        key="eta_eff_check, f_reduction_check",
        status="confirmed",
    ),
    dict(
        claim="The Gaussian filter reproduces both of its required limits: "
              "equipartition when unconditioned, the ground state when fully "
              "conditioned.",
        evidence="filter_check",
        script="experiments/realistic/stage0_adapter.py",
        key="filter_check",
        status="confirmed",
    ),
    dict(
        claim="The record weight f is nonzero only where the oscillator's own "
              "thermal occupation is below one half -- forced by eta_eff = "
              "sqrt(2 Tr rho^2 - 1), not a modelling choice.",
        evidence="baseline, all three platforms",
        script="experiments/realistic/stage1_platforms.py",
        key="baseline",
        status="confirmed",
    ),
    dict(
        claim="On every real platform considered, the second record-conditioned "
              "resonance is four to eight orders broader than its own offset from the "
              "main line: a shape failure, not a noise one.",
        evidence="resolvability",
        script="experiments/realistic/stage1_platforms.py",
        key="resolvability",
        status="confirmed",
    ),
    dict(
        claim="The naive lock-in observable (the raw spectrum at the probe frequency) "
              "fails its own control: it moves under standard quantum "
              "mechanics too, because the ancilla's backaction heats the mass.",
        evidence="controls.qm_lockin_raw",
        script="experiments/realistic/stage2_virtual.py",
        key="controls",
        status="confirmed",
    ),
    dict(
        claim="The second peak's weight (rather than the raw spectrum) is a "
              "heating-nulled observable that passes every control.",
        evidence="controls.qm_lockin_weight, uncond_sn_ancilla, no_record_no_modulation",
        script="experiments/realistic/stage2_virtual.py",
        key="controls",
        status="confirmed",
    ),
    dict(
        claim="The resolvability R does not depend on the oscillator's mass, over "
              "fourteen orders of magnitude.",
        evidence="mass_independence, spread 9.5e-15",
        script="experiments/realistic/stage3_map.py",
        key="mass_independence",
        status="confirmed",
    ),
    dict(
        claim="A feasible region exists (all three of stage 3's conditions met) at "
              "1 mHz, Q=1e12, 1 mK -- but it is a window, not a threshold: pushing Q "
              "higher eventually hurts.",
        evidence="corner, boundary",
        script="experiments/realistic/stage3_map.py",
        key="corner, boundary",
        status="confirmed",
    ),
    dict(
        claim="The crystal-regime self-gravity formula applies to this law's own "
              "conditioned source on all three platforms, but not to the unconditional "
              "rival's unconditioned source on the two hot ones.",
        evidence="alpha",
        script="experiments/realistic/stage3_map.py",
        key="alpha",
        status="confirmed",
    ),
    dict(
        claim="The f=0-on-a-thermal-oscillator conclusion survives an independent "
              "second reading (coherence at the material's lattice scale, sharing no "
              "algebra with the purity-based reading).",
        evidence="second_reading, agree=true on both hot platforms",
        script="experiments/realistic/stage4_robust.py",
        key="second_reading",
        status="confirmed",
    ),
    dict(
        claim="Unconditional Schroedinger-Newton is NOT excluded by experiment: the "
              "most sensitive published torsion-balance test reports no evidence "
              "either way.",
        evidence="[Y25]: 0.3 microrad/rtHz at 2.5 mHz, three months, no exclusion "
                 "claimed",
        script="data/references.yaml",
        key="Y25",
        status="cited",
    ),
    dict(
        claim="The record-broadening wall that defeats this law's own protocol "
              "does NOT transfer to the measurement-conditioned rival, which beats it "
              "by a factor of (2 nbar + 1).",
        evidence="walls",
        script="experiments/realistic/stage4_robust.py",
        key="walls",
        status="confirmed",
    ),
    dict(
        claim="A weaker, field-wide bound DOES transfer: any spectroscopic test of a "
              "conditioned second peak needs at least pi*Q/omega_0, independent of "
              "this law -- and this matches, to the right order, the run time a "
              "real torsion-balance experiment reports needing. This is a special, "
              "law-independent case of an ALREADY PUBLISHED family of such bounds "
              "([Helou2017]), not a new one -- see docs/minimum-time.md.",
        evidence="tmin, checked against [Y25]'s reported 300+ days; [Helou2017] eq. "
                 "120-121 for the published scaling law this specializes",
        script="experiments/realistic/stage4_robust.py",
        key="tmin",
        status="confirmed",
    ),
    dict(
        claim="The crystal-regime self-gravity frequency (omega_SN) and the "
              "oscillator-frequency-shift formula that uses it are imported from the "
              "literature, not derived from the sourcing law.",
        evidence="data/platforms.yaml; rcg.law.omega_sn_sq_from_shift's docstring",
        script="src/rcg/law.py",
        key="omega_sn_sq_from_shift",
        status="imported",
    ),
    dict(
        claim="The adapter's reduction of the sourcing law to a state of rank above "
              "two (a thermal oscillator) is an extrapolation past where the law is "
              "stated for two branches.",
        evidence="see stage4_robust's second reading for why the conclusion does not "
                 "depend on it",
        script="src/rcg/models/gaussian.py",
        key="(module docstring)",
        status="open",
    ),
]
