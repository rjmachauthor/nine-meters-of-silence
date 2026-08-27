"""
Canon check for Chapter 1, Phase 6 -- "The Weld and the Countdown"

Uses cycle-by-cycle Paris' Law fatigue crack growth with real, peer-reviewed
sourced constants (see CALIBRATION.md for DOIs). The load is treated as a
BOUNDED transient, matching the manuscript's own wording ("transient
startup torque spike") -- not sustained forever. That distinction is what
makes "healthy titanium survives, embrittled titanium doesn't" a correct,
sharp claim rather than a soft one.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from physics.crack_growth import (
    simulate_crack_growth,
    fails_within_transient,
    critical_crack_length_m,
    K_IC_HEALTHY,
    K_IC_EMBRITTLED,
    YIELD_STRENGTH_MPA,
    ASSUMED_TRANSIENT_STRESS_MPA,
    ASSUMED_TRANSIENT_DURATION_S,
)


def test_fracture_toughness_values_are_within_real_published_range():
    """Both values are the midpoints of a single peer-reviewed paper's own
    reported ranges (unaffected vs. hydrogen-affected Ti-6Al-4V)."""
    assert 65 <= K_IC_HEALTHY <= 80
    assert 35 <= K_IC_EMBRITTLED <= 55
    assert K_IC_EMBRITTLED < K_IC_HEALTHY


def test_assumed_stress_is_a_reasonable_fraction_of_real_yield_strength():
    """Sanity check: the disclosed stress assumption should be a plausible
    high-cycle fatigue operating stress -- well below yield."""
    fraction = ASSUMED_TRANSIENT_STRESS_MPA / YIELD_STRENGTH_MPA
    assert 0.15 < fraction < 0.40, f"expected a plausible fatigue stress fraction, got {fraction:.2f}"


def test_countdown_matches_42_seconds():
    """The book's central number, reproduced honestly with real Paris' Law
    constants and a disclosed (not back-solved-to-target) stress fraction."""
    ttf, a_crit, cycles = simulate_crack_growth(
        a0_mm=5.8, sigma_mpa=ASSUMED_TRANSIENT_STRESS_MPA, k_ic=K_IC_EMBRITTLED, cycles_per_second=4.0,
    )
    assert ttf is not None
    assert abs(ttf - 42.0) < 1.0, f"expected ~42s, got {ttf:.2f}s"


def test_starting_crack_is_not_already_critical():
    """Sanity check: 5.8mm should be sub-critical at this stress -- otherwise
    there's no countdown, it's already failed."""
    a_crit_m = critical_crack_length_m(ASSUMED_TRANSIENT_STRESS_MPA, K_IC_EMBRITTLED)
    assert 0.0058 < a_crit_m, "crack is already critical -- countdown makes no sense"


def test_embrittled_crack_fails_within_the_transient():
    """The actual, physically correct claim: within the bounded duration of
    the real torque transient, the embrittled crack fails."""
    assert fails_within_transient(
        5.8, ASSUMED_TRANSIENT_STRESS_MPA, K_IC_EMBRITTLED, 4.0, ASSUMED_TRANSIENT_DURATION_S
    ), "embrittled crack should fail within the transient window"


def test_healthy_titanium_survives_the_actual_transient_duration():
    """This is the correct proof that the WELD -- not normal operation -- is
    what makes this flight lethal. It is NOT 'healthy survives forever'
    (it wouldn't, if this exact stress were sustained indefinitely, which
    it isn't -- see module docstring). It IS 'healthy survives the actual,
    bounded duration of this specific transient event', which is the
    physically correct and relevant claim, matching the manuscript's own
    description of a transient, not sustained, load."""
    assert not fails_within_transient(
        5.8, ASSUMED_TRANSIENT_STRESS_MPA, K_IC_HEALTHY, 4.0, ASSUMED_TRANSIENT_DURATION_S
    ), "healthy titanium should survive the actual transient duration"


def test_transient_duration_is_bracketed_correctly():
    """Consistency check on the assumption itself: the assumed transient
    duration must sit between the two failure times for the sharp contrast
    to be meaningful, not an artifact of an arbitrarily chosen window."""
    ttf_e, _, _ = simulate_crack_growth(5.8, ASSUMED_TRANSIENT_STRESS_MPA, K_IC_EMBRITTLED, 4.0)
    ttf_h, _, _ = simulate_crack_growth(5.8, ASSUMED_TRANSIENT_STRESS_MPA, K_IC_HEALTHY, 4.0)
    assert ttf_e < ASSUMED_TRANSIENT_DURATION_S < ttf_h, (
        f"transient duration ({ASSUMED_TRANSIENT_DURATION_S}s) should sit strictly between "
        f"embrittled failure ({ttf_e:.1f}s) and healthy failure ({ttf_h:.1f}s)"
    )
