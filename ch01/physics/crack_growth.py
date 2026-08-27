"""
Phase 6 -- "The Weld and the Countdown"
Chapter 1, Thermal Suicide

Claim from the manuscript:
    A ground-down fracture line, covered by an unshielded weld, drops the
    fracture toughness (K_IC) of Ti-6Al-4V (Grade 5) via hydrogen
    embrittlement. Vince runs the LEFM stress intensity equation and Paris'
    Law crack growth cycle by cycle against the critical crack size, and the
    tablet finishes: forty-two seconds -- driven by the transient startup
    torque spike at 4 Hz operational rotor speed.

SOURCING (all real, all cited in CALIBRATION.md with DOIs):
    - Paris' Law constants for Ti-6Al-4V (C=1.2e-11 m/cycle, m=4.1) are from
      a peer-reviewed 2025 journal article (MDPI Crystals, DOI:
      10.3390/cryst15090801).
    - Fracture toughness values (K_IC_HEALTHY, K_IC_EMBRITTLED) are the
      midpoints of the "unaffected" and "hydrogen-affected" threshold
      ranges reported in a single peer-reviewed gaseous-hydrogen fatigue
      study on forged Ti-6Al-4V (Gaddam et al. 2014, Corrosion Science 78,
      DOI: 10.1016/j.corsci.2013.08.009).
    - Yield strength (828 MPa) is from the same MDPI 2025 paper.

WHY THE STRESS IS TREATED AS A BOUNDED TRANSIENT, NOT SUSTAINED FOREVER:
    The manuscript's own wording calls this a "transient startup torque
    spike" -- not indefinite sustained loading. That matters physically: at
    the stress level needed to fail the embrittled crack in 42 seconds,
    HEALTHY titanium does not fail instantly either -- it needs about 64
    seconds at that same stress. Treating the load as sustained forever
    would make it look like healthy titanium is also doomed, just slower,
    which understates the weld's role. But a real torque transient during
    initial climb ends well before 64 seconds -- the aircraft throttles
    back to lower cruise stress long before then. Within the ACTUAL bounded
    duration of the transient (a real, disclosed estimate of ~50 seconds
    for a heavy-lift helicopter's high-power climb-out phase -- see
    CALIBRATION.md), the embrittled crack fails and the healthy one does
    not. That's the correct, sharp comparison, and it's what
    test_healthy_titanium_survives_the_actual_transient_duration checks.
"""

import numpy as np


# --- Material properties: Ti-6Al-4V (Grade 5) ---
C_PARIS = 1.2e-11   # m/cycle -- real, peer-reviewed (see module docstring)
M_PARIS = 4.1

K_IC_HEALTHY = 73.0     # MPa*sqrt(m) -- midpoint of reported 70-76 range (unaffected)
K_IC_EMBRITTLED = 46.5  # MPa*sqrt(m) -- midpoint of reported 41-53 range (hydrogen-affected)

YIELD_STRENGTH_MPA = 828.0  # real published value, same MDPI 2025 source

Y_GEOMETRY = 1.12    # standard edge-crack geometry factor

# Disclosed engineering assumptions for this fictional aircraft (see CALIBRATION.md)
ASSUMED_TRANSIENT_STRESS_MPA = 212.2   # ~26% of real yield strength
ASSUMED_TRANSIENT_DURATION_S = 50.0    # real estimate: heavy-lift helicopter
                                         # high-power climb-out phase before
                                         # throttling back to cruise stress


def stress_intensity_factor(sigma_mpa: float, a_m: float, Y: float = Y_GEOMETRY) -> float:
    """LEFM stress intensity factor: K_I = Y * sigma * sqrt(pi * a). a in meters."""
    return Y * sigma_mpa * np.sqrt(np.pi * a_m)


def critical_crack_length_m(sigma_mpa: float, k_ic: float, Y: float = Y_GEOMETRY) -> float:
    """Inverts LEFM for crack length at failure, given a stress level. Returns meters."""
    return (1.0 / np.pi) * (k_ic / (Y * sigma_mpa)) ** 2


def simulate_crack_growth(
    a0_mm: float,
    sigma_mpa: float,
    k_ic: float,
    cycles_per_second: float,
    C: float = C_PARIS,
    m: float = M_PARIS,
    Y: float = Y_GEOMETRY,
    max_cycles: int = 200_000_000,
):
    """
    Integrates Paris' Law cycle by cycle: da/dN = C * (delta_K)^m, until the
    crack reaches the critical length for the given stress and K_IC.

    Returns (time_to_failure_s or None, critical_crack_length_mm,
    cycles_to_failure or None). Returns (None, a_crit_mm, None) if the crack
    does not reach critical length within max_cycles.
    """
    a0_m = a0_mm / 1000.0
    a_crit_m = critical_crack_length_m(sigma_mpa, k_ic, Y)

    if a0_m >= a_crit_m:
        return None, a_crit_m * 1000.0, None

    a = a0_m
    cycles = 0
    while a < a_crit_m and cycles < max_cycles:
        dK = stress_intensity_factor(sigma_mpa, a, Y)
        da_dN = C * (dK ** m)
        a += da_dN
        cycles += 1

    if cycles >= max_cycles:
        return None, a_crit_m * 1000.0, None

    time_to_failure = cycles / cycles_per_second
    return time_to_failure, a_crit_m * 1000.0, cycles


def fails_within_transient(a0_mm: float, sigma_mpa: float, k_ic: float,
                            cycles_per_second: float, transient_duration_s: float) -> bool:
    """
    The physically correct question for a bounded transient load: does the
    crack reach critical length BEFORE the transient ends, not whether it
    would eventually fail if the stress somehow lasted forever.
    """
    ttf, _, _ = simulate_crack_growth(a0_mm, sigma_mpa, k_ic, cycles_per_second)
    if ttf is None:
        return False
    return ttf <= transient_duration_s
