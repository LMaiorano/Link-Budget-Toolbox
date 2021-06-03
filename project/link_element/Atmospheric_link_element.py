# -*- coding: utf-8 -*-
"""
Created on Sun May 23 18:46:47 2021

@author: Willem van Lynden
"""
from project.link_element import LinkElement
import numpy as np

c = 299792458   #[m/s]

class Atmospheric_LinkElement(LinkElement):
    """Specific type of LinkElement for the Atmospheric loss,
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
            'air_temperature': int
                The surface temperature in [degK],
            'air_pressure': int
                The surface pressure in [Pa],
            'water_vapor_content': int
                The water vapor content at surface level in [kg/m**3],
            'wavelength': int
                The wavelength of the transmission in [m],
            'elevation_angle': int
                The elevation from the horizon of ground station to the 
                spacecraft in [deg]
    Methods:
    -------
    process()
        Updates the attenuation loss
    attenuationDryAir()
        Returns the attenuation in dry air based on ITU-R P.676-9
    attenuationWetAir()
        Returns the attenuation in wet air based on ITU-R P.676-9
    g()
        Wet air attenuation substitution calculation in Rec. ITU-R P.676-10
    phi()
        Dry air attenuation substitution calculation in Rec. ITU-R P.676-10
    
    Although not defined here, methods "dB(value)", "get_gain()" and 
    "get_loss()" are automatically inherited and will also work
    """
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
            'air_temperature': int,
                The surface temperature in [degK]
            'air_pressure': int,
                The surface pressure in [Pa]
            'water_vapor_content': int,
                The water vapor content at surface level in [kg/m**3]
            'wavelength': int
                The wavelength of the transmission in [m]
            'elevation_angle': int
                The elevation from the horizon of ground station to the 
                spacecraft in [deg]
        '''
        
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='Atmospheric', gain = gain)
        # Add attributes that are unique to Atmospheric_LinkElement
        self.input_type = input_type

        self.t = parameters.get('air_temperature', None) -273.15    # [degC]
        self.p = parameters.get('air_pressure', None)*1e-2          # [hPa]
        self.ro = parameters.get('water_vapor_content', None)*1e3   # [g/m**3]
        self.wavelength = parameters.get('wavelength', None)        # [m]
        self.angle = parameters.get('elevation_angle', None)        # [deg]
        self.f = c/self.wavelength*1e-6                             # [GHz]
        # Check if gain/loss is given directly or calculations are required
        if self.input_type != 'gain_loss':
            self.process()

    def process(self):
        '''Updates the attenuation loss
        
        Follows the "RECOMMENDATION ITU-R P.676-9 - Attenuation by
        atmospheric gases" document of the International Telecommunication
        Union. The calculations of attenuation in wet and dry air are summated
        and multiplied with the path length.

        Returns
        -------
        None

        '''
        # Summates the attenuations due to the path through wet and dry air
        self.gain = (self.attenuationWetAir() + self.attenuationDryAir()
                     ) / np.sin(self.angle / 180 * np.pi)
    def attenuationDryAir(self):
        '''Returns the attenuation in dry air based on ITU-R P.676-9
        
        Calculates the atmospheric attenuation in dry air, based on the
        water_vapor_content, air_temperature, air_pressure and frequency.
        The function is valid up to 54 GHz.

        Returns
        -------
        double

        '''
        # approximation valid up to 54 GHz
        e = self.ro* (self.t + 273.15) / 216.7
        ptot= self.p + e
        rp= ptot/ 1013
        rt= 288 / (273 + self.t)

        xi1 = float(self.phi(rp, rt, 0.0717, -1.8132, 0.0156, -1.6515))
        xi2 = float(self.phi(rp, rt, 0.5146, -4.6368, -0.1921, -5.7416))
        xi3 = float(self.phi(rp, rt, 0.3414, -6.5851, 0.2130, -8.5854))
        gamma0 = (((7.2 * rt**(2.8)) / (self.f**2 + 0.34 * rp**2 * rt**(1.6)))
                  + ((0.62 * xi3) / ((54 -self.f)**(1.16 * xi1) + 0.83 * xi2))
                  ) * self.f**2 * rp**2 * 1e-3

        t1 = 4.64 / (1 + 0.066 * rp**(-2.3)) * np.exp(
            -((self.f -59.7) / (2.87 + 12.4 * np.exp(-7.9 * rp)))**2)
        t2 = 0.14 * np.exp(2.12 * rp) / (
            (self.f -118.75)**2 + 0.031 * np.exp(2.2 * rp))
        t3 = 0.0114 / (1 + 0.14 * rp**(-2.6)) * self.f * (
            -0.0247 + 0.0001 * self.f + 1.61e-6 * self.f**2) / (
                1 -0.0169 * self.f + 4.1e-5 * self.f**2 + 3.2e-7 * self.f**3)
        h0 = 6.1 / (1+0.17* rp**(1.1)) * (1+t1 +t2 + t3)
        att = h0 * gamma0

        return att

    def attenuationWetAir(self):
        '''Returns the attenuation in wet air based on ITU-R P.676-9
        
        Calculates the atmospheric attenuation in wet air, based on the
        water_vapor_content, air_temperature, air_pressure and frequency.
        The function is valid up to 350 GHz.

        Returns
        -------
        double

        '''
        # approximation valid up to 350 GHz
        e = self.ro* (self.t + 273.15) / 216.7
        ptot= self.p + e
        rp= ptot/ 1013
        rt= 288 / (273 + self.t)

        eta1 = 0.955 * rp* rt**(0.68) + 0.006 * self.ro
        eta2 = 0.735 * rp* rt**(0.5) + 0.0353 * rt**4 * self.ro

        gamma1 = self.g(self.f, 22) * (3.98 * eta1 * np.exp(2.23 * (
            1 -rt))) / ((self.f -22.235)**2 + 9.42 * eta1**2) + (
                11.96 * eta1 * np.exp(0.7 * (1 -rt))) / ((
                    self.f -183.31)**2 + 11.14 * eta1**2)
        gamma2 = ((0.081 * eta1 * np.exp(6.44 * (1 -rt))) / (
            (self.f -321.226)**2 + 6.29 * eta1**2)) + ((3.66 * eta1 * np.exp(
                1.6 * (1 -rt))) / ((self.f -325.153)**2 + 9.22 * eta1**2))
        gamma3 = ((25.37 * eta1 * np.exp(1.09 * (1 -rt))) / (
            (self.f -380)**2)) + ((17.4 * eta1 * np.exp(1.46 * (
                1 -rt))) /((self.f -448)**2))
        gamma4 = (self.g(self.f, 557) * (844.6 * eta1 * np.exp(0.17 * (
            1 -rt))) /((self.f -557)**2)) + (self.g(self.f, 752) * (
                290 * eta1 * np.exp(0.41 * (1 -rt))) /((self.f -752)**2))
        gamma5 = self.g(self.f, 1780) * (8.3328e4 * eta2 * np.exp(0.99 * (
            1 -rt))) /((self.f -1780)**2)
        gammaw= (gamma1 + gamma2 + gamma3 + gamma4 + gamma5
                 ) * self.f**2 * rt**(2.5) * self.ro* 1e-4

        sigmaw= 1.013 / (1 + np.exp(-8.6 * (rp-0.57)))

        t1 = (1.39 * sigmaw) / ((self.f -22.235)**2 + 2.56 * sigmaw)
        t2 = (3.37 * sigmaw) / ((self.f -183.31)**2 + 4.69 * sigmaw)
        t3 = (1.58 * sigmaw) / ((self.f -325.1)**2 + 2.89 * sigmaw)

        hw= 1.66 * (1 + t1 + t2 + t3)

        att = gammaw* hw

        return att

    def g(self,f,fi):
        '''
        Wet air attenuation substitution calculation in Rec. ITU-R P.676-10

        Returns
        -------
        float

        '''
        out = 1 + ((f-fi) / (f+fi))**2
        return out

    def phi(self,rp, rt, a, b, c, d):
        '''
        Dry air attenuation substitution calculation in Rec. ITU-R P.676-10

        Returns
        -------
        double

        '''
        out = rp**a * rt**b * np.exp(c * (1 - rp) + d * (1 - rt))
        return out

if __name__ == '__main__':
    # Put any code here you want to use to test the class
    # (like a scratch pad to test stuff while you're working)
    testparameters = {'air_temperature': 15+273.15,
                      'air_pressure': 101300,
                      'water_vapor_content': 7.5*1e-3,
                      'wavelength': c/2e6,
                      'elevation_angle': 5}
    testelement = Atmospheric_LinkElement('test', 'parameter_set_2', -131, 
                                          testparameters)
    print(testelement)
    testelement.process()
    print(testelement)