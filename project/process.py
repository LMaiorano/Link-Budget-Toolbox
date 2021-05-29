#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: process.py
project: Link-Budget-Toolbox
date: 09/05/2021
author: Jesper Frijns
"""

# Two ways of importing the link element classes
import project.link_element as le
from pathlib import Path
import yaml
import pandas as pd
from loguru import logger
from astropy import units as u


def load_from_yaml(file):
    with open(file, 'r') as f:
        data = yaml.full_load(f)
    return data

def save_to_yaml(d:dict, filename:str):
    '''Save dictionary to yaml, with a specified filename

    Parameters
    ----------
    d : dict
        Dictionary to save to YAML
    filename : str
        Filename of YAML. If only a filename is passed, the save location
        defaults to "./configs/". This can be overwritten if a filepath is given
    '''
    # Convert to Path object, makes manipulation easier in the future
    filepath = Path(filename)

    if filepath.suffix != '.yaml': # Wrong suffix given
        filepath = Path(filepath.parent, filepath.stem+'.yaml')

    if len(filepath.parts) == 1: # Only a filename is given, change save directory to default
        filepath = Path('./configs', filepath.name)

    # Save data to YAML
    with open(filepath, 'w') as f:
        yaml.dump(d, f)

def read_user_data(user_data):
    '''Convert the link element inputs from the user_data dictionary to a dataframe

    Parameters
    ----------
    user_data: dict
        Dictionary containing the data and link elements the user has given

    Returns
    -------
    df_user_data : df
        Dictionary which gives along its rows per link element the link element name, link type, input type,
        gain loss and parameters, based on the user input in the dictionary user_data
    '''

    df_user_data = pd.DataFrame.from_dict(user_data['elements']).T.reset_index().rename(columns={'index' : 'name'})

    return df_user_data


def fill_results_data(df_user_data, user_data):
    '''Get the gain/loss of each link element and write it to the results_data dictionary

    Parameters
    ----------
    df_user_data : df
        Dictionary which gives along its rows per link element the link element name, link type, input type,
        gain loss and parameters, based on the user input in the dictionary user_data

    Returns
    -------
    results_data : dict
        User_data dictionary which has been updated with the calculated gains/losses
    '''

    results_data = user_data

    for i in range(len(df_user_data)):
        # calculation step

        link_type = df_user_data.get("link_type")[i]
        link_class = f'{link_type}_LinkElement'


        if link_type == 'GENERIC':     # Generic (parent) link element class, takes 3 arguments
            link_class = f'LinkElement'
            result_gain_loss = (eval('le.' + link_class +
                                     '(df_user_data.get("name")[i], \
                                     df_user_data.get("input_type")[i],\
                                     df_user_data.get("gain_loss")[i])')).gain

        elif df_user_data.get("parameters")[i] == None: # Specific Link element, no parameters
            result_gain_loss = (eval('le.' + link_class +
                                     '(df_user_data.get("name")[i], \
                                     df_user_data.get("input_type")[i],\
                                     df_user_data.get("gain_loss")[i], \
                                     dict())')).gain

        else:           # All other link elements with parameters given
            result_gain_loss = (eval('le.' + link_class +
                                     '(df_user_data.get("name")[i], \
                                     df_user_data.get("input_type")[i],\
                                     df_user_data.get("gain_loss")[i], \
                                     df_user_data.get("parameters")[i])')).gain

        #update step
        results_data['elements'][df_user_data.get("name")[i]]["gain_loss"] = result_gain_loss

    return results_data

def decompose_SI(val, unit_str, **kwargs):
    '''Converts a value with specified unit to its base SI unit

    Parameters
    ----------
    val : float
        Quantity to convert
    unit_str : str
        Unit to convert from. For available units, see:
         https://docs.astropy.org/en/stable/units/index.html
    skip_units : list of str
        Units to skip conversion (Default: ['dB', 'deg', '-', ''])

    Returns
    -------
    tuple
        Quantity converted to base unit,
        Base unit string representation
    '''
    # Default units to skip, unless specified otherwise
    default_skip = ['dB', 'deg', '-', '']
    skip_units = kwargs.pop('skip_units', default_skip)

    # Check if unit is excluded
    if unit_str in skip_units:
        return val, unit_str            # Return same as what is given

    try:
        x_u = eval(f'u.{unit_str}')     # Given units
        x = val * x_u                   # Create unit-quantity
        x_si = x.decompose()            # Convert quantity to the base-unit of u
        return float(x_si.value), str(x_si.unit)  # convert numpy float64 (precision not necessary)

    except AttributeError:
        logger.debug(f'Error decomposing units. "{unit_str}" is not a recognized unit')
        return None, None


def convert_to_standard_units(data):
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

    for element, attributes in data['elements'].items():
        if attributes['parameters'] is None:
            continue  # move on to next element since no parameters to convert

        link_type = attributes['link_type']
        input_type = attributes['input_type']

        for param, value in attributes['parameters'].items():
            unit = param_ref[link_type][input_type][param]['units'] # Determine unit
            si_value = decompose_SI(value, unit)[0]      # Convert value to base SI

            # Replace value in dictionary
            data['elements'][element]['parameters'][param] = si_value


def main_process(user_data):
    '''Use user_data dictionary to calculate gains/losses to create a results_data dictionary

    Parameters
    ----------
    user_data: dict
        Dictionary containing the data and link elements the user has given

    Returns
    -------
    results_data : dict
        User_data dictionary which has been updated with the calculated gains/losses
    '''
    # Convert parameter units to standard SI base units
    convert_to_standard_units(user_data)

    # results_data = fill_results_data(read_user_data(update_params_from_genval(user_data, read_user_data(user_data))))
    results_data = fill_results_data(read_user_data(user_data), user_data)

    return results_data

if __name__ == '__main__':

    default_file = 'configs/default_config.yaml'

    data = load_from_yaml(default_file)

    main_process(data)





