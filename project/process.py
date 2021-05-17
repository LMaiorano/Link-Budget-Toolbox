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

#TODO: Import dictionary automatically from GUI

# This is a temporary dictionary. In the end the dictionary should be filled in automatically based on user input.
user_data = {'setting' : {'case_type' : 'nominal'},
             'generic_values' : {'altitude':800},
             'elements' : {'TX_SC'      :             {'link_type'  :   'TX',
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss'  :    10,
                                                       'parameters' :  {'antenna_efficiency'    : None,
                                                                        'antenna_diameter'      : None,
                                                                        'wavelength'            : None}},
                           'FREE_SPACE' :             {'link_type' :    'FREE_SPACE',
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss' :     -8,
                                                       'parameters' :  {'distance'      : None,
                                                                        'sc_altitude'   : None,
                                                                        'gs_altitude'   : None,
                                                                        'angle'         : None,
                                                                        'wavelength'    : None}},
                           'RX_GS    ':               {'link_type'  :   'RX',
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

def main_process():
    print("Jesper's main process")


if __name__ == '__main__':
    # call class, give gain, all parameter types and input_type
    # TODO: Get gainloss from link elements
    # TODO: Decide on if EIRP should be a class or calculated in process.py

    # check for input_type and call with correct variables each link element file.
    for give_link_element_name in user_data['elements'].keys(): # Access seperate link elements one by one

        for key, element in user_data['elements'][give_link_element_name].items():

            if key == 'link_type':
                give_link_type = element

            if key == 'gain_loss':
                give_gain_loss = element

            if key == 'input_type':
                give_input_type = element

            give_params = []
            if key == 'parameters':
                for param_key, param_element in user_data['elements'][give_link_element_name]['parameters'].items():
                    give_params.append(param_element)

        results_name =  []
        results_val =   []
        # TODO: uncomment this below if you want to calculate the gains. N.B. This does not work yet as the inputs and
        # outputs of the classes still have to be changed. (input list of params and output gain_loss only)

        # TODO: Make give_params input a dictionary (variable_a = dic.get('elements', default value))
        results_val.append(eval('le.'+ give_link_type + '_LinkElement' + '(give_link_element_name,\
                                                           give_input_type, give_gain_loss, give_params)'))

    flux_margin = sum(results_val)
    # TODO: Save to file result_data (same as user_data, but with gain_loss results updated.

    # generic = le.LinkElement('Example 1', 'GENERIC', 3)
    # # What input to classes will be: link_type, loss_gain value and all parameter values
    # eirp_example = le.EIRPElement('EIRP Example', parameters=[5, 23])
    #
    # print(generic)

    ## Save dictionary to yaml
    # (luigi needed this quick for the gui, it's not necessary for the overall process)
    save_to_yaml(user_data, 'example_config')



