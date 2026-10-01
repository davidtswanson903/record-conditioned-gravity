"""The controls each experiment's decision rules required, asserted directly
rather than only implied by the equivalence tests. A reviewer can run just this
file (`pytest tests/test_controls.py -v`) to see every control named.
"""


# ------------------------------------------------------- the computational check
def test_sn_does_not_depend_on_eta(check_results):
    """Control (1): unconditional Schroedinger-Newton must not depend on eta."""
    vals = check_results["controls"]["sn_flat"]
    assert max(vals) - min(vals) < 1e-9


def test_quantized_coupling_generates_entanglement(check_results):
    """Control (2): the quantized interaction must generate entanglement in T8's
    setup, so the negativity measure is shown to see entanglement when there is
    any."""
    assert check_results["controls"]["quantized_max"] > 0.1


def test_outcome_sourced_law_differs_from_the_theory_in_T5(check_results):
    """Control (3): the outcome-sourced law must differ from the theory's when a
    record is unread, so 'read vs unread' is shown to be a real distinction the
    code can represent."""
    assert check_results["controls"]["outcome_spread"] > 0.1


def test_T4_passes_for_both_rules_so_no_signalling_does_not_discriminate(check_results):
    """T4's own verdict: the theory's law does not signal under either rule. This
    is why no signalling cannot be the criterion that selects between them (see
    LIMITS.md and docs/law.md)."""
    assert check_results["T4"]["worst_2d"] < 1e-12
    assert check_results["T4"]["worst_4d"] < 1e-12
    assert abs(check_results["T4"]["theory_i"]) < 1e-9
    assert abs(check_results["T4"]["theory_ii"]) < 1e-9
    assert abs(check_results["T4"]["outcome_x"] - check_results["T4"]["outcome_z"]) > 0.1


def test_T9_energy_drift_is_integrator_order(check_results):
    """No record configuration creates energy: the drift is the split-step
    integrator's own, and falls by ~4x when dt is quartered (first order)."""
    ratios = [t["rel"] / t["rel_quarter"] for t in check_results["T9"]]
    assert all(3.5 < r < 4.5 for r in ratios)


# --------------------------------------------------------- the realistic experiment
def test_observable_A_fails_its_own_control_for_a_physical_reason(realistic_results):
    """The raw PSD at the probe frequency moves under standard quantum mechanics
    when the ancilla is switched -- not because the code cannot tell the laws
    apart (see test_observable_B_passes below), but because the ancilla's own
    backaction heats the mass. This is the correction LIMITS.md and
    docs/realistic.md record, not a bug."""
    c = realistic_results["stage2_virtual"]["controls"]
    assert c["qm_lockin_raw"] > 0.5
    assert c["passes_on_observable_A"] is False


def test_observable_B_passes_every_control(realistic_results):
    c = realistic_results["stage2_virtual"]["controls"]
    assert c["qm_lockin_weight"] == 0.0
    assert c["uncond_sn_ancilla"] < 1e-9
    assert c["no_record_no_modulation"] == 0.0
    assert c["passes_on_observable_B"] is True


def test_the_five_laws_are_not_one_law(realistic_results):
    assert realistic_results["stage2_virtual"]["controls"]["law_spread"] > 0.5


def test_f_is_nonzero_only_below_the_ground_state_occupation(realistic_results):
    """f (the law's weight on the unconditioned density) is nonzero only where
    the oscillator's own purity exceeds 1/2, i.e. nbar < 1/2 -- forced by
    eta_eff = sqrt(2 Tr rho^2 - 1) with Tr rho^2 = 1/(2 nbar + 1)."""
    plats = realistic_results["stage1_platforms"]["baseline"]
    assert plats["osmium-paul"]["nbar"] > 0.5 and plats["osmium-paul"]["f"] == 0.0
    assert plats["torsion-mg"]["nbar"] > 0.5 and plats["torsion-mg"]["f"] == 0.0
    assert plats["levitated-gs"]["nbar"] < 0.5 and plats["levitated-gs"]["f"] > 0.0


def test_no_platform_meets_all_three_feasibility_conditions(realistic_results):
    """The central negative result: on every real platform considered, the
    resolvability gate fails, by four to eight orders."""
    for key, row in realistic_results["stage3_map"]["platforms_gate"].items():
        assert row["ok"] is False, key
        assert row["gate"] is False, key


def test_a_feasible_corner_exists_beyond_current_technology(realistic_results):
    """stage 3's corner (1 mHz, Q=1e12, 1 mK) DOES meet all three conditions --
    the protocol is not impossible in principle, only far beyond any built
    oscillator (see docs/minimum-time.md)."""
    assert realistic_results["stage3_map"]["corner"]["ok"] is True


def test_the_extrapolation_survives_a_second_reading(realistic_results):
    """stage 4's first challenge: f=0 on a thermal oscillator, read through
    coherence at the lattice scale rather than through purity, agrees with the
    purity reading on both hot platforms -- the conclusion does not rest on the
    adapter's one extrapolation (LIMITS.md)."""
    sr = realistic_results["stage4_robust"]["second_reading"]
    assert sr["osmium-paul"]["agree"] is True
    assert sr["torsion-mg"]["agree"] is True


def test_the_wall_does_not_transfer_to_measurement_conditioned_proposals(realistic_results):
    """stage 4's third challenge: the measurement-conditioned law clears the
    imprecision floor where the theory never does, on the same platform."""
    w = realistic_results["stage4_robust"]["walls"]["osmium-paul"]
    assert w["theory"]["cleared"] is False
    assert w["mc_sn"]["cleared"] is True
