# -*- coding: utf-8 -*-
"""
Created on Tue May 11 13:15:08 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np

class GS_RX_Ant_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Downlink Ground Station Antenna 
    Gain, that depends on parameters instead of a single gain/loss value

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, antenna_efficiency, antenna_diameter, 
                 wavelength):
        # Run the initialization of parent LinkElement, with gain and loss 
        #   set initially as unknown (None)
        super().__init__(name, linktype='RX', gain=0)

        # Add attributes that are unique to RxElement
        self.efficiency = antenna_efficiency
        self.diameter = antenna_diameter
        
        #FIX: wavelength is not unique to RxElement?
            
        self.wavelength = wavelength
        self.process()

    def process(self, efficiency, diameter, wavelength):
        # GS_RX_Antenna Specific calculations, does not cover specific antenna models yet
        Gr = efficiency*(diameter*np.pi/wavelength)**2  #[-], receiver gain
        self.gain = dB(Gr)



if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    print('Good Busy Willem! :P')