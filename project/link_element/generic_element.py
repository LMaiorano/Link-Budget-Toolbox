#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

class LinkElement:
    ''' Basic Element that only has a gain and/or loss. 
    
    If parameters are used, then the respective child Element should be created 
    which will process the parameters accordingly
    '''
    LINK_TYPES = ['TX', 'FREE_SPACE', 'RX'] # JUST AN EXAMPLE

    def __init__(self, name, linktype, gain):
        # The basic attributes that all types Elements must have
        self.name = name
        self.linktype = linktype
        self.gain = gain

    def __str__(self):
        return f'{self.name} is a {self.linktype} LinkElement, with a gain of ' \
               f'{self.gain}dB'
               
    def dB(self,value):
        #Return value in decibels (used in all elements for defining the gain)
        return 10*np.log10(value/1)



# We would create as 

if __name__ == '__main__':

    # Example Usage
    basic_elem = LinkElement('Cable', linktype="CABLE",  gain=5)

    # tx_elem = TxElement("Ground to S/C", parameters=tx_parameters)
    #
    # fs_elem = FsElement("Space", parameters=tx_parameters)


    # Sum of all gains
    # tot_gain = basic_elem.get_gain() + tx_elem.get_gain() + fs_elem.get_gain()

    print('finished')