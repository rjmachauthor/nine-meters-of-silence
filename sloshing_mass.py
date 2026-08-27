"""
Phase 3 -- "False Lead #2: The Sloshing Mass"
Chapter 1, Thermal Suicide

Claim from the manuscript:
    An unrestrained doctor moving inside the suspended crate shifts the
    load's center of gravity by roughly 30cm as she lunges to secure the
    medical dummy, creating an internal coupled mass-spring-damper effect on
    top of the pendulum's own swing (a fuel-slosh analogy). Cable tension
    spikes from a baseline of 38.2 kN to 45 kN at the swing's 30-degree
    apex, driven by the kinetic impact of the internal shifting mass.

This is a light module: a pendulum's baseline tension at a given swing
angle, plus an added impulsive tension term from a mass shifting inside the
load, calibrated to reproduce the manuscript's two stated tension values.
"""

import numpy as np

G = 9.81

TOTAL_LOAD_MASS_KG = 4500.0     # effective mass of the full suspended system --
                                  # crate, medical rig, structural housing, and
                                  # equipment for field surgery, not just one
                                  # person -- back-solved to match the book's
                                  # stated 38.2 kN baseline; see CALIBRATION.md
CABLE_LENGTH_M = 12.0
SWING_ANGLE_APEX_DEG = 30.0
INTERNAL_SHIFT_M = 0.30         # the doctor's ~30cm lunge, as stated in the book


def pendulum_baseline_tension_n(mass_kg: float, angle_deg: float) -> float:
    """
    Baseline cable tension for a simple pendulum at a given swing angle:
    T = m * g * cos(angle)   (centripetal term omitted for a quasi-static
    apex estimate, where angular velocity is momentarily zero)
    plus a small centripetal correction is not needed exactly at the apex.
    """
    angle_rad = np.radians(angle_deg)
    return mass_kg * G * np.cos(angle_rad)


def internal_mass_impact_tension_n(shifting_mass_kg: float, shift_distance_m: float,
                                    shift_duration_s: float) -> float:
    """
    Extra impulsive tension from an internal mass changing position quickly
    inside the load: treats the shift as a roughly constant deceleration
    over `shift_duration_s`, producing an additional force the cable must
    carry on top of the static/quasi-static baseline.

    F_impulse = m * (2 * shift_distance / shift_duration^2)
    (from d = 1/2 * a * t^2, solved for a, then F = m*a)
    """
    a = 2 * shift_distance_m / (shift_duration_s ** 2)
    return shifting_mass_kg * a


def total_cable_tension_kn(shifting_mass_kg: float = 75.0, shift_duration_s: float = 0.0813) -> dict:
    """
    Returns baseline and peak tension in kN, given a mass (e.g. the doctor,
    ~75kg) shifting INTERNAL_SHIFT_M within shift_duration_s.
    """
    baseline_n = pendulum_baseline_tension_n(TOTAL_LOAD_MASS_KG, SWING_ANGLE_APEX_DEG)
    impulse_n = internal_mass_impact_tension_n(shifting_mass_kg, INTERNAL_SHIFT_M, shift_duration_s)
    peak_n = baseline_n + impulse_n
    return {
        "baseline_kn": baseline_n / 1000.0,
        "peak_kn": peak_n / 1000.0,
    }
