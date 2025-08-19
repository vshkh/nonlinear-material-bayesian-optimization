"""
materials.py

Database of MaterialProperties for candidate nonlinear materials.
Values here are placeholders — replace with literature/experimental data.
"""

from .types import Material, MaterialProperties, Sourcing
from copy import deepcopy

MATERIALS_DATABASE = {
    Material.MOS2: MaterialProperties(
        name=Material.MOS2,
        sourcing=Sourcing.COMMERCIAL,
        n=5.5, k=0.10, n2=1e-12,
        layer_thickness_nm=0.65,
        Isat_W_m2=8e5,             # placeholder; tune with data
        tau_s=5e-9,                # ~ns-class for photocarrier recovery
        saturable_fraction=0.6     # 60% of loss is bleachable
    ),
    Material.WS2: MaterialProperties(
        name=Material.WS2,
        sourcing=Sourcing.COMMERCIAL,
        n=4.5, k=0.10, n2=1e-12,
        layer_thickness_nm=0.65,
        Isat_W_m2=6e5,
        tau_s=3e-9,
        saturable_fraction=0.6
    ),
    Material.GRAPHENE: MaterialProperties(
        name=Material.GRAPHENE,
        sourcing=Sourcing.LAB,
        n=2.5, k=0.00, n2=1e-11,
        layer_thickness_nm=0.34,
        Isat_W_m2=None,            # not used in Kerr path
        tau_s=1e-12,               # ultrafast Kerr
        saturable_fraction=None
    ),
}

def get_material(material: Material) -> MaterialProperties:
    return deepcopy(MATERIALS_DATABASE[material])