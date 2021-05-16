# -*- coding: utf-8 -*-
"""
Created on Fri May 14 14:28:25 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np
Re = 6371e3     #[m]

class Free_Space_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Free Space Loss,
    that can depend a single gain/loss value or on parameters instead. as
    dictated by the input_type value. 

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, input_type, gain, distance, sc_altitude, gs_altitude, angle, wavelength):
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='FREE_SPACE', gain = 0)
        # Add attributes that are unique to TxElement
        # TODO: figure out if giving wavelength isn' causing problems
        self.input_type = input_type
        self.gain = gain
        self.distance = distance
        self.wavelength = wavelength
        self.sc_altitude = sc_altitude
        self.gs_altitude = gs_altitude
        self.angle = angle      #[deg]
        
    def process(self):
        # Free Space Path Loss Specific calculations, first checks if any 
        # calculations are required or if gain_loss is directly given and 
        # needs to be used. parameter set 1 gives the distance directly, while
        # parameter set 2 first calculates it with the altitudes of the tx and
        # rx elements, and the angle from horizon as taken from rx (<90deg)
        # Requires the distance between point of Transmission and Reception
        
        # TODO: How to define negativity of Losses? parameters automatically 
        # give it, but if gain/loss is pregiven, should it be given as 
        # negative input or be made a negative input later?
            
        if self.input_type == "parameter_set_1":
            S = self.distance   #[m]
            Ls = (self.wavelength/(4*np.pi*S))**2 #[-], Free Space Loss, will give negative Decibel as it is smaller than 1
            self.gain = self.dB(Ls)
        elif self.input_type == "parameter_set_2":
            #Use the sine rule to calculate the distance
            # TODO: also make this work for if the angle between elements is
            # <90deg
            
            # TODO: Breaks at angle = 90 currently
            r_sc = self.sc_altitude + Re    #[m]
            r_gs = self.gs_altitude + Re    #[m]
            a = 90+self.angle               #[deg]
            sineratio = r_sc/np.sin(np.deg2rad(a))
            b = np.rad2deg(np.arcsin(r_gs/sineratio))  #[deg]
            c = 180-a-b                     #[deg]
            S = sineratio*np.sin(np.deg2rad(c))         #[m]
            Ls = (self.wavelength/(4*np.pi*S))**2 #[-], Free Space Loss, will give negative Decibel as it is smaller than 1
            self.gain = self.dB(Ls)
        elif self.input_type == "gain_loss":
            self.gain = -self.gain

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    print('Good Busy Willem! :P')
    
    testelement = Free_Space_LinkElement('test', 'parameter_set_2', 10, 100e3, 90e3,0,89,1)
    print(testelement)
    testelement.process()
    print(testelement)