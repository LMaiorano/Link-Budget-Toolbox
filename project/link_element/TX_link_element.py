# -*- coding: utf-8 -*-
"""
Created on Tue May 11 12:32:54 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np
<<<<<<< HEAD
=======

>>>>>>> 721fcab70754d728427cc5b286f171c83961c1d0

class TX_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Transmitting Antenna,
    that can depend a single gain/loss value or on parameters instead. as
    dictated by the input_type value

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, input_type, gain, parameters):
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='TX', gain = gain)
        # Add attributes that are unique to TxElement
        # TODO: figure out if giving wavelength isn' causing problems
        self.input_type = input_type

        try:
            self.efficiency = parameters['antenna_efficiency']
            self.diameter = parameters['antenna_diameter']
            self.wavelength = parameters['wavelength']

            self.process()

        except KeyError as key:
            print(f'Missing parameter: {key}. Unable to calculate gain with parameters, using default')

        

        
    def process(self):
        # TX Specific calculations, first checks if any calculations are 
        # required or if gain_loss is directly given and needs to be usec. 
        # does not cover specific antenna models yet

        if self.input_type == "parameter_set_1":
            Gtpeak = self.efficiency*(np.pi*self.diameter/self.wavelength)**2  #[-], peak gain
            self.gain = self.dB(Gtpeak)
        # elif self.input_type == "gain_loss":
        #     self.gain = self.gain

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    # print('Good Busy Willem! :P')

    params = {'antenna_efficiency': 8,
              'antenna_diameter': 10,
              'wavelength': 0}
    
    testelement = TX_LinkElement('test', 'parameter_set_1', 10, params).gain
    print(testelement)