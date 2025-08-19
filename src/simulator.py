"""
simulator.py

This module contains the core simulation logic.

The `simulate` function takes a set of parameters (Params) and returns
the calculated Key Performance Indicators (KPIs) for that configuration.

It uses placeholder physical models from `models.py`. These should be
replaced with real, validated models for accurate results.
"""

import numpy as np
from .types import Params, KPIs, Curve, Material
from .materials import MATERIALS_DATABASE
from .models import (
    sa_T, kerr_phi, mzi_T_from_phase,
    small_signal_absorption_from_k, layers_to_total_thickness,
    contrast as kpi_contrast, knee_intensity_by_fraction
)

def simulate(params: Params) -> KPIs:
    """
    This is the main simulation function.
    It takes a set of parameters, chooses a physical model based on the material,
    simulates the material's response to light, and returns the performance metrics.
    """
    # Look up the intrinsic physical properties of the chosen material
    props = MATERIALS_DATABASE[params.material]

    # Define the range of light intensities to simulate over.
    # This should span from low intensity to high intensity to see the nonlinear effect.
    I = np.logspace(2, 8, 300)  # W/m^2

    # Convert parameters to standard units (meters)
    lambda_m = params.lambda_nm * 1e-9
    t_total = layers_to_total_thickness(props.layer_thickness_nm, params.layers)

    # --- Select the physical model based on the material ---
    if params.material in (Material.MOS2, Material.WS2):
        # ----- Path 1: Saturable Absorber (SA) Model -----
        # This model is for materials that change their ABSORPTION with light intensity.
        
        # First, calculate the baseline absorption at low light intensity.
        A0 = small_signal_absorption_from_k(props.k, lambda_m, t_total)
        
        # Not all absorption is necessarily bleachable. We define a saturable fraction.
        f_sat = props.saturable_fraction if props.saturable_fraction is not None else 0.6
        f_sat = float(np.clip(f_sat, 0.0, 1.0))
        alpha0 = f_sat * A0           # This is the part of the absorption that can disappear.
        alpha_ns = (1.0 - f_sat) * A0 # This part of the absorption always remains.
        
        # Get the saturation intensity from the material properties.
        Isat = props.Isat_W_m2 if props.Isat_W_m2 is not None else 1e6
        
        # Run the SA model to get the transmission curve.
        T = sa_T(I, alpha0=alpha0, alpha_ns=alpha_ns, Isat=Isat)

        # --- Calculate KPIs for the SA material ---
        curve = Curve(I=I, y=T, kind='T')
        T0 = float(T[0]) # Baseline transmission at low intensity
        C = kpi_contrast(T) # Total change in transmission
        knee = knee_intensity_by_fraction(I, T, frac=0.5)  # Intensity at mid-point of the transition
        tau = props.tau_s if props.tau_s is not None else 5e-9 # Response time

        # Estimate the switching energy. A key metric for ONNs.
        # E_sw ≈ I_knee * Area * τ (a rough estimate)
        area_m2 = (10e-6) * (10e-6) # Assume a 10x10 micron device area
        Esw_pJ = 1e12 * knee * area_m2 * tau

    elif params.material is Material.GRAPHENE:
        # ----- Path 2: Kerr Effect Model -----
        # This model is for materials that change their REFRACTIVE INDEX with light intensity.
        
        # Get geometry parameters that affect the effective intensity.
        Gamma = max(0.0, float(params.Gamma)) # Mode overlap with the material
        FE = 1.0 + 0.002 * max(0.0, float(params.Q)) # Field enhancement from a cavity
        
        # Run the Kerr model to get the phase shift curve.
        phi = kerr_phi(I * Gamma, n2=props.n2, L_int_m=params.L_int_um * 1e-6,
                       lambda_m=lambda_m, field_enhance=FE)
        
        # A phase shift is invisible. We use a device model (MZI) to convert it to a transmission change.
        T = mzi_T_from_phase(phi)

        # --- Calculate KPIs for the Kerr material ---
        curve = Curve(I=I, y=T, kind='T')
        T0 = float(T[0])
        C = kpi_contrast(T)

        # For an MZI, the most interesting point is often a π/2 phase shift.
        # We can calculate the intensity required to achieve this directly.
        phi_target = np.pi / 2.0
        k0 = 2.0 * np.pi / lambda_m
        denom = max(k0 * props.n2 * params.L_int_um * 1e-6 * FE * max(Gamma, 1e-12), 1e-30)
        knee = float(phi_target / denom)

        tau = props.tau_s if props.tau_s is not None else 1e-12
        area_m2 = (10e-6) * (10e-6) # Assume a 10x10 micron device area
        Esw_pJ = 1e12 * knee * area_m2 * tau

    else:
        raise NotImplementedError(f"No model wired for {props.name}")

    # Return all the calculated performance metrics.
    return KPIs(
        contrast=float(C),
        T0=float(T0),
        knee_I=float(knee),
        E_sw_pJ=float(Esw_pJ),
        tau_s=float(tau),
        curve=curve
    )
