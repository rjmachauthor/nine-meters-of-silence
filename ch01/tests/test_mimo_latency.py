"""
Canon check for Chapter 1, Phase 4 -- "MIMO Latency Loop"
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from physics.mimo_latency import (
    simulate_roll_cargo_system,
    growth_rate,
    is_stable,
    cross_coupling_term,
)


def test_coupling_term_is_negative():
    """Book claim: the cross-coupling term is -mgh/I_xx -- cargo swing angle
    should produce a rolling moment in the opposite sense (negative sign)."""
    assert cross_coupling_term() < 0


def test_zero_delay_is_stable():
    """With no control delay, the system should settle -- this is the
    baseline that proves the delay itself is the actual cause of failure,
    not the coupling or the cargo swing on their own."""
    r = simulate_roll_cargo_system(delay_s=0.0, duration_s=20.0)
    gr = growth_rate(r["phi"], r["time"])
    assert gr < 0.05, f"expected near-zero or negative growth rate at 0s delay, got {gr:.3f}/s"
    assert is_stable(r["phi"]), "system should settle with no control delay"


def test_book_stated_delay_causes_runaway_instability():
    """Book claim: a 0.2-second micro-latency turns the control loop into a
    positive feedback energy pump -- pilot-induced oscillation with no pilot."""
    r = simulate_roll_cargo_system(delay_s=0.2, duration_s=20.0)
    gr = growth_rate(r["phi"], r["time"])
    assert gr > 0.3, f"expected strong positive (diverging) growth rate at 0.2s delay, got {gr:.3f}/s"
    assert not is_stable(r["phi"]), "system should NOT settle with the book's stated 0.2s delay"


def test_instability_is_a_delay_effect_not_a_coincidence():
    """Consistency check: growth rate should increase monotonically (or close
    to it) as delay increases -- this is what makes it a real delay-induced
    instability rather than a fluke at one specific number."""
    delays = [0.0, 0.1, 0.2, 0.3]
    rates = []
    for d in delays:
        r = simulate_roll_cargo_system(delay_s=d, duration_s=20.0)
        rates.append(growth_rate(r["phi"], r["time"]))
    # allow the very first step (0 -> 0.1) to be the biggest jump, but overall
    # trend should be increasing
    assert rates[-1] > rates[0], "growth rate should be higher at large delay than at zero delay"
    assert all(rates[i + 1] >= rates[i] - 0.05 for i in range(len(rates) - 1)), (
        f"growth rate should trend upward with delay, got {rates}"
    )
