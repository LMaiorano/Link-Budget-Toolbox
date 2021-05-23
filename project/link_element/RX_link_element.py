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
    def __init__(self, name, input_type, gain, parameters):
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='RX', gain = gain)
        # Add attributes that are unique to RxElement
        self.input_type = input_type

        self.efficiency = parameters.get('antenna_efficiency', None)
        self.diameter = parameters.get('antenna_diameter', None)
        self.wavelength = parameters.get('wavelength', None)

        if self.input_type != 'gain_loss':
            self.process()
            

        
    def process(self):
        # RX Specific calculations, first checks if any calculations are 
        # required or if gain_loss is directly given and needs to be usec. 
        # does not cover specific antenna models yet
        if self.input_type == "parameter_set_1":
            Gr = self.efficiency*(np.pi*self.diameter/self.wavelength)**2  #[-], peak gain
            self.gain = self.dB(Gr)
        # elif self.input_type == "gain_loss":
        #     self.gain = self.gain 

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    print('Testcase:')
    
    testparameters = {'antenna_efficiency':0.7,
                      'antenna_diameter':10,
                      'wavelength':1}
    testelement = RX_LinkElement('test', 'parameter_set_1', 30, testparameters)
    print(testelement)
    testelement.process()
    print(testelement)