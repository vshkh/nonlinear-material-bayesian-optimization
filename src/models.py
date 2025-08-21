"""
models.py

Placeholder physics models for the simulator.
Replace these with your actual, validated physical models.
"""

import numpy as np

def sa_T(I, alpha0, alpha_ns, Isat):
    """A simple model for a saturable absorber's transmission."""
    return 1 - (alpha0 / (1 + I / Isat) + alpha_ns)

def photoconductor_R(I, R_dark, R_light, I_half):
    """A simple model for a photoconductor's resistance."""
    return R_dark / (1 + (R_dark/R_light - 1) * I / I_half)

def kerr_phi(I, n2, L_int_m, lambda_m, n_eff, field_enhance):
    """A simple model for Kerr effect phase shift."""
    return (2 * np.pi / lambda_m) * n2 * I * L_int_m * field_enhance / n_eff

def mzi_T_from_phase(phi):
    """Model for a Mach-Zehnder Interferometer's transmission from phase."""
    return np.cos(phi / 2)**2

def calculate_n_from_sellmeier(coeffs: dict, lambda_um: float) -> float:
    """Calculates refractive index n using the Sellmeier equation."""
    lambda_sq = lambda_um**2
    n_sq = 1.0
    for B, C in coeffs.items():
        n_sq += (B * lambda_sq) / (lambda_sq - C)
    return np.sqrt(n_sq)

def small_signal_absorption_from_k(k, lambda_m, t_total):
    """Calculates small-signal absorption from extinction coefficient k."""
    return (4 * np.pi * k / lambda_m) * t_total

def layers_to_total_thickness(layer_thickness_nm, layers):
    """Calculates total thickness from layer thickness and number of layers."""
    return layer_thickness_nm * 1e-9 * layers

def contrast(y):
    """Calculates the contrast of a response curve."""
    return np.max(y) - np.min(y)

def knee_intensity_by_fraction(I, y, frac=0.5):
    """Finds the intensity at which the response reaches a fraction of its max value."""
    target = np.min(y) + frac * (np.max(y) - np.min(y))
    return I[np.argmin(np.abs(y - target))]

