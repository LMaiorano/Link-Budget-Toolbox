# -*- coding: utf-8 -*-
"""
Created on Tue May 11 12:32:54 2021

@author: Willem van Lynden
"""
from .generic_element import LinkElement
import numpy as np

class SC_TX_Ant_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Downlink Spacecraft Antenna Gain,
    that depends on parameters instead of a single gain/loss value

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, antenna_efficiency, antenna_diameter, 
                 wavelength):
        # Run the initialization of parent LinkElement, with gain and loss 
        #   set initially as unknown (None)
        super().__init__(name, linktype='TX', gain=0)

        # Add attributes that are unique to TxElement
        self.efficiency = antenna_efficiency
        self.diameter = antenna_diameter
        
        #FIX: wavelength is not unique to TxElement?
            
        self.wavelength = wavelength
        self.process()

    def process(self, efficiency, diameter, wavelength):
        # SC_Tx_Antenna Specific calculations, using general Gpeak
        #   formulation. Does not cover specific antenna models yet
        Gpeak = efficiency*(np.pi*diameter/wavelength)**2  #[-], peak gain
        self.gain = 10*np.log10(Gpeak/1)



if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    print('Good Busy Willem! :P')