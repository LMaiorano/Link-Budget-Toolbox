# -*- coding: utf-8 -*-
"""
Created on Sun May 23 18:46:47 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np
# TODO: Populate this element with either the equation given in space instrumentation course or the tables from intelsat in microsat course

class Atmospheric_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Atmospheric loss,
    that can depend a single gain/loss value or on parameters instead. as
    dictated by the input_type value

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, input_type, gain, parameters):
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='Atmospheric', gain = gain)
        # Add attributes that are unique to TxElement
        self.input_type = input_type

        # self.efficiency = parameters.get('antenna_efficiency', None)
        # self.diameter = parameters.get('antenna_diameter', None)
        # self.wavelength = parameters.get('wavelength', None)

        # if self.input_type != 'gain_loss':
        #     self.process()