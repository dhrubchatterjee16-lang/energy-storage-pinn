"""
Tests for Conformal Battery Uncertainty Quantification
"""

import unittest
from energy_storage.conformal import ConformalBatteryUQ

class TestConformal(unittest.TestCase):
    def test_soh_bounds(self):
        uq = ConformalBatteryUQ()
        res90 = uq.predict_soh_interval(predicted_soh_pct=88.5, confidence=0.90)
        res95 = uq.predict_soh_interval(predicted_soh_pct=88.5, confidence=0.95)

        self.assertLessEqual(res90["lower_bound_pct"], 88.5)
        self.assertGreaterEqual(res90["upper_bound_pct"], 88.5)
        self.assertGreaterEqual(res95["interval_width_pct"], res90["interval_width_pct"])

    def test_boundary_clamping(self):
        uq = ConformalBatteryUQ()
        res = uq.predict_soh_interval(predicted_soh_pct=99.0, confidence=0.95)
        self.assertLessEqual(res["upper_bound_pct"], 100.0)

if __name__ == "__main__":
    unittest.main()
