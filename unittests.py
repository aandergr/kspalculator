#!/usr/bin/env python3

from unittest import TestCase, main

import physics

class TestPhysics(TestCase):
    def assertListAlmostEqual(self, first, second):
        if len(first) != len(second):
            raise self.failureException("List length mismatch")
        for i in range(len(first)):
            self.assertAlmostEqual(first[i], second[i], places=1)
    def test_lf_needed_fuel(self):
        m_c = physics.lf_needed_fuel([1750, 580, 310, 792], 4*[345], 1500)
        self.assertAlmostEqual(m_c, 3378.94, places=1)
        m_c = physics.lf_needed_fuel([1750, 580, 310, 792], 3*[345]+[300], 1500)
        self.assertAlmostEqual(m_c, 3625.64, places=1)
    def test_lf_performance(self):
        r_dv, r_p, r_a_s, r_a_t, r_m_s, r_m_t, r_solid, r_op = \
                physics.lf_performance([1750,580,310,792], 4*[345], 4*[60000], 4*[0], 2005, 5000)
        self.assertListAlmostEqual(r_dv, [1750, 580, 310, 792, 171.56])
        self.assertListEqual(r_p, 5*[0])
        self.assertListEqual(r_solid, 5*[False])
        self.assertListEqual(r_op, list(range(4))+[3])
        self.assertListAlmostEqual(r_a_s, [7.86, 13.19, 15.65, 17.15, 21.68])
        self.assertListAlmostEqual(r_a_t, [13.19, 15.65, 17.15, 21.68, 22.81])
        self.assertListAlmostEqual(r_m_s, [7630.0, 4548.69, 3832.08, 3496.57, 2766.80])
        self.assertListAlmostEqual(r_m_t, [4548.69, 3832.08, 3496.57, 2766.80, 2630.0])
    def test_sflf_needed_fuel(self):
        # This doesn't test all cases. Current sflf_needed_fuel()
        # implementation has been heavily tested by hand. In case we change
        # something, we should invent good unit tests.
        m_c = physics.sflf_needed_fuel([2500, 2000], [250, 320], [195,220], 15000, 50, 24000, 4500)
        self.assertAlmostEqual(m_c, 104716.64, places=1)

main()
