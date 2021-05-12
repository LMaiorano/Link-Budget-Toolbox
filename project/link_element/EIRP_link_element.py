# -*- coding: utf-8 -*-
"""
Created on Sun May  9 14:15:31 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement

class EIRPElement(LinkElement):
    '''Specific type of LinkElement for the EIRP of the spacecraft,
    that depends on parameters instead of a single gain/loss value

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, parameters):
        # Run the initialization of parent LinkElement, with gain and loss 
        #   set initially as unknown (None)
        super().__init__(name, linktype='TX', gain=0)

        # Add attributes that are unique to TxElement
        self.parameters = parameters
        self.process()

    def process(self):
        # Tx Specific calculations
        self.gain = sum(self.parameters)



if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    print('Good Busy Willem! :P')