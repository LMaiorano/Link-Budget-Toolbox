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
            'distance': int
                Total distance tx-rx in [m], 
            'sc_altitude': int 
            Altitude, not orbit, of furthest point in [m],
            'gs_altitude': int
                Altitude, not orbit, of closest point in [m],
            'wavelength': int
                Wavelength of the transmission in [m],
            'elevation_angle': int
                Elevation of sc from horizon of gs in [deg].
    Methods:
    -------
    process()
        Updates the Free Space loss
    calc_loss()
        Calculates the Free Space loss when a parameter_set is used
    calc_elevdistance()
        Calculates the distance when parameter_set_2 is used
    
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
                'distance': int
                    Total distance tx-rx in [m], 
                'sc_altitude': int 
                    Altitude, not orbit, of furthest point in [m],
                'gs_altitude': int
                    Altitude, not orbit, of closest point in [m],
                'wavelength': int
                    Wavelength of the transmission in [m],
                'elevation_angle': int
                    Elevation of sc from horizon of gs in [deg].

        '''
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='FREE_SPACE', gain = gain)
        # Add attributes that are unique to TxElement
        self.input_type = input_type
        # Add attributes that are unique parameters to FREE_Space_LinkElement
        self.distance = parameters.get('distance', None)
        self.sc_altitude = parameters.get('sc_altitude', None)
        self.gs_altitude = parameters.get('gs_altitude', None)
        self.angle = parameters.get('elevation_angle', None)     #[deg]
        self.wavelength = parameters.get('wavelength', None)
        # check if gain/loss is given directly or calculations are required
        if self.input_type != 'gain_loss':
            self.process()

        
    def process(self):
        '''Updates the Free Space loss
        
        Free Space Path Loss Specific calculations,
        if parameter_set_1 is used it calculates the loss directly, while
        with parameter_set_2 it first calculates the distance before doing so.

        Returns
        -------
        None

        '''
        if self.input_type == 'parameter_set_1':
            self.gain = self.calc_FreeSpaceLoss()
        elif self.input_type == 'parameter_set_2':
                self.calc_distance()
                self.gain = self.calc_FreeSpaceLoss()

    def calc_FreeSpaceLoss(self):
        '''returns the Free Space loss in decibels.
        
        Calculates the Free Space Loss using a given distance between the 
        transmitting and receiving points.

        Returns
        -------
        double
            The Free Space loss

        '''
        Ls = (self.wavelength / (4 * np.pi * self.distance)) ** 2  # [-], Free Space Loss
        loss = self.dB(Ls)
        return loss
        
    def calc_distance(self):
        '''Updates the distance between the transmitting and receiving points 
        based on parameter_set_2
        
        Calculates the distance between two points orbiting a
        barycentre: gs, groundstation, the closest to the barycentre and sc,
        spacecraft, the furthest from the barycentre. The final parameter is
        the angle from the horizon as taken from the groundstation. This 
        assumes that the horizon plane is perpendicular to the origin of the
        barycenter. The sine-rule is then used to calculate the distance 
        between sc and gs.

        Returns
        -------
        None

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
        self.distance = S

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    testparameters = {'distance': 600e3,
                      'sc_altitude': 500e3,
                      'gs_altitude': 0,
                      'elevation_angle': 10,
                      'wavelength': c/2e6}   
    testelement = FREE_SPACE_LinkElement('test', 'parameter_set_1', -131, testparameters)
    print(testelement)