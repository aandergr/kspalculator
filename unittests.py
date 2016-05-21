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
    # TODO: have a very deep look to test_sflf_needed_fuel and test_sflf_performance correctness
    def test_sflf_needed_fuel(self):
        m_c = physics.sflf_needed_fuel([2500, 2000], [250, 320], [195,220], 15000, 50, 24000, 4500)
        self.assertAlmostEqual(m_c, 104716.64, places=1)
    def test_sflf_performance(self):
        r_dv, r_p, r_a_s, r_a_t, r_m_s, r_m_t, r_solid, r_op = \
                physics.sflf_performance([1000, 500], [250, 260], [150, 170],
                        [0,0], [0,0], [0,0], 10000, 7000, 100, 5000, 1000)
        self.assertListAlmostEqual(r_dv, [281.37, 718.62, 500.0, 19.68])
        self.assertListAlmostEqual(r_m_s, [22975.0, 17875.0, 13333.60, 10959.29])
        self.assertListAlmostEqual(r_m_t, [18975.0, 13333.60, 10959.29, 10875.0])
        self.assertListEqual(r_solid, [True, False, False, False])
        self.assertListEqual(r_op, [0, 0, 1, 1])
        r_dv, r_p, r_a_s, r_a_t, r_m_s, r_m_t, r_solid, r_op = \
                physics.sflf_performance([2000], [250], [150], [0], [0], [0],
                        10000, 11000, 200, 10000, 2000)
        self.assertListAlmostEqual(r_dv, [414.54, 1585.45, 73.16])
        self.assertListAlmostEqual(r_m_s, [32575.0, 22375.0, 11719.57])
        self.assertListAlmostEqual(r_m_t, [24575.0, 11719.57, 11375.0])
        self.assertListEqual(r_solid, [True, False, False])
        self.assertListEqual(r_op, [0, 0, 0])
        r_dv, r_p, r_a_s, r_a_t, r_m_s, r_m_t, r_solid, r_op = \
                physics.sflf_performance([100, 900, 500], [250, 250, 260], [150, 150, 170],
                        [0,0,0], [0,0,0], [0,0,0], 10000, 7000, 100, 5000, 1000)
        self.assertListAlmostEqual(r_dv, [100.0, 181.37, 718.62, 500.0, 19.68])
        self.assertListAlmostEqual(r_m_s, [22975.0, 21465.04, 17875.0, 13333.60, 10959.29])
        self.assertListAlmostEqual(r_m_t, [21465.04, 18975.0, 13333.60, 10959.29, 10875.0])
        self.assertListEqual(r_solid, [True, True, False, False, False])
        self.assertListEqual(r_op, [0, 1, 1, 2, 2])

main()
