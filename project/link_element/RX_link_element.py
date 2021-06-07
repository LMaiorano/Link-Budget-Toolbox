# -*- coding: utf-8 -*-
"""
Created on Tue May 11 13:15:08 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np

class RX_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Receiving Channel Antenna,
    that can depend a single gain/loss value or on parameters instead. as
    dictated by the input_type value

    ...
    
    Attributes
    ----------
    name : str
        Defines the type of link element.
    input_type : str
        Defines wether a gain/loss is given or a parameter set is used.
    gain : int
        The gain or loss in Decibel of this link element in the case it is
        known or given. Losses are given as negative gains.
    parameters : dict
        Contains parameters used: 
            'antenna_efficiency': int
                Efficiency of the antenna [1 = 100%], 
            'antenna_diameter': int
                The diameter of the antenna dish in[m],
            'wavelength': int
                Transmission wavelength in [m]
    Methods:
    -------
    process()
        Updates the Receiving Channel gain
    calc_efficiencygain()
        Returns the calculated antenna gain using parameter_set_1
    
    Although not defined here, methods "dB(value)", "get_gain()" and 
    "get_loss()" are automatically inherited and will also work
    '''
    def __init__(self, name, input_type, gain, parameters):
        '''
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
            Contains parameters used: 
                'antenna_efficiency': int
                    Efficiency of the antenna [1 = 100%], 
                'antenna_diameter': int
                    The diameter of the antenna dish in[m],
                'wavelength': int
                    Transmission wavelength in [m]
        '''
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='RX', gain = gain)
        # Add attributes that are unique to Rx_LinkElement
        self.input_type = input_type
        # Add attributes that are unique parameters to RxElement
        self.efficiency = parameters.get('antenna_efficiency', None)
        self.diameter = parameters.get('antenna_diameter', None)
        self.wavelength = parameters.get('wavelength', None)
        # check if gain/loss is given directly or calculations are required
        if self.input_type != 'gain_loss':
            self.process()
            

        
    def process(self):
        '''Updates the Receiving Channel antenna gain
        Checks which parameter set needs to be used and calls the respective 
        required calculations to obtain the gain and update the gain of the 
        RX_LinkElement object.

        Returns
        -------
        None

        '''
        # TODO: include specific antenna models
        if self.input_type == "parameter_set_1":
            Gr = self.calc_efficiencygain()
            self.gain = self.dB(Gr)
        
    def calc_efficiencygain(self):
        '''Returns the Receiving Channel antenna gain using the efficiency
        
        Uses parameter_set_1, consisting of the antenna efficiency, 
        its diameter and the wavelength of transmission for calculating the 
        receiving channel antenna gain. 

        Returns
        -------
        float
            Receiving Channel antenna gain

        '''
        Gr = self.efficiency*(np.pi*self.diameter/self.wavelength)**2  #[-], peak gain
        return Gr

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    print('Testcase:')
    
    testparameters = {'antenna_efficiency':0.7,
                      'antenna_diameter':10,
                      'wavelength':1}
    testelement = RX_LinkElement('test', 'parameter_set_1', 30, testparameters)
    print(testelement.gain)
    