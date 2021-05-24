# -*- coding: utf-8 -*-
"""
Created on Fri May 14 14:28:25 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np
Re = 6371e3     #[m]

class FREE_SPACE_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Free Space Loss,
    that can depend a single gain/loss value or on parameters instead. as
    dictated by the input_type value. 

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, input_type, gain, parameters):
        '''short name
        
        summary
        
        Parameters
        ----------
        name : TYPE
            DESCRIPTION.
        input_type : TYPE
            DESCRIPTION.
        gain : TYPE
            DESCRIPTION.
        distance : TYPE
            DESCRIPTION.
        sc_altitude : TYPE
            DESCRIPTION.
        gs_altitude : TYPE
            DESCRIPTION.
        angle : TYPE
            DESCRIPTION.
        wavelength : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='FREE_SPACE', gain = gain)
        # Add attributes that are unique to TxElement
        self.input_type = input_type

        self.distance = parameters.get('distance', None)
        self.sc_altitude = parameters.get('sc_altitude', None)
        self.gs_altitude = parameters.get('gs_altitude', None)
        self.angle = parameters.get('angle', None)     #[deg]
        self.wavelength = parameters.get('wavelength', None)

        if self.input_type != 'gain_loss':
            self.process()

        
    def process(self):
        '''
        # Free Space Path Loss Specific calculations, first checks if any 
        # calculations are required or if gain_loss is directly given and 
        # needs to be used. parameter set 1 gives the distance directly, while
        # parameter set 2 first calculates it with the altitudes of the tx and
        # rx elements, and the angle from horizon as taken from rx (<90deg)
        # Requires the distance between point of Transmission and Reception
        '''
        # TODO: Use the testcase as provided in the microsat course slides to test this and align elevation provision
        if self.input_type == "parameter_set_1":
            self.calc_1()
            # S = self.distance   #[m]
            # Ls = (self.wavelength/(4*np.pi*S))**2 #[-], Free Space Loss, will give negative Decibel as it is smaller than 1
            # self.gain = self.dB(Ls)
        elif self.input_type == "parameter_set_2":
            #Use the sine rule to calculate the distance
            # TODO: Make sure this works also for negative horizon angles?
            # TODO: Make sure that it doesnt matter if ground station is above
            #       sc, instead make it such that it depends only on tx and rx
            #       and that they can be everywhere
            
            r_sc = self.sc_altitude + Re    #[m]
            r_gs = self.gs_altitude + Re    #[m]
            if self.angle == 90:
                S = abs(r_sc-r_gs)
            else:
                if self.angle < 90:
                    a = 90+self.angle               #[deg]
                elif self.angle > 90:
                    a = 90+abs(180-self.angle)
                sineratio = r_sc/np.sin(np.deg2rad(a))
                b = np.rad2deg(np.arcsin(r_gs/sineratio))  #[deg]
                c = 180-a-b                     #[deg]
                S = sineratio*np.sin(np.deg2rad(c))         #[m]
            Ls = (self.wavelength/(4*np.pi*S))**2 #[-], Free Space Loss, will give negative Decibel as it is smaller than 1
            self.gain = self.dB(Ls)
        # elif self.input_type == "gain_loss":
        #     self.gain = self.gain


    def calc_1(self):
        S = self.distance  # [m]
        Ls = (self.wavelength / (
                    4 * np.pi * S)) ** 2  # [-], Free Space Loss, will give negative Decibel as it is smaller than 1
        self.gain = self.dB(Ls)

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    testparameters = {'distance': 100e3,
                      'sc_altitude': 90e3,
                      'gs_altitude': 0,
                      'angle':91,
                      'wavelength':1}    
    testelement = FREE_SPACE_LinkElement('test', 'parameter_set_2', -100, testparameters)
    print(testelement)
    testelement.process()
    print(testelement)