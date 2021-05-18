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

#TODO: Import dictionary automatically from GUI

# This is a temporary dictionary. In the end the dictionary should be filled in automatically based on user input.

user_data = {'settings'         : {'case_type'      : 'nominal'},
             'generic_values'   : {'sc_altitude'    : 800,                # [m]
                                   'wavelength'     : 1500*10**(-9)},     # [m]
             'elements'         : {'TX_SC'      :     {'link_type'  :   'TX',
                                                       'idx'        :    0,
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss'  :    10,            # [dB]
                                                       'parameters' :  {'antenna_efficiency'    : None,     # [-]
                                                                        'antenna_diameter'      : None,     # [m]
                                                                        'wavelength'            : None}},   # [m]
                                   'FREE_SPACE' :     {'link_type' :    'FREE_SPACE',
                                                       'idx'        :    1,
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss' :     -8,
                                                       'parameters' :  {'distance'      : None,     # [m]
                                                                        'sc_altitude'   : None,     # [m]
                                                                        'gs_altitude'   : None,     # [m]
                                                                        'angle'         : None,     # [deg]
                                                                        'wavelength'    : None}},   # [m]
                                   'RX_GS    ':       {'link_type'  :   'RX',
                                                       'idx'        :    2,
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss'  :    2,             # [dB]
                                                       'parameters' :  {'antenna_efficiency'    : None,     # [-]
                                                                        'antenna_diameter'      : None,     # [m]
                                                                        'wavelength'            : None}},   # [m]
                           }
             }

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
    '''Write the link element inputs from the user_data dictionary to a dataframe

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

def update_params_from_genval(user_data, df_user_data):
    '''Use the user-given generic values to update the matching parameters within all link elements

    Parameters
    ----------
    user_data: dict
        Dictionary containing the data and link elements the user has given
    df_user_data : df
        Dictionary which gives along its rows per link element the link element name, link type, input type,
        gain/loss and parameters, based on the user input in the dictionary user_data

    Returns
    -------
    user_data: dict
        Dictionary containing the data and link elements the user has given

    '''

    df_generic_values = pd.DataFrame.from_dict(user_data['generic_values'], orient='index').reset_index()\
        .rename(columns={'index' : 'variable', 0 : 'value'})

    for i in range(len(df_generic_values)):
        for j in range(len(df_user_data)):
            if df_generic_values.iloc[i]['variable'] in \
                    user_data['elements'][df_user_data.get("name")[j]]['parameters']:

                user_data['elements'][df_user_data.get("name")[j]]['parameters']\
                    .update({df_generic_values.iloc[i]['variable'] : df_generic_values.iloc[i]['value']})

    return user_data

def fill_results_data(df_user_data):
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
        result_gain_loss = (eval('le.'+ df_user_data.get("link_type")[i] + '_LinkElement' +
                                 '(df_user_data.get("name")[i], \
                                 df_user_data.get("input_type")[i],\
                                 df_user_data.get("gain_loss")[i], \
                                 df_user_data.get("parameters")[i])')).gain

        #update step
        results_data['elements'][df_user_data.get("name")[i]]["gain_loss"] = result_gain_loss

    return results_data

# TODO: Make user_data an input of main_process()
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

    results_data = fill_results_data(read_user_data(update_params_from_genval(user_data, read_user_data(user_data))))

    return results_data

if __name__ == '__main__':
    main_process(user_data)





