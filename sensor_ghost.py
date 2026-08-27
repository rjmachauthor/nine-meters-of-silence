"""
Phase 2 -- "False Lead #1: The Sensor Ghost"
Chapter 1, Thermal Suicide

Claim from the manuscript:
    The IMU shows a sudden, massive phase shift in the roll axis during the
    flutter event. The team suspects the sensor is blinded by the flutter
    and sending bad signals. Maya runs a Kalman Filter Residual Analysis:
    if the sensor were broken, the residual should blow up. Instead, the
    residuals are flat. The sensor isn't lying. It's tracking reality
    perfectly. The hardware is fine.

This module implements a real Kalman filter tracking roll angle from noisy
measurements, and compares two scenarios:

  1. Healthy sensor, large real disturbance (the flutter event itself) --
     the filter's process model correctly represents the true dynamics, so
     even though the *signal* looks dramatic, the *residual* stays small
     and within statistically normal bounds.

  2. Broken sensor -- a sudden bias fault (a real, documented, instant-onset
     IMU failure mode -- a "stuck-at" or bias-offset fault, distinct from
     classic gyro drift). NOTE: classic gyro drift is a genuinely slow
     phenomenon -- real aviation-grade gyros drift on the order of
     0.01-10 degrees PER HOUR, which cannot produce a detectable signature
     within a few seconds. A sudden bias STEP, by contrast, is a real
     failure mode that can onset instantly and matches the manuscript's own
     description ("a sudden, massive phase shift") far better than a slow
     drift would. See CALIBRATION.md for the sourcing on this distinction.

The diagnostic used is the Normalized Innovation Squared (NIS), the
standard statistical test for Kalman filter consistency: NIS should stay
within a known chi-squared bound if the filter and sensor are behaving as
expected, and rise well past that bound if something is actually wrong.
"""

import numpy as np


def true_roll_angle(t: np.ndarray, base_freq_hz: float = 0.1, flutter_freq_hz: float = 20.0,
                     flutter_onset_s: float = 5.0, flutter_amp_rad: float = 0.15) -> np.ndarray:
    """
    A physically plausible roll-angle time history: gentle baseline motion,
    with a real 20 Hz flutter oscillation kicking in partway through -- this
    is the actual physical event the book's Phase 1 flutter describes.
    """
    baseline = 0.02 * np.sin(2 * np.pi * base_freq_hz * t)
    flutter = np.where(
        t >= flutter_onset_s,
        flutter_amp_rad * np.sin(2 * np.pi * flutter_freq_hz * (t - flutter_onset_s)),
        0.0,
    )
    return baseline + flutter


def run_kalman_1d(measurements: np.ndarray, dt: float, process_var: float, measurement_var: float,
                   decay_rate: float = 0.0):
    """
    A minimal 1D Kalman filter tracking a single scalar state (roll angle)
    with a process model that includes a physically-motivated mean-reversion
    term: `decay_rate` represents the aerodynamic/control restoring force
    that keeps a real aircraft's attitude bounded rather than drifting
    indefinitely. Setting decay_rate=0 recovers a plain random-walk model.

    Returns the filtered estimate and, critically, the sequence of
    normalized innovation squared (NIS) values used for the consistency test.

    NIS_k = innovation_k^2 / innovation_covariance_k

    Under a correctly-tuned filter observing a sensor that's actually
    telling the truth about a physically bounded quantity, NIS should
    average close to 1 (chi-squared with 1 degree of freedom). A signal that
    violates the model's physical assumption (e.g. an unexplained offset on
    a quantity the model expects to stay bounded near zero) breaks that
    assumption and NIS rises and stays elevated.
    """
    n = len(measurements)
    x_est = np.zeros(n)      # filtered state estimate
    p_est = np.zeros(n)      # estimate covariance
    nis = np.zeros(n)        # normalized innovation squared

    x = measurements[0]
    p = measurement_var

    for k in range(n):
        # predict -- mean-reverting process model: a real, aerodynamically
        # damped roll attitude decays toward zero rather than drifting freely
        x_pred = x * (1 - decay_rate)
        p_pred = p + process_var

        # update
        innovation = measurements[k] - x_pred
        innovation_cov = p_pred + measurement_var
        kalman_gain = p_pred / innovation_cov

        x = x_pred + kalman_gain * innovation
        p = (1 - kalman_gain) * p_pred

        nis[k] = (innovation ** 2) / innovation_cov

        x_est[k] = x
        p_est[k] = p

    return x_est, p_est, nis


def generate_healthy_sensor_scenario(duration_s: float = 10.0, dt: float = 0.001,
                                      measurement_std: float = 0.01, seed: int = 42):
    """
    Scenario 1: sensor is fine, and there's a real, large flutter disturbance.
    The filter's process noise is set high enough to track real dynamics of
    this scale, so even a dramatic true signal should not blow up the NIS.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(0, duration_s, dt)
    true_signal = true_roll_angle(t)
    measurements = true_signal + rng.normal(0, measurement_std, size=len(t))

    # process variance tuned so the filter can genuinely track the real
    # flutter dynamics -- see CALIBRATION.md for how this value was chosen
    process_var = (0.015) ** 2
    measurement_var = measurement_std ** 2
    decay_rate = 0.12  # mean-reversion strength -- see CALIBRATION.md

    x_est, p_est, nis = run_kalman_1d(measurements, dt, process_var, measurement_var, decay_rate)
    return {"time": t, "true": true_signal, "measured": measurements, "estimate": x_est, "nis": nis}


def generate_broken_sensor_scenario(duration_s: float = 10.0, dt: float = 0.001,
                                     measurement_std: float = 0.01, fault_onset_s: float = 5.0,
                                     bias_magnitude_rad: float = 0.2, seed: int = 42):
    """
    Scenario 2: the sensor develops a sudden bias fault at fault_onset_s --
    a real, instant-onset IMU failure mode, and a much closer physical match
    to the manuscript's "sudden, massive phase shift" than gradual drift
    would be. Because the filter's process model assumes a physically
    bounded, mean-reverting roll attitude, a persistent, unexplained offset
    is a genuine, sustained violation of that assumption -- which is exactly
    why the residual test can tell it apart from a large but legitimate
    oscillation.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(0, duration_s, dt)
    true_signal = true_roll_angle(t)
    noise = rng.normal(0, measurement_std, size=len(t))

    bias = np.where(t >= fault_onset_s, bias_magnitude_rad, 0.0)
    measurements = true_signal + noise + bias

    process_var = (0.015) ** 2
    measurement_var = measurement_std ** 2
    decay_rate = 0.12

    x_est, p_est, nis = run_kalman_1d(measurements, dt, process_var, measurement_var, decay_rate)
    return {"time": t, "true": true_signal, "measured": measurements, "estimate": x_est, "nis": nis}


def mean_nis_after(scenario: dict, after_s: float) -> float:
    """Average NIS value after a given time -- used to check consistency
    once the disturbance/failure has had time to take effect."""
    mask = scenario["time"] >= after_s
    return float(np.mean(scenario["nis"][mask]))
