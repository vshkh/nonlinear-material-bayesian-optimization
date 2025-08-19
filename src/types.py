"""
types.py

Define a class for materials to store its properties for simulation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional
import numpy as np

class Material(str, Enum):
    MOS2 = 'MOS2'
    WS2 = 'WS2'
    GRAPHENE = 'Graphene'

class Sourcing(str, Enum):
    COMMERCIAL = "Commercial"
    LAB = "Lab-Synthesized"
    EXPERIMENTAL = "Experimental"

"""
Input parameters for simulation.
"""
@dataclass
class Params:
    material: Material
    layers: int 
    lambda_nm: int 
    # Geometry knobs, geometry-related parameters
    Q: float = 200.0
    Gamma: float = 0.2
    L_int_um: float = 50.0

"""
Curve class to store the data of the curves.
"""
@dataclass
class Curve:
    
    I: np.ndarray # Intensity grid
    y: np.ndarray # response
    kind: Literal['T', 'R', 'phi']

"""
Key Performance Indicators (KPIs)
"""
@dataclass
class KPIs:
    contrast: float        # y(high) - y(low) on a defined range
    T0: float              # baseline (for T-kind) else np.nan
    knee_I: float          # characteristic intensity (Isat, I0, or I@phase_target)
    E_sw_pJ: Optional[float]  # switching energy estimate (filled later)
    tau_s: float           # response time (s)
    curve: Curve # type: ignore

@dataclass(frozen=True)
class MaterialProperties:
    name: Material
    sourcing: Sourcing
    n: float                   # real refractive index
    k: float                   # extinction coefficient (imag part)
    n2: float                  # nonlinear index [m^2/W] (Kerr path)
    layer_thickness_nm: float  # single-layer thickness in nm
    # ---- Optional model-specific defaults (may be None; can be overridden by data) ----
    Isat_W_m2: Optional[float] = None   # Saturation intensity for SA/PC if known
    tau_s: Optional[float] = None       # Response time [s]
    saturable_fraction: Optional[float] = None  # Fraction of low-intensity absorption that saturates (0..1)