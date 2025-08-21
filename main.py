"""
main.py

Main script to run the Bayesian Optimization.

This script defines the search space for the optimizer, runs the optimization loop,
prints the best-found material and device parameters, and plots the results.

NOTE: This script requires scikit-optimize and matplotlib.
Install with: pip install scikit-optimize matplotlib
"""

import numpy as np

# --- Imports for Bayesian Optimization ---
from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args
from skopt.plots import plot_convergence

# --- Imports for Plotting ---
import matplotlib.pyplot as plt

from src.simulator import simulate
from src.types import Params, Material, Sourcing, KPIs
from src.materials import MATERIALS_DATABASE

# --- 1. Define Search Space for the Optimizer ---
searchable_materials = [
    m for m in MATERIALS_DATABASE.keys() 
    if MATERIALS_DATABASE[m].sourcing == Sourcing.COMMERCIAL
]
space  = [
    Categorical([m.value for m in searchable_materials], name='material'),
    Integer(1, 5, name='layers'),
    Integer(1300, 1600, name='lambda_nm'),
    Real(10, 1000, name='Q'),
    Real(0.05, 0.5, name='Gamma')
]

# --- 2. Create the Objective Function for the Optimizer ---
@use_named_args(space)
def objective_function(**params_dict):
    params_dict['material'] = Material(params_dict['material'])
    params = Params(**params_dict)
    kpis = simulate(params)
    if kpis.E_sw_pJ is not None and kpis.E_sw_pJ > 1e-9:
        score = kpis.contrast / kpis.E_sw_pJ
    else:
        score = 0.0
    print(f"  - Simulating: {params.material.value}, Layers: {params.layers}, Lambda: {params.lambda_nm}nm, Q: {params.Q:.1f}, Gamma: {params.Gamma:.2f} -> Score: {score:.4e}")
    return -score

# --- 5. Add a new function for plotting results ---
def plot_results(result: object, best_kpis: KPIs):
    """
    Generates and displays plots summarizing the optimization results.
    """
    print("\nGenerating plots...")
    # Create a figure with two subplots, arranged vertically
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), tight_layout=True)

    # --- Plot 1: Convergence Plot ---
    # This plot shows the best score found at each iteration of the optimizer.
    # It helps visualize if the optimizer is converging to a good solution.
    plot_convergence(result, ax=ax1)
    ax1.set_title('Optimizer Convergence')
    ax1.set_ylabel('Best Score Found (Negative)')
    ax1.grid(True)

    # --- Plot 2: Response Curve of the Best Device ---
    # This shows the transmission vs. intensity curve for the winning parameters.
    curve = best_kpis.curve
    ax2.semilogx(curve.I, curve.y, label=f'Best Result (Esw = {best_kpis.E_sw_pJ:.2f} pJ)')
    ax2.set_title('Response Curve of Optimal Device')
    ax2.set_xlabel('Intensity (W/m^2)')
    ax2.set_ylabel(f'Transmission ({curve.kind})')
    ax2.grid(True)
    ax2.legend()

    # Save the plots to a file instead of showing them
    output_filename = "optimization_results.png"
    plt.savefig(output_filename)
    print(f"Plots saved to {output_filename}")

def main():
    """
    Main function to set up and run the Bayesian Optimization loop.
    """
    print("Starting Bayesian Optimization...")

    # --- 3. Run Optimization Loop ---
    result = gp_minimize(
        func=objective_function, 
        dimensions=space, 
        n_calls=50, 
        random_state=42
    )

    print("\n--- Optimization Finished ---")
    
    # --- 4. Process and Display Results ---
    best_params_list = result.x
    best_score = -result.fun
    best_params = Params(
        material=Material(best_params_list[0]),
        layers=best_params_list[1],
        lambda_nm=best_params_list[2],
        Q=best_params_list[3],
        Gamma=best_params_list[4]
    )
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
        
        # Call the new plotting function
        plot_results(result, best_kpis)
    else:
        print("Optimization failed to find a suitable result.")

if __name__ == "__main__":
    main()
