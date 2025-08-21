"""
simulator.py

This module contains the core simulation logic.

This version uses a flexible, data-driven pipeline where the physical effects
to be simulated are determined by the `active_effects` list in the material's
properties, rather than a rigid if/elif structure.
"""

import numpy as np
from .types import Params, KPIs, Curve, Material, NonlinearEffect
from .materials import MATERIALS_DATABASE
from .models import (
    sa_T, kerr_phi, mzi_T_from_phase,
    small_signal_absorption_from_k, layers_to_total_thickness,
    contrast as kpi_contrast, knee_intensity_by_fraction
)

def simulate(params: Params) -> KPIs:
    """
    This is the main simulation function.
    It checks the material's `active_effects` list and applies each physical
    model in a pipeline to determine the final device response.
    """
    props = MATERIALS_DATABASE[params.material]
    I = np.logspace(2, 8, 300)  # W/m^2
    lambda_m = params.lambda_nm * 1e-9
    t_total = layers_to_total_thickness(props.layer_thickness_nm, params.layers)

    # --- Simulation Pipeline ---
    # Initialize baseline transmission and phase. We start with a perfectly
    # transparent device with no phase shift.
    total_transmission = np.ones_like(I, dtype=float)
    total_phase_shift = np.zeros_like(I, dtype=float)

    # Loop through the active effects defined for the material and apply them.
    for effect in props.active_effects:

        if effect == NonlinearEffect.SATURABLE_ABSORPTION:
            # --- Apply Saturable Absorption Effect ---
            # This effect modifies the device's transmission (loss).
            A0 = small_signal_absorption_from_k(props.k, lambda_m, t_total)
            f_sat = props.saturable_fraction if props.saturable_fraction is not None else 0.6
            alpha0 = f_sat * A0
            alpha_ns = (1.0 - f_sat) * A0
            Isat = props.Isat_W_m2 if props.Isat_W_m2 is not None else 1e6
            
            # This transmission is multiplied with the running total.
            total_transmission *= sa_T(I, alpha0=alpha0, alpha_ns=alpha_ns, Isat=Isat)

        elif effect == NonlinearEffect.KERR:
            # --- Apply Kerr Effect ---
            # This effect modifies the phase of the light.
            Gamma = max(0.0, float(params.Gamma))
            FE = 1.0 + 0.002 * max(0.0, float(params.Q))
            
            # This phase shift is added to the running total.
            total_phase_shift += kerr_phi(I * Gamma, n2=props.n2, L_int_m=params.L_int_um * 1e-6,
                                        lambda_m=lambda_m, field_enhance=FE)

    # --- Combine Effects ---
    # After all effects are accumulated, we convert the final phase shift into
    # a transmission change using a device model (e.g., an MZI).
    T_from_phase = mzi_T_from_phase(total_phase_shift)
    
    # The final response is the product of the transmission from absorption effects
    # and the transmission from phase effects.
    T_final = total_transmission * T_from_phase

    # --- Calculate Final KPIs ---
    # The KPIs are calculated based on the final, combined response curve.
    curve = Curve(I=I, y=T_final, kind='T')
    T0 = float(T_final[0])
    C = kpi_contrast(T_final)
    
    # For the knee, we have a choice. We can use the simple fractional method,
    # or for phase-based devices, calculate the intensity for a specific phase shift.
    # We'll use the fractional method for simplicity here on the final curve.
    knee = knee_intensity_by_fraction(I, T_final, frac=0.5)
    
    tau = props.tau_s if props.tau_s is not None else 1e-9 # Default to 1ns if not specified
    area_m2 = (10e-6) * (10e-6)
    Esw_pJ = 1e12 * knee * area_m2 * tau

    return KPIs(
        contrast=float(C),
        T0=float(T0),
        knee_I=float(knee),
        E_sw_pJ=float(Esw_pJ),
        tau_s=float(tau),
        curve=curve
    )

