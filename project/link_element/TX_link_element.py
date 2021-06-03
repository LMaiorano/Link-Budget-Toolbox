# -*- coding: utf-8 -*-
"""
Created on Tue May 11 12:32:54 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np


class TX_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Transmitting Channel Antenna,
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
                Transmission wavelength in [m],
            'w0': int
                    The waist radius of the antenna in [m]
    Methods:
    -------
    process()
        Updates the Transmitting Channel gain
    calc_efficiencygain()
        Returns the calculated peak antenna gain using parameter_set_1
    calc_waistgain()
        Returns the calculated antenna gain using parameter_set_2
    
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
                    Transmission wavelength in [m],
                'w0': int
                    The waist radius of the antenna in [m]
        '''
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='TX', gain = gain)
        # Add attributes that are unique to TxElement
        self.input_type = input_type

        self.efficiency = parameters.get('antenna_efficiency', None)
        self.diameter = parameters.get('antenna_diameter', None)
        self.wavelength = parameters.get('wavelength', None)
        self.w0 = parameters.get('waist_radius', None)
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
        # Check which calculation is required
        if self.input_type == "parameter_set_1":
            Gtpeak = self.calc_efficiencygain()
            self.gain = self.dB(Gtpeak)
        elif self.input_type == "parameter_set_2":
            Gt = self.calc_waistgain()
            self.gain = self.dB(Gt)

    def calc_efficiencygain(self):
        '''Returns the Transmitting Channel antenna gain using the efficiency
        
        Uses parameter_set_1, consisting of the antenna efficiency, 
        its diameter and the wavelength of transmission for calculating the 
        receiving channel antenna gain. 

        Returns
        -------
        float
            Receiving Channel antenna gain

        '''
        Gtpeak = self.efficiency*(np.pi*self.diameter/self.wavelength)**2  #[-], peak gain
        # TODO: does this needs to be in dB and is it?
        return Gtpeak

    def calc_waistgain(self):
        '''Returns the Transmitting Channel antenna gain using the waist radius
        
        Uses parameter_set_2, consisting of the waist radius and the 
        wavelength of transmission for calculating the receiving channel
        antenna gain. 

        Returns
        -------
        float
            Receiving Channel antenna gain

        '''
        Gt = 2*(2*np.pi*self.w0/self.wavelength)**2
        # TODO: does this needs to be in dB and is it?
        return Gt

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    # print('Good Busy Willem! :P')

    params = {'antenna_efficiency': 8,
              'antenna_diameter': 10,
              'wavelength': 1550e-9,
              'waist_radius': 24.7e-3}
    
    testelement = TX_LinkElement('test', 'parameter_set_2', 10, params).gain
    print(testelement)