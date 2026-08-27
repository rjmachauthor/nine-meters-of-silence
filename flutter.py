"""
Phase 1 -- "Gorge Entry: Flutter"
Chapter 1, Thermal Suicide

Claim from the manuscript:
    High-frequency acoustic emission spike at 20 Hz from the tail
    section/rotor mast sensors. The structure is absorbing energy from the
    airstream instead of dissipating it -- aeroelastic flutter. A healthy,
    rigid titanium structure has a natural frequency far above 20 Hz. The
    line kept deliberately plain: "the mast's not behaving like solid
    titanium anymore -- like there's a soft spot" -- framed as effective
    stiffness / local compliance changing, not the material constant itself.

This is intentionally a light module: a single-degree-of-freedom natural
frequency calculation, not a full simulation. It checks that a healthy
mast's natural frequency really is far above 20 Hz, and that a physically
reasonable local stiffness loss (a "soft spot") can bring it down into the
observed range -- without claiming the material itself changed.
"""

import numpy as np


def natural_frequency_hz(stiffness_n_per_m: float, effective_mass_kg: float) -> float:
    """
    Simple 1-DOF natural frequency: f = (1/2*pi) * sqrt(k/m)
    """
    return (1 / (2 * np.pi)) * np.sqrt(stiffness_n_per_m / effective_mass_kg)


# --- Structural parameters (rotor mast, simplified as a 1-DOF beam mode) ---
EFFECTIVE_MASS_KG = 38.0            # effective modal mass of the mast section
HEALTHY_STIFFNESS_N_PER_M = 8.5e8    # a stiff titanium mast section
SOFT_SPOT_STIFFNESS_N_PER_M = 6.0e5  # local compliance from a hidden flaw -- NOT
                                       # a change to the material's stiffness
                                       # constant itself, just localized give


def healthy_natural_frequency_hz() -> float:
    return natural_frequency_hz(HEALTHY_STIFFNESS_N_PER_M, EFFECTIVE_MASS_KG)


def soft_spot_natural_frequency_hz() -> float:
    return natural_frequency_hz(SOFT_SPOT_STIFFNESS_N_PER_M, EFFECTIVE_MASS_KG)
