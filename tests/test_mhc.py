"""
Tests for Marcus-Hush-Chidsey Kinetics & Electrodiffusion
"""

import unittest
from energy_storage.mhc_kinetics import MarcusHushChidseyKinetics, MHCParameters

class TestMHC(unittest.TestCase):
    def test_mhc_kinetics_electrodiffusion(self):
        mhc = MarcusHushChidseyKinetics()
        rate_pos = mhc.compute_mhc_rate(overpotential_v=0.15)
        rate_neg = mhc.compute_mhc_rate(overpotential_v=-0.15)
        self.assertNotEqual(rate_pos, 0.0)
        self.assertNotEqual(rate_neg, 0.0)

        profile = mhc.solve_1d_nernst_planck(applied_voltage_v=0.20)
        self.assertEqual(len(profile.spatial_nodes_m), 30)
        self.assertEqual(len(profile.concentration_profile_mol_m3), 30)
        self.assertGreaterEqual(profile.entropy_generation_rate_w_k, 0.0)

if __name__ == "__main__":
    unittest.main()
