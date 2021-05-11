#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: process.py
project: Link-Budget-Toolbox
date: 09/05/2021
author: lmaio
"""

# Two ways of importing the link element classes
import project.link_element as le

#TODO: Import dictionary to GUI
user_data = {'setting' : 'nominal',
             'generic_values' : {'altitude':800},
             'elements' : {'spacecraft_transmitter' : {'link_type' :    'TRANSMITTER',
                                                       'input_type' :   'gainloss',
                                                       'parameters' :  {'parameter1' : None,
                                                                        'parameter2' : None,
                                                                        'parameter3' : None}},
                           'free_space' :              {'link_type' :   'FREE_SPACE',
                                                       'input_type' :   'gainloss',
                                                       'parameters' :  {'parameter1' : None,
                                                                        'parameter2' : None,
                                                                        'parameter3' : None}},
                           'ground_station_receiver': {'link_type':     'RECEIVER',
                                                       'input_type':    'gainloss',
                                                       'parameters':   {'parameter1': None,
                                                                       'parameter2': None,
                                                                       'parameter3': None}}
                           }
             }





#TODO: Create dictionary
#TODO: Read out dictionary and check for linktypes
#TODO: Based on linktypes, call link elements
#TODO: Get gainloss from link elements
#TODO: Sum link elements
#TODO: Decide on export file (JSON, YAML, etc.)
#TODO: Save to file for GUI


if __name__ == '__main__':
    generic = le.LinkElement('Example 1', 'GENERIC', 3)

    eirp_example = le.EIRPElement('EIRP Example', parameters=[5, 23])

    print(generic)


