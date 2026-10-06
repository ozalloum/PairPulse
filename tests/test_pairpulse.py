import unittest

import numpy as np

from pairpulse import (PulseTrain, SauterPulse, sauter_exact_occupation,
                       solve_dirac_mode, solve_qke_mode)


class PairPulseTests(unittest.TestCase):
    def test_sauter_mode_methods_match_exact_solution(self):
        pulse = SauterPulse(0.3, 2.0)
        exact = sauter_exact_occupation(0.0, pulse)
        direct = solve_dirac_mode(0.0, pulse).occupation
        kinetic = solve_qke_mode(0.0, pulse).occupation
        self.assertLess(abs(direct - exact), 2e-9)
        self.assertLess(abs(kinetic - exact), 2e-9)

    def test_qke_invariant_and_fermion_probability_range(self):
        result = solve_qke_mode(0.2, SauterPulse(0.5, 1.5))
        self.assertLess(result.diagnostic, 1e-8)
        self.assertGreaterEqual(result.occupation, 0.0)
        self.assertLessEqual(result.occupation, 1.0)

    def test_zero_field_has_zero_occupation(self):
        pulse = SauterPulse(0.0, 1.0)
        self.assertLess(solve_dirac_mode(0.4, pulse).occupation, 1e-12)
        self.assertEqual(solve_qke_mode(0.4, pulse).occupation, 0.0)
        self.assertEqual(sauter_exact_occupation(0.4, pulse), 0.0)

    def test_pulse_train_is_superposed(self):
        first, second = SauterPulse(0.2, 1.0, -1.0), SauterPulse(0.1, 0.5, 1.0)
        train = PulseTrain([first, second])
        self.assertTrue(np.isclose(train.field(0.0), first.field(0.0) + second.field(0.0)))
        self.assertTrue(np.isclose(train.potential(0.0), first.potential(0.0) + second.potential(0.0)))


if __name__ == "__main__":
    unittest.main()

