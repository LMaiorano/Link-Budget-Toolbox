# -*- coding: utf-8 -*-
"""
Created on Fri May 14 14:28:25 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np
# parameter_set_2 assumes an orbit surrounding a barycentre of both points
# Earth is taken as the system in which the transmission occurs.

Re = 6371e3     #[m]
c = 299792458   #[m/s]

class FREE_SPACE_LinkElement(LinkElement):
    '''Specific type of LinkElement for the Free Space Loss,
    that can depend a single gain/loss value or on parameters instead. as
    dictated by the input_type value. 

    Although not defined here, methods "get_gain()" and "get_loss()" are 
    automatically inherited and will also work
    '''
    def __init__(self, name, input_type, gain, parameters):
        '''Free Space Link Element object
        
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
        distance : int
            The total distance between the transmitting and receiving elements.
        sc_altitude : int
            The altitude, not orbit, of the furthest of the transmitting and
            receiving points to the barycentre in the system under
            consideration.
        gs_altitude : int
            The altitude, not orbit, of the closest of the transmitting and
            receiving points to the barycentre in the system under
            consideration.
        angle : int
            The elevation angle of sc as seen from the horizon of the gs point.
        wavelength : int
            The wavelength of the transmission in [m].

        Returns
        -------
        None.

        '''
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='FREE_SPACE', gain = gain)
        # Add attributes that are unique to TxElement
        self.input_type = input_type
        # Add attributes that are unique parameters to FREE_Space_LinkElement
        self.distance = parameters.get('distance', None)
        self.sc_altitude = parameters.get('sc_altitude', None)
        self.gs_altitude = parameters.get('gs_altitude', None)
        self.angle = parameters.get('angle', None)     #[deg]
        self.wavelength = parameters.get('wavelength', None)
        # check if gain/loss is given directly or calculations are required
        if self.input_type != 'gain_loss':
            self.process()

        
    def process(self):
        '''
        Free Space Path Loss Specific calculations, it checks which parameter
        set needs to be used and uses the respective required calculations.
        Parameter_set_1 gives the distance directly, while
        parameter_set_2 first calculates it with the altitudes of a
        groundstation, the closest to the barycentre and a spacecraft, the
        furthest from the barycentre, and the angle from horizon as taken from
        the groundstation. After this it calls calc_1 or calc_2 respectively
        to calculate the Free Space Loss.

        Returns
        -------
        self.gain: The updated gain of the FREE_SPACE_LinkElement object.

        '''
        
        if self.input_type == "parameter_set_1":
            self.calc_1()
        elif self.input_type == "parameter_set_2":
            # TODO: Make a try statement here that catches when people have
            # The gs altitude above the sc altitude
            self.calc_2()            

    def calc_1(self):
        '''
        Calculates the Free Space Loss using a given distance between the transmitting
        and receiving points.

        Returns
        -------
        self.gain: The updated gain of the FREE_SPACE_LinkElement object.

        '''
        S = self.distance  # [m]
        Ls = (self.wavelength / (4 * np.pi * S)) ** 2  # [-], Free Space Loss
        self.gain = self.dB(Ls)
        
    def calc_2(self):
        '''
        Calculates the gain using the distance between two points orbiting a
        barycentre: gs, groundstation, the closest to the barycentre and sc,
        spacecraft, the furthest from the barycentre. The final parameter is
        the angle from the horizon as taken from the groundstation. The
        sine-rule is then used to calculate the distance between sc and gs,
        after which the Free Space Loss is calculated.

        Returns
        -------
        self.gain: The updated gain of the FREE_SPACE_LinkElement object.

        '''
        # TODO: Check what happens in the case that the orbits are the same!
        # Set altitudes to orbital distance around barycentre of Earth-System.
        r_sc = self.sc_altitude + Re    #[m]
        r_gs = self.gs_altitude + Re    #[m]
        # Check the given horizon elevation for straight alignment with origin
        if self.angle == 90:
            # Distance is subtraction of orbits
            S = abs(r_sc-r_gs)  #[m]
        elif self.angle == -90 or self.angle == 270:
            # Distance is summation of orbits, signal passes through barycentre
            S = abs(r_sc+r_gs)  #[m]
        else:
            # Create triangle between origin, sc and gs, find angle sc-origin
            if self.angle < 90:
                a = 90+self.angle               #[deg]
            elif self.angle > 90:
                a = 90+180-self.angle           #[deg]
            #Use the sine rule to calculate the distance of sc-gs
            sineratio = r_sc/np.sin(np.deg2rad(a))
            b = np.rad2deg(np.arcsin(r_gs/sineratio))  #[deg]
            c = 180-a-b                     #[deg]
            S = sineratio*np.sin(np.deg2rad(c))         #[m]
        Ls = (self.wavelength/(4*np.pi*S))**2 #[-], Free Space Loss
        self.gain = self.dB(Ls)

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    testparameters = {'distance': 600e3,
                      'sc_altitude': 500e3,
                      'gs_altitude': 0,
                      'angle': 10,
                      'wavelength': c/2e6}    
    testelement = FREE_SPACE_LinkElement('test', 'parameter_set_2', -131, testparameters)
    print(testelement)
    testelement.process()
    print(testelement)