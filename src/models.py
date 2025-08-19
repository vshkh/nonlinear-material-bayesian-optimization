# models.py
"""
Analytic device models for fast Tier-1 simulation.
Units:
  I: W/m^2, lambda: m, lengths: m, n2: m^2/W
"""
from __future__ import annotations
import numpy as np

# ---------- Utilities ----------
def _asf(x): 
    """A shorthand function to ensure the input is a numpy array of floats."""
    return np.asarray(x, dtype=float, order="C")

def absorption_coeff_from_k(k: float, lambda_m: float) -> float:
    """
    Calculates the absorption coefficient (alpha) from the extinction coefficient (k).
    Physics: The extinction coefficient 'k' is the imaginary part of the complex
    refractive index. It describes how much light is absorbed by the material.
    This formula converts 'k' into the more commonly used absorption coefficient
    'alpha', which has units of inverse meters (1/m).
    """
    lambda_m = max(lambda_m, 1e-30) # Avoid division by zero
    return 4.0 * np.pi * float(k) / lambda_m

def layers_to_total_thickness(layer_thickness_nm: float, layers: int) -> float:
    """Converts number of layers and single-layer thickness to total thickness in meters."""
    return max(0.0, float(layer_thickness_nm)) * 1e-9 * max(1, int(layers))

def small_signal_absorption_from_k(k: float, lambda_m: float, t_m: float) -> float:
    """
    Calculates the total absorption (A0) for a thin film at low light intensity.
    Physics: For a thin film, the transmission of light follows the Beer-Lambert law,
    T0 = exp(-alpha * t), where t is the thickness. This function calculates that
    initial transmission and returns the absorption A0 = 1 - T0.
    """
    alpha = absorption_coeff_from_k(k, lambda_m)
    T0 = np.exp(-alpha * t_m)
    A0 = float(np.clip(1.0 - T0, 0.0, 0.95))  # cap to avoid pathological values
    return A0

# ---------- Nonlinear “activation” models ----------
def sa_T(I, alpha0: float, alpha_ns: float, Isat: float) -> np.ndarray:
    """
    Models the transmission of a Saturable Absorber (SA).
    Physics: A saturable absorber is a material that becomes more transparent as the
    intensity of light increases. At low intensity, it absorbs a lot (alpha0).
    As intensity approaches the saturation intensity (Isat), this absorption
    "bleaches" away, and the transmission increases. Some non-saturable absorption
    (alpha_ns) always remains.
    """
    I = _asf(I)
    Isat = max(Isat, 1e-30)
    # T = 1 - (total absorption)
    T = 1.0 - alpha_ns - alpha0 / (1.0 + I / Isat)
    return np.clip(T, 0.0, 1.0)

def photoconductor_R(I, R_dark: float, R_light: float, I_half: float, gamma: float = 1.0) -> np.ndarray:
    """
    Models the resistance of a photoconductor.
    Physics: A photoconductor is a material whose electrical resistance decreases when
    light shines on it. It has a high resistance in the dark (R_dark) and a lower
    resistance when illuminated (R_light). The transition between these states
    depends on the light intensity, characterized by a half-intensity (I_half).
    """
    I = _asf(I)
    I_half = max(I_half, 1e-30)
    gamma = max(gamma, 1e-9)
    return np.maximum(R_light + (R_dark - R_light) / (1.0 + (I / I_half) ** gamma), 0.0)

def kerr_phi(I, n2: float, L_int_m: float, lambda_m: float, field_enhance: float = 1.0) -> np.ndarray:
    """
    Models the phase shift from the Kerr effect.
    Physics: The Kerr effect is a nonlinear phenomenon where the refractive index (n)
    of a material changes with the intensity of light (I). The strength of this
    effect is determined by the nonlinear refractive index (n2). This change in 'n'
    causes the phase of the light to shift as it travels through the material over a
    certain length (L_int_m). The field_enhance factor accounts for structures like
    cavities that can make the light intensity inside the device stronger.
    """
    I = _asf(I)
    lambda_m = max(lambda_m, 1e-30)
    k0 = 2.0 * np.pi / lambda_m # Wavevector in vacuum
    # The core formula for nonlinear phase shift: Δφ = k0 * Δn * L
    # where Δn = n2 * I_effective
    return k0 * n2 * L_int_m * (field_enhance * I)

# ---------- Linear optics wrappers ----------
def mzi_T_from_phase(phi: np.ndarray, insertion_loss: float = 0.0) -> np.ndarray:
    """
    Models the transmission of a Mach-Zehnder Interferometer (MZI).
    Physics: An MZI is a common optical device that splits light into two paths and
    then recombines them. The final output intensity depends on the phase difference
    (phi) between the two paths. It converts a phase change (which is hard to detect)
    into a transmission change (which is easy to detect). This is the standard way
    to measure the result of a Kerr phase shift.
    """
    phi = _asf(phi)
    # The classic MZI transmission formula
    T = 0.5 * (1.0 + np.cos(phi))
    if insertion_loss > 0:
        T *= np.exp(-insertion_loss)
    return np.clip(T, 0.0, 1.0)

def ring_T_from_phase(phi: np.ndarray, t: float, a: float) -> np.ndarray:
    """
    Models the transmission of a single-bus ring resonator.
    Physics: A ring resonator is another device that is very sensitive to phase shifts.
    Light circulates in a ring, and its interference with the input light depends
    critically on the round-trip phase (phi). 't' is the transmission coefficient
    of the coupler and 'a' is the single-pass amplitude transmission (loss in the ring).
    """
    phi = _asf(phi); t = np.clip(float(t), 0.0, 1.0); a = np.clip(float(a), 0.0, 1.0)
    num = (t - a) ** 2
    den = 1.0 - 2.0 * a * t * np.cos(phi) + (a * t) ** 2
    T = num / np.maximum(den, 1e-30)
    return np.clip(T, 0.0, 1.0)

# ---------- KPI helpers ----------
def contrast(y: np.ndarray) -> float:
    """Calculates the contrast (max - min) of a response curve."""
    y = _asf(y)
    return float(np.nanmax(y) - np.nanmin(y))

def knee_intensity_by_fraction(I: np.ndarray, y: np.ndarray, frac: float = 0.5) -> float:
    """
    Calculates the "knee" intensity of a curve.
    This is a characteristic point, defined as the intensity where the response 'y'
    has completed a certain fraction of its total swing (e.g., 50%).
    """
    I = _asf(I); y = _asf(y)
    if I.size == 0: return float("nan")
    y0, y1 = y[0], y[-1]
    target = y0 + frac * (y1 - y0)
    # Find the index of the intensity value that corresponds to the target response
    idx = int(np.clip(np.searchsorted(y, target), 0, len(I) - 1))
    return float(I[idx])
