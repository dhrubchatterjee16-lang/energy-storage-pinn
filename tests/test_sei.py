"""
Tests for Battery SEI Growth & Aging PINN
"""

import unittest
from energy_storage.sei_pinn import BatterySEIPINN

class TestBatterySEI(unittest.TestCase):
    def test_aging_degradation(self):
        model = BatterySEIPINN(nominal_capacity_Ah=2.5)
        res = model.forecast_aging_trajectory(cycles=50, c_rate=1.0, temp_C=25.0)

        self.assertEqual(res["initial_capacity_Ah"], 2.5)
        self.assertLess(res["final_capacity_Ah"], 2.5)
        self.assertLessEqual(res["final_soh_pct"], 100.0)
        self.assertGreaterEqual(res["final_soh_pct"], 50.0)
        self.assertGreater(res["final_sei_thickness_nm"], 5.0)
        self.assertGreater(res["final_resistance_mOhm"], 0.0)

    def test_c_rate_acceleration(self):
        model = BatterySEIPINN(nominal_capacity_Ah=2.5)
        res_low = model.forecast_aging_trajectory(cycles=30, c_rate=0.5)
        res_high = model.forecast_aging_trajectory(cycles=30, c_rate=2.5)

        self.assertGreater(res_high["final_sei_thickness_nm"], res_low["final_sei_thickness_nm"])

    def test_temperature_arrhenius_effect(self):
        model = BatterySEIPINN(nominal_capacity_Ah=2.5)
        res_25c = model.forecast_aging_trajectory(cycles=30, temp_C=25.0)
        res_45c = model.forecast_aging_trajectory(cycles=30, temp_C=45.0)

        self.assertGreater(res_45c["final_sei_thickness_nm"], res_25c["final_sei_thickness_nm"])

if __name__ == "__main__":
    unittest.main()
