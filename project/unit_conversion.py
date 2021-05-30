#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: unit_conversion.py
project: Link-Budget-Toolbox
date: 30/05/2021
author: lmaio
"""
from pathlib import Path
from loguru import logger
import yaml
from astropy import units as u

def load_from_yaml(file):
    with open(file, 'r') as f:
        data = yaml.full_load(f)
    return data

def base_SI(val, unit_str):
    '''Converts a value with specified unit to its base SI unit

    Parameters
    ----------
    val : float
        Quantity to convert
    unit_str : str
        Unit to convert from. For available units, see:
         https://docs.astropy.org/en/stable/units/index.html

    Returns
    -------
    float or None
        Quantity converted to base unit
    str or None
        Base unit string representation
    '''
    try:
        x_u = eval(f'u.{unit_str}')     # Given units
        x = val * x_u                   # Create unit-quantity
        x_si = x.decompose()            # Convert quantity to the base-unit of u
        return float(x_si.value), str(x_si.unit)  # convert numpy float64 (precision not necessary)

    except AttributeError:
        logger.debug(f'Error decomposing units. "{unit_str}" is not a recognized unit')
        return None, None

def UI_units(val, unit_str):
    try:
        x_u = eval(f'u.{unit_str}')     # Given units
        # x = val * x_u                   # Create unit-quantity
        x_si = x_u.decompose()            # Convert quantity to the base-unit of u
        return float(x_si.value), str(x_si.unit)  # convert numpy float64 (precision not necessary)

    except AttributeError:
        logger.debug(f'Error decomposing units. "{unit_str}" is not a recognized unit')
        return None, None

def convert_SI_units(data, to_base_SI=True):
    '''Convert units to standard SI units

    References:
        'element_config_reference.yaml' for the given units per parameter

    Parameters
    ----------
    data : dict
        Link Budget configuration dictionary as passed from UI or config file
    '''
    elem_cfg_path = Path(Path(__file__).parent, 'element_config_reference.yaml')
    param_ref = load_from_yaml(elem_cfg_path)

    ignore_units = ['dB', 'deg', '-', '']

    for element, attributes in data['elements'].items():
        if attributes['parameters'] is None:
            continue  # move on to next element since no parameters to convert

        link_type = attributes['link_type']
        input_type = attributes['input_type']

        for param, value in attributes['parameters'].items():
            unit = param_ref[link_type][input_type][param]['units'] # Determine unit

            if unit not in ignore_units:
                if to_base_SI:
                    value = base_SI(value, unit)[0]      # Convert value to base SI
                else:
                    value = UI_units(value, unit)[0]

            # Replace value in dictionary
            data['elements'][element]['parameters'][param] = value


