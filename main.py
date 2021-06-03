#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script execution of the Link Budget. Performs same calculations as the UI app
"""

from project.process import main_process, load_from_yaml
from pathlib import Path
from project.settings import DEFAULT_APP_CONFIG
from project.app.app import run_app
import argparse


def run_script(config_file):
    def column_print(values, indent=''):
        col_width = max(len(name) for row in values for name in row) + 2
        for row in values:
            print(indent + "".join(word.ljust(col_width) for word in row))

    # Load config
    data = load_from_yaml(config_file)

    result = main_process(data)


    # Print Results
    header = [['Input Power:', f'{data["general_values"]["input_power"]} dBm'],
              ['Receiver System Threshold', f"{data['general_values']['rx_sys_threshold']} dBm"]]

    values = []
    for elem, data in result['elements'].items():
        values.append([elem, str(data['gain_loss'])])

    footer = [['Total Gain:', f"{result['general_values']['total_gain']} dB"],
              ["Margin:", f"{result['general_values']['total_margin']} dB"]]


    column_print(header)
    print()
    print(f'Total Gain per Element:')
    column_print(values, indent='\t')
    print()
    column_print(footer)


def main(method='script', config_file=DEFAULT_APP_CONFIG):
    # ----------- Command Line Script ---------
    if method.lower() == 'script':
        run_script(config_file)

    # --------- GUI Application ------------
    elif method.lower() == 'app':
        run_app()


if __name__ == '__main__':
    """Available Methods:
            'app'
            'script' - Requires file path of YAML config file
            
    Modify settings.py to change default file paths
    """
    main('app')

    # config1 = Path(DEFAULT_APP_CONFIG)
    # main(method='script', config_file=config1)




