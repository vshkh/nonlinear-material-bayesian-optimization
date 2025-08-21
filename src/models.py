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

def kerr_phi(I, n2, L_int_m, lambda_m):
    """A simple model for Kerr effect phase shift."""
    return (2 * np.pi / lambda_m) * n2 * I * L_int_m

def mzi_T_from_phase(phi):
    """Model for a Mach-Zehnder Interferometer's transmission from phase."""
    return np.cos(phi / 2)**2
