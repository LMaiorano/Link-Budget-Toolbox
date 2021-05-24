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
        '''Receiving Channel Link Element
        
        Assigns all attributes such as the name, wether a gain is given
        directly or needs to be calculated, said gain and the parameters list

        Parameters
        ----------
       name : str
            Defines the type of link element.
        input_type : str
            Defines wether a gain/loss is given or a parameter set is used.
        gain : int
            The gain or loss in Decibel of this link element in the case it is
            known or given. Losses are given as negative gains.
        parameters : dict
            Parameters used: Antenna Efficiency[1 = 100%], Antenna diameter[m],
            Transmission wavelength[m].

        Returns
        -------
        None.

        '''
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='RX', gain = gain)
        # Add attributes that are unique to RxElement
        self.input_type = input_type
        # Add attributes that are unique parameters to RxElement
        self.efficiency = parameters.get('antenna_efficiency', None)
        self.diameter = parameters.get('antenna_diameter', None)
        self.wavelength = parameters.get('wavelength', None)
        # check if gain/loss is given directly or calculations are required
        if self.input_type != 'gain_loss':
            self.process()
            

        
    def process(self):
        '''
        Free Space Path Loss Specific calculations, it checks which parameter
        set needs to be used and uses the respective required calculations.
        Parameter_set_1 uses the antenna efficiency, its diameter and the
        wavelength of transmission for calculating the receiving antenna gain.

        Returns
        -------
        self.gain: The updated gain of the RX_LinkElement object.

        '''
        # RX Specific calculations, first checks if any calculations are 
        # required or if gain_loss is directly given and needs to be usec. 
        # does not cover specific antenna models yet
        # TODO: include specific antenna models
        if self.input_type == "parameter_set_1":
            self.calc_1()
        
    def calc_1(self):
        Gr = self.efficiency*(np.pi*self.diameter/self.wavelength)**2  #[-], peak gain
        self.gain = self.dB(Gr)

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