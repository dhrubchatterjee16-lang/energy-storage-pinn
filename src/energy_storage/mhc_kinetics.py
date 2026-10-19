"""
Marcus-Hush-Chidsey (MHC) Interfacial Kinetics & Electrodiffusion
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np
from scipy.integrate import quad

@dataclass
class MHCParameters:
    reorganization_energy_ev: float = 0.85
    standard_rate_constant_m_s: float = 2.5e-6
    temperature_k: float = 298.15
    transfer_coefficient_alpha: float = 0.5

@dataclass
class ElectrodiffusionProfile:
    spatial_nodes_m: List[float]
    concentration_profile_mol_m3: List[float]
    potential_profile_v: List[float]
    current_density_a_m2: float
    mhc_rate_constant_s_inv: float
    mass_transfer_overpotential_v: float
    entropy_generation_rate_w_k: float

class MarcusHushChidseyKinetics:
    """
    Marcus-Hush-Chidsey (MHC) kinetics for battery intercalation and interface electron transfer.
    Accounts for Fermi-Dirac continuum of states, preventing non-physical exponential runaway.
    """
    def __init__(self, params: Optional[MHCParameters] = None):
        self.params = params or MHCParameters()
        self.k_b_ev = 8.617333262145e-5
        self.faraday = 96485.33212
        self.r_gas = 8.314462

    def compute_mhc_rate(self, overpotential_v: float) -> float:
        """
        Calculates normalized MHC rate constant via numerical quadrature of Fermi-Dirac integral:
        k_MHC(eta) = k0 * integral [ exp(- (x - lambda +/- eta)^2 / (4 * lambda * k_B * T)) / (1 + exp(x)) dx ]
        """
        temp = self.params.temperature_k
        kt_ev = self.k_b_ev * temp
        lam_ev = self.params.reorganization_energy_ev
        eta = overpotential_v

        denom = 4.0 * lam_ev * kt_ev

        def integrand_reduction(x):
            arg = - ((x - lam_ev / kt_ev + eta / kt_ev) ** 2) / (denom / (kt_ev ** 2))
            fermi = 1.0 / (1.0 + math.exp(np.clip(x, -60.0, 60.0)))
            return math.exp(np.clip(arg, -60.0, 0.0)) * fermi

        def integrand_oxidation(x):
            arg = - ((x - lam_ev / kt_ev - eta / kt_ev) ** 2) / (denom / (kt_ev ** 2))
            fermi = 1.0 / (1.0 + math.exp(np.clip(x, -60.0, 60.0)))
            return math.exp(np.clip(arg, -60.0, 0.0)) * fermi

        val_red, _ = quad(integrand_reduction, -25.0, 25.0, limit=40)
        val_ox, _ = quad(integrand_oxidation, -25.0, 25.0, limit=40)

        net_rate = self.params.standard_rate_constant_m_s * (val_red - val_ox)
        return float(net_rate)

    def solve_1d_nernst_planck(
        self,
        applied_voltage_v: float = 0.25,
        bulk_concentration_mol_m3: float = 1000.0,
        diffusion_coefficient_m2_s: float = 2.5e-10,
        boundary_layer_thickness_m: float = 50e-6,
        n_nodes: int = 30
    ) -> ElectrodiffusionProfile:
        """
        Solves coupled 1D steady-state Nernst-Planck electrodiffusion with MHC boundary condition.
        """
        temp = self.params.temperature_k
        f = self.faraday
        r = self.r_gas
        d = diffusion_coefficient_m2_s
        l_bl = boundary_layer_thickness_m

        x_nodes = np.linspace(0, l_bl, n_nodes)
        j_lim = f * d * bulk_concentration_mol_m3 / l_bl

        mhc_rate = self.compute_mhc_rate(applied_voltage_v)
        surface_flux = mhc_rate * bulk_concentration_mol_m3
        j_actual = np.clip(surface_flux * f, -0.92 * j_lim, 0.92 * j_lim)

        c_surface = max(1e-3, bulk_concentration_mol_m3 - (j_actual / (f * d)) * l_bl)
        c_profile = [float(c_surface + (bulk_concentration_mol_m3 - c_surface) * (x / l_bl)) for x in x_nodes]

        eta_conc = (r * temp / f) * math.log(max(1e-4, c_surface / bulk_concentration_mol_m3))
        kappa = 1.0
        pot_profile = [float(applied_voltage_v - (j_actual / kappa) * x + eta_conc * (1.0 - x / l_bl)) for x in x_nodes]

        s_gen = max(0.0, (abs(j_actual) * abs(applied_voltage_v)) / temp)

        return ElectrodiffusionProfile(
            spatial_nodes_m=[round(float(x), 8) for x in x_nodes],
            concentration_profile_mol_m3=[round(float(c), 3) for c in c_profile],
            potential_profile_v=[round(float(p), 4) for p in pot_profile],
            current_density_a_m2=round(float(j_actual), 3),
            mhc_rate_constant_s_inv=round(float(mhc_rate), 6),
            mass_transfer_overpotential_v=round(float(eta_conc), 4),
            entropy_generation_rate_w_k=round(float(s_gen), 5)
        )
