# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 13:49:50 2021

@author: Willem van Lynden
"""
# TODO: test this with DELFT values as also validation
import unittest
from project.link_element import FREE_SPACE_LinkElement, RX_LinkElement, \
    TX_LinkElement, Atmospheric_LinkElement

Re = 6371e3     #[m]
c = 299792458   #[m/s]

class FREE_SPACE_LinkElementTest(unittest.TestCase):
    def test_outcome(self):
        testparameters = {'distance': 600e3,
                      'sc_altitude': 500e3,
                      'gs_altitude': 0,
                      'elevation_angle': 10,
                      'wavelength': c/2e6}

        out_val = FREE_SPACE_LinkElement('test', 'parameter_set_2',0, testparameters).gain
        print(out_val)
        ref_val = -103 # Should be -103

        self.assertAlmostEqual(ref_val, out_val,0)

class RX_LinkElementTest(unittest.TestCase):
    def test_outcome(self):
        testparameters = {'antenna_efficiency':0.7,
                      'antenna_diameter':10,
                      'wavelength':1}

        out_val = RX_LinkElement('test', 'parameter_set_1', 30, testparameters).gain
        print(out_val)
        ref_val = 691 # Should be 691

        self.assertAlmostEqual(ref_val, out_val,0)

class TX_LinkElementTest(unittest.TestCase):
    def test_outcome(self):
        testparameters = {'antenna_efficiency': 8,
              'antenna_diameter': 10,
              'wavelength': 1550e-9,
              'waist_radius': 24.7e-3}

        out_val = TX_LinkElement('test', 'parameter_set_2', 30, testparameters).gain
        print(out_val)
        ref_val = 103 # Should be 103

        self.assertAlmostEqual(ref_val, out_val,0)

class Atmospheric_LinkElementTest(unittest.TestCase):
    def test_outcome(self):
        testparameters = {'air_temperature': 15+273.15,
                      'air_pressure': 101300,
                      'water_vapor_content': 7.5*1e-3,
                      'wavelength': c/2e6,
                      'elevation_angle': 5}

        out_val = Atmospheric_LinkElement('test', 'parameter_set_1', 30, testparameters).gain
        print(out_val)
        ref_val = -0.4 # Should be -0.4

        self.assertAlmostEqual(ref_val, out_val,0)










if __name__ == '__main__':
    unittest.main()
