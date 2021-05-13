# -*- coding: utf-8 -*-
"""
Created on Tue May 11 12:32:54 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np

class SC_TX_Ant_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Downlink Spacecraft Antenna Gain,
    that depends on parameters instead of a single gain/loss value

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, antenna_efficiency, antenna_diameter):
        # Run the initialization of parent LinkElement, with gain and loss 
        #   set initially as unknown (None)
        # TODO: Make sure gain is included as input and not set to zero but updated through process if other params are
        # given
        # TODO: base calculation methods on input_type given (only gain_loss/parameter set x/ param set y etc..
        # TODO: change class name to link_type name
        super().__init__(name, linktype='SC_TX_ANT', gain=0)

        # Add attributes that are unique to TxElement
        self.efficiency = antenna_efficiency
        self.diameter = antenna_diameter

    def process(self, wavelength):
        # SC_Tx_Antenna Specific calculations, using general Gpeak
        #   formulation. Does not cover specific antenna models yet
        Gtpeak = self.efficiency*(np.pi*self.diameter/wavelength)**2  #[-], peak gain
        self.gain = self.dB(Gtpeak)



if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    print('Good Busy Willem! :P')
    
    testelement = SC_TX_Ant_LinkElement('test', 0.5, 1)
    print(testelement)
    testelement.process(1)
    print(testelement)