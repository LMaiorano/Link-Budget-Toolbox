#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script execution of the Link Budget. Performs same calculations as the UI app
"""

from project.process import main_process, load_from_yaml
from pathlib import Path
from project.settings import DEFAULT_APP_CONFIG


def main(config_file):
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


def column_print(values, indent=''):
    col_width = max(len(name) for row in values for name in row) + 2
    for row in values:
        print(indent + "".join(word.ljust(col_width) for word in row))


if __name__ == '__main__':
    default_file = Path(DEFAULT_APP_CONFIG)

    main(default_file)

