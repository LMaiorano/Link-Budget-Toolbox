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
user_data = {'settings' : {'case_type' : 'nominal'},
             'generic_values' : {'altitude':800},
             'elements' : {'TX_SC'      :             {'link_type'  :   'TX',
                                                       'index'      :   0,
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss'  :    10,
                                                       'parameters' :  {'antenna_efficiency'    : None,
                                                                        'antenna_diameter'      : None,
                                                                        'wavelength'            : None}},
                           'FREE_SPACE' :             {'link_type' :    'FREE_SPACE',
                                                       'index'      :   1,
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss' :     -8,
                                                       'parameters' :  {'distance'      : None,
                                                                        'sc_altitude'   : None,
                                                                        'gs_altitude'   : None,
                                                                        'angle'         : None,
                                                                        'wavelength'    : None}},
                           'RX_GS    ':               {'link_type'  :   'RX',
                                                       'index'      :    2,
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss'  :    2,
                                                       'parameters' :  {'antenna_efficiency'    : None,
                                                                        'antenna_diameter'      : None,
                                                                        'wavelength'            : None}},
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

    df_user_data = pd.DataFrame.from_dict(user_data['elements']).T.reset_index().rename(columns={'index': 'name'})

    return df_user_data

def fill_results_data(df_user_data):

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

def main_process(user_data):
    # print("Jesper's main process")

    results_data = fill_results_data(read_user_data(user_data))

    return results_data

if __name__ == '__main__':
    main_process(user_data)

    ## Save dictionary to yaml
    # (luigi needed this quick for the gui, it's not necessary for the overall process)
    # save_to_yaml(user_data, 'example_config')



