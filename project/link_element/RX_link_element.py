# -*- coding: utf-8 -*-
"""
Created on Tue May 11 13:15:08 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np

class RX_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Receiving Antenna,
    that can depend a single gain/loss value or on parameters instead. as
    dictated by the input_type value

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, input_type, gain, antenna_efficiency, antenna_diameter, wavelength):
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='RX', gain = 0)
        # Add attributes that are unique to RxElement
        # TODO: figure out if giving wavelength isn' causing problems
        self.input_type = input_type
        self.gain = gain
        self.efficiency = antenna_efficiency
        self.diameter = antenna_diameter
        self.wavelength = wavelength
        
    def process(self):
        # RX Specific calculations, first checks if any calculations are 
        # required or if gain_loss is directly given and needs to be usec. 
        # does not cover specific antenna models yet
        if self.input_type == "parameter_set_1":
            Gr = self.efficiency*(np.pi*self.diameter/self.wavelength)**2  #[-], peak gain
            self.gain = self.dB(Gr)
        elif self.input_type == "gain_loss":
            self.gain = self.gain 

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    print('Testcase:')
    
    testelement = RX_LinkElement('test', 'parameter_set_1', 30, 0.7, 10, 1)
    print(testelement)
    testelement.process()
    print(testelement)