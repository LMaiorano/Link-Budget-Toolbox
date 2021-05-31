#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: unit_conversion.py
project: Link-Budget-Toolbox
date: 30/05/2021
author: Luigi Maiorano
"""
from pathlib import Path
from loguru import logger
import yaml
from project.settings import ELEMENT_REFERENCE
from astropy import units as u
import scipy.constants as sc
import copy

def load_from_yaml(file):
    with open(file, 'r') as f:
        data = yaml.full_load(f)
    return data

def base_SI(val, prefix_unit_str):
    '''Converts a value with specified unit to its base SI unit

    Parameters
    ----------
    val : float
        Quantity to convert
    prefix_unit_str : str
        Unit to convert from. For available units, see:
         https://docs.astropy.org/en/stable/units/index.html

    Raises
    ------
    NotImplementedError:
        For composite units

    Returns
    -------
    float or None
        Quantity converted to base unit
    str or None
        Base unit string representation
    '''
    try:
        x_u = u.Unit(prefix_unit_str)          # Given units
        if isinstance(x_u, u.CompositeUnit):
            raise NotImplementedError(f'\n\tConversion of composite units not supported: "{prefix_unit_str}"')

        x = val * x_u                   # Create unit-quantity
        x_si = x.decompose()            # Convert quantity to the base-unit of u
        return float(x_si.value), str(x_si.unit)  # convert numpy float64 (precision not necessary)

    except AttributeError:
        logger.debug(f'Error decomposing units. "{prefix_unit_str}" is not a recognized unit')
        return None, None


def prefixed_SI(base_si_val, prefix_unit_str):
    '''Converts a Base SI value to a specified prefixed unit

    The base SI unit is derived directly from the desired prefixed unit.
    Note: This only works for single units. Composite units (ie m / s^2) are not supported

    This is used after the main_process calculation to convert back to logical units

    Parameters
    ----------
    base_si_val : float
        Quantity to convert
    prefix_unit_str : str
        Unit to convert TO. For available units, see:
         https://docs.astropy.org/en/stable/units/index.html
    
    Raises
    ------
    NotImplementedError:
        For composite units

    Returns
    -------
    float or None
        Quantity converted to base unit
    str or None
        Base unit string representation
    '''
    try:
        x_u = u.Unit(prefix_unit_str)         # Units to convert to
        if isinstance(x_u, u.CompositeUnit):
            raise NotImplementedError(f'\n\tConversion of composite units not supported: "{prefix_unit_str}"')

        si_u = x_u.decompose().bases[0]        # Determine base unit (what the given value is in)
        x = (base_si_val * si_u).to(x_u)       # Convert to desired unit_str

        return float(x.value), str(x.unit)  # convert numpy float64 (precision not necessary)

    except AttributeError:
        logger.debug(f'Error decomposing units. "{prefix_unit_str}" is not a recognized unit')
        return None, None

def convert_SI_units(data, to_base_SI=True):
    '''Convert units to the base SI units

    Example: km -> m, GHz -> Hz

    References:
        'element_reference.yaml' for the given units per parameter

    Parameters
    ----------
    data : dict
        Link Budget configuration dictionary as passed from UI or config file
    '''
    elem_cfg_path = Path(ELEMENT_REFERENCE)
    param_ref = load_from_yaml(elem_cfg_path)

    ignore_units = ['dB', 'deg', '-', '']

    # Create copy to write changes to, without modifying iterator
    converted_data = copy.deepcopy(data)

    for element, attributes in data['elements'].items():
        if attributes['parameters'] is None:
            continue  # move on to next element since no parameters to convert

        link_type = attributes['link_type']
        input_type = attributes['input_type']

        converted_params = {}
        for param, value in attributes['parameters'].items():
            if not to_base_SI:
                # Convert frequency parameter (currently wavelength in [m]) to [Hz]
                if param.lower() == 'wavelength':
                    value = wavelength_to_freq(value)
                    # replace w/ 'frequency'
                    param = 'frequency'

            unit = param_ref[link_type][input_type][param]['units'] # Determine unit

            if unit not in ignore_units:
                # -------------- BEFORE Calculations -------------
                if to_base_SI:
                    # Convert value to base SI
                    value, new_unit = base_SI(value, unit)

                    # Convert frequency [Hz] to wavelength
                    if param.lower() == 'frequency':
                        if new_unit != '1 / s':
                            logger.debug(f'Frequency not reduced to Hz. {new_unit}')
                        value = freq_to_wavelength(value)

                        # Replace with 'wavelength'
                        param = 'wavelength'

                # -------------- AFTER Calculations -------------------
                else:
                    # Convert value to user-friendly unit
                    value= prefixed_SI(value, unit)[0]

            converted_params[param] = value

        # Replace value in dictionary
        converted_data['elements'][element]['parameters'] = converted_params

    return converted_data



def freq_to_wavelength(f):
    return float(sc.c / f)

def wavelength_to_freq(lmbda):
    return float(sc.c / lmbda)


if __name__ == '__main__':
    test_val = 60
    test_unit = 'km '

    # Convert to SI Base units
    si_val, si_unit = base_SI(test_val, test_unit)


    # Convert back to UI units
    res_val, res_unit = prefixed_SI(si_val, test_unit)

    print(res_val, res_unit)
