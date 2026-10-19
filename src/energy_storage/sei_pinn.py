"""
Battery Electrochemical PINN & SEI Aging Dynamics
"""

import math
import numpy as np
from typing import Dict, Any, List, Tuple

FARADAY = 96485.3321  # C/mol
R_GAS = 8.314462618   # J/(mol*K)

class BatterySEIPINN:
    """
    Physics-informed model incorporating diffusion-controlled SEI growth and mechanical degradation.
    Simulates capacity fade, Li+ inventory consumption, and impedance rise over cycling.
    """
    def __init__(
        self,
        nominal_capacity_Ah: float = 2.5,
        electrode_area_m2: float = 0.25,
        sei_diffusivity_D_s: float = 1.0e-18,
        solvent_bulk_conc: float = 4500.0,
        molar_volume_sei: float = 1.3e-5
    ):
        self.Q0 = nominal_capacity_Ah
        self.A = electrode_area_m2
        self.D_s = sei_diffusivity_D_s
        self.c_s = solvent_bulk_conc
        self.V_sei = molar_volume_sei

    def compute_sei_flux_and_overpotential(
        self,
        c_rate: float,
        temperature_C: float,
        current_sei_thickness_nm: float
    ) -> Tuple[float, float, float]:
        """
        Calculates SEI side-reaction current density (j_sei) and overpotential.
        """
        temp_K = temperature_C + 273.15
        delta_m = max(1.0e-9, current_sei_thickness_nm * 1.0e-9)
        D_eff = self.D_s * math.exp(-35000.0 / (R_GAS * temp_K))
        
        # Stress-enhanced solvent permeability at elevated C-rates
        stress_factor = (c_rate ** 1.3)
        j_sei = (FARADAY * (D_eff * self.c_s / delta_m) * 1e-4) * (1.0 + 0.8 * stress_factor)
        d_delta_dt = (j_sei / FARADAY) * self.V_sei
        
        kappa_sei = 1.0e-6 # S/m (electronic conductivity)
        R_sei = delta_m / (kappa_sei * self.A)
        
        return float(j_sei), float(d_delta_dt), float(R_sei)

    def forecast_aging_trajectory(
        self,
        cycles: int = 500,
        c_rate: float = 1.0,
        temp_C: float = 25.0
    ) -> Dict[str, Any]:
        """
        Forecast battery capacity fade, SoH %, and SEI resistance over cycles.
        """
        delta_nm = 5.0 # Initial native SEI thickness in nm
        capacity_fade_Ah = 0.0
        soh_history = []
        cycle_duration_s = (3600.0 / max(0.01, c_rate)) * 2.0
        temp_factor = math.exp(0.03 * (temp_C - 25.0))
        
        for c in range(1, cycles + 1):
            j_sei, d_delta_dt, R_sei = self.compute_sei_flux_and_overpotential(c_rate, temp_C, delta_nm)
            q_lost_Ah = (j_sei * self.A * cycle_duration_s) / 3600.0
            
            # Coupled electrochemical SEI growth and chemomechanical fatigue crack growth
            crack_growth_nm = 0.08 * (c_rate ** 2.2) * temp_factor
            delta_nm += (d_delta_dt * cycle_duration_s) * 1.0e9 + crack_growth_nm
            q_lost_crack = (crack_growth_nm * 1e-9 / self.V_sei) * FARADAY * self.A / 3600.0
            capacity_fade_Ah += q_lost_Ah + q_lost_crack
            
            soh = max(0.0, min(100.0, (1.0 - (capacity_fade_Ah / self.Q0)) * 100.0))
            
            if c % 25 == 0 or c == cycles:
                soh_history.append({"cycle": c, "soh_pct": round(soh, 2)})
        
        return {
            "initial_capacity_Ah": self.Q0,
            "final_capacity_Ah": round(max(0.0, self.Q0 - capacity_fade_Ah), 3),
            "final_soh_pct": round(soh, 2),
            "final_sei_thickness_nm": round(delta_nm, 2),
            "final_r_sei_ohm": round(R_sei, 4),
            "final_resistance_mOhm": round(R_sei * 1000.0, 3),
            "end_of_life_reached": soh < 80.0,
            "c_rate": c_rate,
            "temperature_C": temp_C,
            "soh_trajectory": soh_history
        }
