"""
main.py

Main script to run the Bayesian Optimization.

This script defines the search space for the optimizer, runs the optimization loop,
and prints the best-found material and device parameters.

NOTE: This script requires the scikit-optimize library.
Install it with: pip install scikit-optimize
"""

import numpy as np

# --- Add this import for Bayesian Optimization ---
# You may need to install it: pip install scikit-optimize
from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args

from src.simulator import simulate
from src.types import Params, Material, Sourcing
from src.materials import MATERIALS_DATABASE

# --- 1. Define Search Space for the Optimizer ---
# This section tells the optimizer which parameters (or "dials") it is allowed to turn,
# and what the valid range is for each one.

# First, we can apply any hard constraints, like only using commercial materials.
searchable_materials = [
    m for m in MATERIALS_DATABASE.keys() 
    if MATERIALS_DATABASE[m].sourcing == Sourcing.COMMERCIAL
]

# Next, we define the space. skopt needs to know the type and range of each parameter.
# NOTE: We pass the string values of the materials (e.g., 'MOS2') to skopt.
space  = [
    Categorical([m.value for m in searchable_materials], name='material'),
    Integer(1, 5, name='layers'),
    Integer(1300, 1600, name='lambda_nm'),
    # We can also optimize the geometry knobs from the Params dataclass.
    Real(10, 1000, name='Q'),
    Real(0.05, 0.5, name='Gamma')
]

# --- 2. Create the Objective Function for the Optimizer ---
# This is the function the optimizer will repeatedly call to test a set of parameters.
# Its goal is to find the set of parameters that returns the best score.

# The @use_named_args decorator is a helper from skopt that lets us use keyword arguments.
@use_named_args(space)
def objective_function(**params_dict):
    """
    Wrapper around our `simulate` function.
    It takes keyword arguments from the optimizer, runs the simulation,
    and returns a single score to be MINIMIZED.
    """
    # The optimizer gives us a string for the material, so we cast it back to our Enum.
    params_dict['material'] = Material(params_dict['material'])
    # Create the Params object that our simulator expects.
    params = Params(**params_dict)
    
    kpis = simulate(params)

    # Define a "figure of merit" or "score" based on the simulation results.
    # A good modulator has high contrast and low switching energy, so we maximize C/E.
    if kpis.E_sw_pJ is not None and kpis.E_sw_pJ > 1e-9:
        score = kpis.contrast / kpis.E_sw_pJ
    else:
        score = 0.0 # Assign a poor score if the energy is zero or None. 
    
    print(f"  - Simulating: {params.material.value}, Layers: {params.layers}, Lambda: {params.lambda_nm}nm, Q: {params.Q:.1f}, Gamma: {params.Gamma:.2f} -> Score: {score:.4e}")
    
    # skopt's gp_minimize function tries to MINIMIZE the objective.
    # Since we want to MAXIMIZE our score, we return its negative.
    return -score

def main():
    """
    Main function to set up and run the Bayesian Optimization loop.
    """
    print("Starting Bayesian Optimization...")

    # --- 3. Run Optimization Loop ---
    # This single function call is the core of the optimization.
    # It will intelligently search the parameter `space` by repeatedly calling the
    # `objective_function` for `n_calls` iterations.
    result = gp_minimize(
        func=objective_function, 
        dimensions=space, 
        n_calls=50, # You can increase this for a more thorough search
        random_state=42 # for reproducibility
    )

    print("\n--- Optimization Finished ---")
    
    # --- 4. Process and Display Results ---
    # The best parameters found by the optimizer are in the `result.x` list.
    best_params_list = result.x
    # The best score is in `result.fun`.
    best_score = -result.fun # Remember to negate the score back to its original scale.

    # Re-create the Params object to get full details.
    best_params = Params(
        material=Material(best_params_list[0]),
        layers=best_params_list[1],
        lambda_nm=best_params_list[2],
        Q=best_params_list[3],
        Gamma=best_params_list[4]
    )
    # Rerun the simulation one last time with the best params to get the final KPIs.
    best_kpis = simulate(best_params)

    if best_params and best_kpis:
        print(f"Best Score: {best_score:.4e}")
        print(f"Best Parameters Found:")
        print(f"  - Material: {best_params.material.value}")
        print(f"  - Layers: {best_params.layers}")
        print(f"  - Wavelength: {best_params.lambda_nm} nm")
        print(f"  - Q: {best_params.Q:.1f}")
        print(f"  - Gamma: {best_params.Gamma:.2f}")
        print("\nResulting Performance:")
        print(f"  - Contrast: {best_kpis.contrast:.3f}")
        print(f"  - T0: {best_kpis.T0:.3f}")
        print(f"  - Knee Intensity: {best_kpis.knee_I:.2e} W/m^2")
        print(f"  - Switching Energy: {best_kpis.E_sw_pJ:.3f} pJ")
        print(f"  - Response Time: {best_kpis.tau_s * 1e9:.3f} ns")
    else:
        print("Optimization failed to find a suitable result.")

if __name__ == "__main__":
    main()
