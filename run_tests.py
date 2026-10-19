"""
Master Test Runner for Energy Storage PINN
"""

import sys
import unittest
from pathlib import Path

src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def run_suite():
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print(f"\nALL ENERGY-STORAGE-PINN TESTS PASSED ({result.testsRun}/{result.testsRun})!\n")
        return 0
    else:
        print(f"\nTEST FAILURES DETECTED: {len(result.failures)} failures, {len(result.errors)} errors.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_suite())
