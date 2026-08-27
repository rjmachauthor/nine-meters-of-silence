"""
Canon check for Chapter 1, Phase 3 -- "False Lead #2: The Sloshing Mass"
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from physics.sloshing_mass import total_cable_tension_kn


def test_baseline_tension_matches_book():
    """Book claim: cable tension baseline of 38.2 kN at the swing's 30-degree apex."""
    result = total_cable_tension_kn()
    assert abs(result["baseline_kn"] - 38.2) < 0.5, f"expected ~38.2kN baseline, got {result['baseline_kn']:.2f}kN"


def test_peak_tension_matches_book():
    """Book claim: tension spikes to 45 kN from the internal shifting mass."""
    result = total_cable_tension_kn()
    assert abs(result["peak_kn"] - 45.0) < 0.5, f"expected ~45kN peak, got {result['peak_kn']:.2f}kN"


def test_peak_exceeds_baseline_by_a_real_margin():
    """Consistency check: the internal mass shift should meaningfully add to
    tension, not just be noise around the baseline."""
    result = total_cable_tension_kn()
    delta = result["peak_kn"] - result["baseline_kn"]
    assert delta > 5.0, f"expected the internal mass shift to add several kN, got {delta:.2f}kN"


def test_no_internal_shift_means_no_spike():
    """Sanity check: if nothing shifts inside the load, tension should stay
    at baseline -- the spike is caused by the shifting mass, not by the
    swing angle alone."""
    from physics.sloshing_mass import pendulum_baseline_tension_n, TOTAL_LOAD_MASS_KG, SWING_ANGLE_APEX_DEG
    baseline_only = pendulum_baseline_tension_n(TOTAL_LOAD_MASS_KG, SWING_ANGLE_APEX_DEG) / 1000.0
    result = total_cable_tension_kn(shifting_mass_kg=0.0)
    assert abs(result["peak_kn"] - baseline_only) < 0.5, (
        "with zero shifting mass, peak tension should equal the static baseline"
    )
