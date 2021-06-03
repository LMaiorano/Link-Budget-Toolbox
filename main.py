#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script execution of the Link Budget.
Allows user to choose whether to use script or UI app

"""

from project.process import main_process, load_from_yaml
from project.settings import DEFAULT_LINK_CONFIG
from project.app.app import run_app

import argparse
import os
from pathlib import Path, WindowsPath



def run_script(config_file):
    '''Runs Link Budget Toolbox as a script without a User Interface

    Total gain and margin are printed in console as results

    Parameters
    ----------
    config_file : str
        File path to configuration YAML file

    Returns
    -------
    dict
        Updated configuration file, with gain of each element and total overall
        gain and margin
    '''
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

    return result




def main():
    '''Runs Link Budget Toolbox. Defaults to GUI app, unless CLI argument '-s' is passed

    usage: Link Budget Toolbox [-h] [-d | -s] [-f FILE]

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           GUI app only: Print debug statements to terminal
      -s, --script          Run as CLI script. Does not open GUI
      -f FILE, --file FILE  Link Budget configuration file (YAML)
    '''

    parser = argparse.ArgumentParser(prog="Link Budget Toolbox",
                                     description="Runs by default as application with GUI")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--debug', help='GUI app only: Print debug statements to terminal',
                       action="store_true")
    group.add_argument('-s', '--script', help="Run as CLI script. Does not open GUI",
                       action="store_true")
    parser.add_argument('-f', '--file', nargs=1, default=DEFAULT_LINK_CONFIG, help='Link Budget configuration file (YAML)')
    args = parser.parse_args()

    # ----------- Command Line Script ---------
    if args.script:
        file = args.file
        if not isinstance(file, WindowsPath):
            file = Path(os.getcwd(), file[0].strip("'"))

        cfg_file = Path(os.getcwd(), file)
        print(cfg_file)
        run_script(str(cfg_file))

    # --------- GUI Application ------------
    else:
        if args.debug:
            run_app(log_lvl='DEBUG')
        else:
            run_app()


if __name__ == '__main__':
    main()





