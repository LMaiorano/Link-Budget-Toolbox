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

#TODO: Import dictionary to GUI

#TODO: Put right link element names in 'elements' to call

# This is a temporary dictionary. In the end the dictionary should be filled in automatically based on user input.
user_data = {'setting' : {'case_type' : 'nominal'},
             'generic_values' : {'altitude':800},
             'elements' : {'SC_TX_Ant' :              {'link_type'  :   'TRANSMITTER',
                                                       'input_type' :   'gainloss',
                                                       'gain_loss'  :    10,
                                                       'parameters' :  {'parameter1' : None,
                                                                        'parameter2' : None,
                                                                        'parameter3' : None}},
                           'free_space' :             {'link_type' :    'FREE_SPACE',
                                                       'input_type' :   'gainloss',
                                                       'gain_loss' :     -8,
                                                       'parameters' :  {'parameter1' : None,
                                                                        'parameter2' : None,
                                                                        'parameter3' : None}},
                           'GS_RX_Ant':               {'link_type'  :   'RECEIVER',
                                                       'input_type' :   'gainloss',
                                                       'gain_loss'  :    2,
                                                       'parameters' :  {'parameter1' : None,
                                                                        'parameter2' : None,
                                                                        'parameter3' : None}}
                           }
             }




if __name__ == '__main__':
    # TODO: Read out dictionary and check for linktypes
    # TODO: Based on linktypes, call link elements
    # TODO: Get gainloss from link elements
    for i in user_data['elements']:
        # Access seperate link elements one by one, check for input_type and call with correct variables each link
        # element file.
        print(i, user_data['elements'])
        #TODO: Make sure that all link element classes have same naming convention for callability's sake
        #TODO: Make sure that all link element classes are in a seperate file

    # TODO: Sum link elements
    # TODO: Decide on export file (JSON, YAML, etc.)
    # TODO: Save to file for GUI

    generic = le.LinkElement('Example 1', 'GENERIC', 3)

    eirp_example = le.EIRPElement('EIRP Example', parameters=[5, 23])

    print(generic)


