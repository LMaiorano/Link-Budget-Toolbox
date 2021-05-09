#!/usr/bin/env python
# -*- coding: utf-8 -*-


class LinkElement:
    ''' Basic Element that only has a gain and/or loss. 
    
    If parameters are used, then the respective child Element should be created 
    which will process the parameters accordingly
    '''
    def __init__(self, name, linktype, gain):
        # The basic attributes that all types Elements must have
        self.name = name
        self.linktype = linktype
        self.gain = gain

    def get_gain(self):
        # Return net gain (used by final process step)
        return self.gain


class TxElement(LinkElement):
    '''Specific type of LinkElement, that depends on parameters instead of a 
    single gain/loss value

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

    def process(self)
        # Tx Specific calculations
        self.gain = sum(self.parameters)




class FsElement(LinkElement):
    '''Specific type of LinkElement, that depends on parameters instead of a 
    single gain/loss value

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, parameters):
        # Run the initialization of parent LinkElement, with gain and loss 
        #   set initially as unknown (None)
        super().__init__(name, gain=None, loss=None)

        # Add attributes that are unique to TxElement
        self.parameters = parameters
        self.process()

    def process(self)
        # Tx Specific calculations
        self.gain = sum(self.parameters)
        self.loss = sum(self.parameters)


# We would create as 


# Example Usage
basic_elem = LinkElement('Cable', gain=5, loss=0)

tx_elem = TxElement("Ground to S/C", parameters=tx_parameters)

fs_elem = FsElement("Space", parameters=tx_parameters)


# Sum of all gains
tot_gain = basic_elem.get_gain() + tx_elem.get_gain() + fs_elem.get_gain()