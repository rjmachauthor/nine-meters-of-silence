"""
Canon check for Chapter 1, Phase 2 -- "False Lead #1: The Sensor Ghost"
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from physics.sensor_ghost import (
    generate_healthy_sensor_scenario,
    generate_broken_sensor_scenario,
    mean_nis_after,
)


def test_healthy_sensor_residual_stays_near_expected_baseline():
    """Book claim: the residuals are flat -- even during the dramatic real
    flutter event, a correctly-tuned filter's NIS should sit close to its
    textbook expected value of 1 (chi-squared, 1 degree of freedom), not
    blown out just because the underlying signal looks dramatic."""
    healthy = generate_healthy_sensor_scenario()
    overall_nis = mean_nis_after(healthy, 0.0)
    assert 0.5 < overall_nis < 2.0, f"expected NIS near 1 (flat/healthy), got {overall_nis:.2f}"


def test_broken_sensor_residual_rises_after_fault_onset():
    """Book claim: if the sensor were broken, the residual should blow up.
    A sudden bias fault -- a real, instant-onset IMU failure mode, and a
    closer physical match to the manuscript's 'sudden, massive phase shift'
    than gradual drift -- should produce a residual that rises well past
    the flat baseline once the fault occurs."""
    broken = generate_broken_sensor_scenario()
    before_mask = broken["time"] < 5.0
    before_nis = float(np.mean(broken["nis"][before_mask]))
    after_nis = mean_nis_after(broken, 6.0)

    assert after_nis > 3.0, f"expected NIS to clearly rise after the fault, got {after_nis:.2f}"
    assert after_nis > before_nis * 2, (
        f"expected NIS after fault onset to be much higher than before it "
        f"(before={before_nis:.2f}, after={after_nis:.2f})"
    )


def test_broken_sensor_nis_stays_elevated_not_a_one_time_blip():
    """The fault should produce a SUSTAINED elevation, not a brief spike --
    a real bias fault persists once it occurs."""
    broken = generate_broken_sensor_scenario()
    t = broken["time"]
    nis = broken["nis"]
    just_after = float(np.mean(nis[(t >= 5.0) & (t < 5.5)]))
    much_later = float(np.mean(nis[(t >= 9.0) & (t < 10.0)]))
    assert much_later > 2.0, f"expected NIS to remain elevated late in the fault window, got {much_later:.2f}"
    assert just_after > 1.5, f"expected NIS to rise promptly after fault onset, got {just_after:.2f}"


def test_same_flutter_amplitude_does_not_by_itself_trigger_the_broken_reading():
    """Consistency check: the healthy scenario has the SAME large flutter
    disturbance as the broken scenario's pre-fault period. If big real
    motion alone triggered a false 'broken sensor' reading, that would
    defeat the whole point of the diagnostic."""
    healthy = generate_healthy_sensor_scenario()
    healthy_flutter_nis = mean_nis_after(healthy, 5.0)
    assert healthy_flutter_nis < 3.0, (
        f"a real, large disturbance alone should not trigger a 'broken "
        f"sensor'-level residual, got {healthy_flutter_nis:.2f}"
    )


def test_fault_magnitude_is_realistic_for_a_bias_fault_not_drift():
    """Sanity check on realism: classic gyro drift accumulates on the order
    of 0.01-10 degrees PER HOUR (real published tactical/nav-grade specs) --
    far too slow to matter within a several-second event. This module
    intentionally models a sudden BIAS STEP instead, which is a real,
    documented, instant-onset IMU failure mode. This test just confirms the
    fault is implemented as an instantaneous step, not a slow ramp."""
    broken = generate_broken_sensor_scenario(bias_magnitude_rad=0.2, fault_onset_s=5.0)
    t = broken["time"]
    # measured minus true should jump close to the full bias magnitude
    # almost immediately after onset, not ramp up gradually
    idx_just_after = np.searchsorted(t, 5.01)
    offset_immediately_after = broken["measured"][idx_just_after] - broken["true"][idx_just_after]
    assert abs(offset_immediately_after - 0.2) < 0.05, (
        f"expected the bias to appear as an immediate step (~0.2 rad), "
        f"got {offset_immediately_after:.3f} rad just after onset"
    )
