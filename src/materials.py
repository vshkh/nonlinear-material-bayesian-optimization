"""
materials.py

Database of MaterialProperties for candidate nonlinear materials.
Values here are placeholders — replace with literature/experimental data.
"""

from .types import Material, MaterialProperties, Sourcing, NonlinearEffect
from copy import deepcopy

MATERIALS_DATABASE = {
    Material.MOS2: MaterialProperties(
        name=Material.MOS2,
        sourcing=Sourcing.COMMERCIAL,
        active_effects=(NonlinearEffect.SATURABLE_ABSORPTION, NonlinearEffect.KERR),
        layer_thickness_nm=0.65,
        n={1550: 3.5},
        k={1550: 0.01},
        n2={1550: 1.4e-13},
        Isat_W_m2={1550: 1e10}, # 1 MW/cm^2
        tau_s=1e-12, # 1 ps
        saturable_fraction=0.8,
        references={
            "n2": "https://researchportal.hw.ac.uk/en/publications/nonlinear-optical-properties-of-molybdenum-disulfide-mos2-in-the-",
            "Isat": "Placeholder value, literature reports MW/cm^2 to GW/cm^2",
            "tau_s": "Typical ultrafast dynamics are in the ps range"
        }
    ),
    Material.WS2: MaterialProperties(
        name=Material.WS2,
        sourcing=Sourcing.COMMERCIAL,
        active_effects=(NonlinearEffect.SATURABLE_ABSORPTION, NonlinearEffect.KERR),
        layer_thickness_nm=0.65,
        n={1550: 3.3},
        k={1550: 0.01},
        n2={1550: 1e-12},
        Isat_W_m2={1558: 4e10}, # 4 MW/cm^2
        tau_s=1e-12, # 1 ps
        saturable_fraction=0.8,
        references={
            "Isat": "https://opg.optica.org/oe/fulltext.cfm?uri=oe-23-1-535&id=308337",
            "tau_s": "Typical ultrafast dynamics are in the ps range"
        }
    ),
    Material.GRAPHENE: MaterialProperties(
        name=Material.GRAPHENE,
        sourcing=Sourcing.LAB,
        active_effects=(NonlinearEffect.KERR, NonlinearEffect.SATURABLE_ABSORPTION),
        layer_thickness_nm=0.34,
        n={1550: 2.5},
        k={1550: 1.3},
        n2={1550: 1e-11},
        Isat_W_m2={1550: 1e10}, # Placeholder, typically MW/cm^2
        tau_s=1e-12, # 1 ps
        saturable_fraction=0.2,
        references={
            "n, k": "https://refractiveindex.info/?sheet=2d/graphene&page=Li",
            "n2": "Placeholder, reports vary widely. See https://www.nature.com/articles/s41598-017-08959-6",
            "absorption": "approx. 2.3% per layer"
        }
    ),
}

def get_material(material: Material) -> MaterialProperties:
    return deepcopy(MATERIALS_DATABASE[material])