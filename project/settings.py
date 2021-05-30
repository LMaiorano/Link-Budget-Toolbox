#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a central reference file which defines absolute file paths to commonly used
configuration files or directories. Paths should only be changed here.
"""

from pathlib import Path




# Absolute file path of project base directory
BASE_DIR = Path(Path(__file__).parent.parent)



# Element configuration file that defines parameter sets per link type, as well
# as units and descriptions that are displayed in the UI
ELEMENT_REFERENCE = Path(BASE_DIR, 'project/element_reference.yaml')




# LinkBudget Configurations, loaded/saved by UI and run by process
CONFIGS_DIR = Path(BASE_DIR, 'project/configs')
DEFAULT_APP_CONFIG = Path(BASE_DIR, CONFIGS_DIR, 'default_config.yaml')




# PyQt Application Files
APP_UI_DIR = Path(BASE_DIR, 'project/app/ui')



