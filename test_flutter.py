"""
Canon check for Chapter 1, Phase 1 -- "Gorge Entry: Flutter"
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from physics.flutter import healthy_natural_frequency_hz, soft_spot_natural_frequency_hz


def test_healthy_mast_natural_frequency_is_far_above_20hz():
    """Book claim: a healthy, rigid titanium structure has a natural
    frequency far above 20 Hz."""
    f_healthy = healthy_natural_frequency_hz()
    assert f_healthy > 100.0, f"expected healthy natural frequency far above 20Hz, got {f_healthy:.1f}Hz"


def test_local_soft_spot_brings_frequency_to_observed_20hz():
    """Book claim: a local soft spot (not a change to the material itself)
    drops the effective natural frequency into the observed 20 Hz range --
    matching the acoustic emission spike the team measures."""
    f_soft = soft_spot_natural_frequency_hz()
    assert 18.0 < f_soft < 22.0, f"expected soft-spot frequency near 20Hz, got {f_soft:.1f}Hz"


def test_soft_spot_is_a_large_stiffness_drop_not_a_small_one():
    """Consistency check: dropping natural frequency from >100Hz to ~20Hz
    requires a large stiffness reduction (frequency scales with sqrt(k)),
    consistent with the book's framing of a real structural flaw, not noise."""
    f_healthy = healthy_natural_frequency_hz()
    f_soft = soft_spot_natural_frequency_hz()
    ratio = (f_healthy / f_soft) ** 2  # stiffness ratio implied by frequency ratio
    assert ratio > 100, f"expected a large implied stiffness drop, got ratio={ratio:.1f}x"
