# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 13:49:50 2021

@author: Willem van Lynden
"""
import unittest
from project.link_element import FREE_SPACE_LinkElement, RX_LinkElement, \
    TX_LinkElement, Atmospheric_LinkElement

Re = 6371e3     #[m]
c = 299792458   #[m/s]

class FREE_SPACE_LinkElementTest(unittest.TestCase):
    def setup(self):
        testparameters = {'distance': 600e3,
                      'sc_altitude': 500e3,
                      'gs_altitude': 0,
                      'elevation_angle': 10,
                      'wavelength': c/2e6}

        out_val = FREE_SPACE_LinkElement('test', 'parameter_set_2',0, testparameters).gain
        print(out_val)
        ref_val = 103 # Should be -103

        self.assertAlmostEqual(ref_val, out_val,8)

if __name__ == '__main__':
    unittest.main()
