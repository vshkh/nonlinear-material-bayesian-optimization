# Nonlinear Material Bayesian Optimization

This project is a **physics-based screening and optimization framework** for nonlinear optical materials, aimed at enabling **all-optical neural networks (ONNs)**.

The core idea:  
Different materials (e.g. MoS₂, WS₂, Graphene) exhibit nonlinear optical responses that can act as the “activation functions” of an optical neuron. To design practical ONNs, we need to evaluate candidate materials and geometries against **key performance indicators (KPIs)** like contrast, transparency, response time, and switching energy.

---

## Features

- **Material Database (`src/materials.py`)**  
  Includes candidate nonlinear materials with placeholder optical constants (`n`, `k`, `n₂`, thickness, saturation intensity, recovery time). Replace with values from literature or experiments.

- **Analytic Models (`src/models.py`)**  
  - Saturable absorption (MoS₂ / WS₂)  
  - Kerr nonlinearity + Mach–Zehnder interferometer (Graphene)  
  - Helpers for absorption, contrast, knee intensity

- **Simulator (`src/simulator.py`)**  
  Converts `{material, wavelength, layers, geometry}` into:
  - Transmission/response curves
  - KPIs: baseline transparency (T₀), contrast, knee intensity, switching energy, response time

- **Main Script (`main.py`)**  
  Sweeps materials and parameters, computes KPIs, and applies a scoring function to identify “best” candidates.

---

## Example Output

```
(...)
  - Simulating: MOS2, Layers: 4, Lambda: 1403nm, Q: 108.7, Gamma: 0.11 -> Score: 3.3825e-03
  - Simulating: WS2, Layers: 4, Lambda: 1516nm, Q: 875.8, Gamma: 0.11 -> Score: 6.8982e-03
  - Simulating: WS2, Layers: 2, Lambda: 1595nm, Q: 654.9, Gamma: 0.12 -> Score: 3.2801e-03
  - Simulating: MOS2, Layers: 2, Lambda: 1536nm, Q: 570.7, Gamma: 0.10 -> Score: 1.5458e-03
  - Simulating: MOS2, Layers: 4, Lambda: 1410nm, Q: 680.0, Gamma: 0.14 -> Score: 3.3658e-03
  - Simulating: WS2, Layers: 5, Lambda: 1300nm, Q: 164.6, Gamma: 0.42 -> Score: 1.0050e-02
  - Simulating: WS2, Layers: 3, Lambda: 1455nm, Q: 80.9, Gamma: 0.38 -> Score: 5.3918e-03
  - Simulating: MOS2, Layers: 2, Lambda: 1490nm, Q: 523.6, Gamma: 0.42 -> Score: 1.5935e-03

--- Optimization Finished ---
Best Score: 1.0050e-02
Best Parameters Found:
  - Material: WS2
  - Layers: 5
  - Wavelength: 1300 nm
  - Q: 391.7
  - Gamma: 0.50

Resulting Performance:
  - Contrast: 0.002
  - T0: 0.997
  - Knee Intensity: 6.20e+05 W/m^2
  - Switching Energy: 0.186 pJ
  - Response Time: 3.000 ns
```
