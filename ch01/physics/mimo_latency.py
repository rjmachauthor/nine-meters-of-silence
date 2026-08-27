"""
Phase 4 -- "The Real Culprit: MIMO Latency Loop"
Chapter 1, Thermal Suicide

Claim from the manuscript:
    The helicopter's roll rate isn't just reacting to the suspended cargo --
    it's actively driving it. A software patch introduced a 0.2-second
    micro-latency into the flight computer's control loop. Because of the
    delay, the system executes a positive feedback loop -- pilot-induced
    oscillation with no pilot, the code fighting its own airframe.

This module implements a simplified coupled system: a suspended cargo mass
swinging like a pendulum below the helicopter, coupled to the helicopter's
roll dynamics via the cross-coupling term the manuscript names directly:
(-mgh/I_xx), which governs how much cargo angle (theta) drives a rolling
moment (phi_ddot) on the helicopter's center of mass.

The control law is a simple proportional roll-correction controller. The
delay is modeled directly and explicitly -- the controller acts on a
measurement of roll angle taken `tau` seconds in the past, implemented with
a real time-history buffer rather than a frequency-domain approximation.

No governing equation here is fictional: coupled pendulum-on-a-moving-
support dynamics and delayed proportional feedback destabilizing an
otherwise stable control loop are both textbook control theory. What's
chosen for this specific scenario are the physical constants (mass, cable
length, control gain) -- picked to be physically reasonable for a
helicopter-slung load, and disclosed in CALIBRATION.md.
"""

import numpy as np
from collections import deque


# --- Physical constants (helicopter + suspended cargo) ---
CARGO_MASS_KG = 450.0        # doctor + mannequin + crate, roughly
CABLE_LENGTH_M = 12.0         # length of the sling cable
HOOK_HEIGHT_M = 1.2           # h: vertical offset of hook below aircraft CG
I_XX_KG_M2 = 3800.0           # helicopter roll moment of inertia (typical medium helo)
G = 9.81

CONTROL_GAIN_KP = 10.0        # proportional roll-correction gain
CONTROL_GAIN_KD = 0.5         # rate-damping gain -- real flight control laws
                                # always include rate feedback, not pure
                                # proportional control, since a rigid body
                                # under pure-P delayed feedback is only ever
                                # marginally stable even with zero delay
CRITICAL_DELAY_S = 0.2        # the manuscript's stated latency


def cross_coupling_term(m=CARGO_MASS_KG, h=HOOK_HEIGHT_M, i_xx=I_XX_KG_M2):
    """The manuscript's named coupling coefficient: -mgh/I_xx"""
    return -(m * G * h) / i_xx


def simulate_roll_cargo_system(
    delay_s: float,
    duration_s: float = 15.0,
    dt: float = 0.005,
    theta0_rad: float = 0.05,   # small initial cargo swing disturbance
    kp: float = CONTROL_GAIN_KP,
    kd: float = CONTROL_GAIN_KD,
    m: float = CARGO_MASS_KG,
    h: float = HOOK_HEIGHT_M,
    i_xx: float = I_XX_KG_M2,
    cable_length: float = CABLE_LENGTH_M,
):
    """
    Integrate the coupled roll/cargo-swing system under delayed PD feedback
    control.

    State: phi (helicopter roll angle), phi_dot, theta (cargo swing angle),
    theta_dot.

    phi_ddot = coupling_term * theta - kp * phi(t - delay_s) - kd * phi_dot(t - delay_s)
    theta_ddot = -(g/L) * theta - phi_ddot

    The control law only ever sees a delayed measurement of phi and phi_dot --
    this is the direct mechanism of the manuscript's claim: a control system
    reacting to where the aircraft *was*, not where it *is*.

    Returns dict with time array, phi array, theta array.
    """
    n_steps = int(duration_s / dt)
    coupling = cross_coupling_term(m, h, i_xx)

    phi = 0.0
    phi_dot = 0.0
    theta = theta0_rad
    theta_dot = 0.0

    delay_steps = max(1, int(round(delay_s / dt))) if delay_s > 0 else 0
    phi_history = deque([0.0] * (delay_steps + 1), maxlen=delay_steps + 1)
    phi_dot_history = deque([0.0] * (delay_steps + 1), maxlen=delay_steps + 1)

    times = np.zeros(n_steps)
    phis = np.zeros(n_steps)
    thetas = np.zeros(n_steps)

    for i in range(n_steps):
        times[i] = i * dt
        phis[i] = phi
        thetas[i] = theta

        if delay_steps > 0:
            phi_delayed = phi_history[0]
            phi_dot_delayed = phi_dot_history[0]
        else:
            phi_delayed = phi
            phi_dot_delayed = phi_dot

        phi_ddot = coupling * theta - kp * phi_delayed - kd * phi_dot_delayed
        theta_ddot = -(G / cable_length) * theta - phi_ddot

        # simple explicit Euler integration -- adequate at this dt for a
        # demonstrative simulation of a qualitative stability boundary
        phi_dot += phi_ddot * dt
        phi += phi_dot * dt
        theta_dot += theta_ddot * dt
        theta += theta_dot * dt

        phi_history.append(phi)
        phi_dot_history.append(phi_dot)

    return {"time": times, "phi": phis, "theta": thetas}


def is_stable(phi_array: np.ndarray, tail_fraction: float = 0.3, threshold_rad: float = 0.05) -> bool:
    """
    Simple stability check: look at the last `tail_fraction` of the roll
    angle time history. If the amplitude there is still small, the system
    settled. If it's larger than the threshold (or growing), it's unstable.
    """
    tail_start = int(len(phi_array) * (1 - tail_fraction))
    tail = phi_array[tail_start:]
    return np.max(np.abs(tail)) < threshold_rad


def growth_rate(phi_array: np.ndarray, time_array: np.ndarray) -> float:
    """
    Rough exponential growth-rate estimate for an unstable (diverging)
    oscillation: fits log(|phi|) vs time over the second half of the run.
    Positive = diverging, negative/near-zero = stable or decaying.
    """
    half = len(phi_array) // 2
    amp = np.abs(phi_array[half:])
    amp = np.clip(amp, 1e-6, None)  # avoid log(0)
    t = time_array[half:]
    slope, _ = np.polyfit(t, np.log(amp), 1)
    return slope
