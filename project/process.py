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

#TODO: Import dictionary to GUI

#TODO: Put right link element names in 'elements' to call

# This is a temporary dictionary. In the end the dictionary should be filled in automatically based on user input.
user_data = {'setting' : {'case_type' : 'nominal'},
             'generic_values' : {'altitude':800},
             'elements' : {'TX'         :             {'link_type'  :   'TX',
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss'  :    10,
                                                       'parameters' :  {'parameter1' : None,
                                                                        'parameter2' : None,
                                                                        'parameter3' : None}},
                           'free_space' :             {'link_type' :    'FREE_SPACE',
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss' :     -8,
                                                       'parameters' :  {'parameter1' : None,
                                                                        'parameter2' : None,
                                                                        'parameter3' : None}},
                           'GS_RX_Ant':               {'link_type'  :   'RX',
                                                       'input_type' :   'gain_loss',
                                                       'gain_loss'  :    2,
                                                       'parameters' :  {'parameter1' : None,
                                                                        'parameter2' : None,
                                                                        'parameter3' : None}}
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
    # TODO: Read out dictionary and check for linktypes
    # call class, give gain, all parameter types and input_type
    # TODO: Based on linktypes, call link elements
    # TODO: Get gainloss from link elements
    # TODO: Decide on if EIRP should be a class or calculated in process.py
    for i in user_data['elements']:
        # Access seperate link elements one by one, check for input_type and call with correct variables each link
        # element file.
        print(i, user_data['elements'])
        #TODO: Make sure that all link element classes have same naming convention for callability's sake
        #TODO: Make sure that all link element classes are in a seperate file

    # TODO: Sum link elements
    # TODO: Save to file for GUI

    generic = le.LinkElement('Example 1', 'GENERIC', 3)
    # What input to classes will be: link_type, loss_gain value and all parameter values
    eirp_example = le.EIRPElement('EIRP Example', parameters=[5, 23])

    print(generic)

    ## Save dictionary to yaml
    # (luigi needed this quick for the gui, it's not necessary for the overall process)
    save_to_yaml(user_data, 'example_config')



