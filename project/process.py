#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: process.py
project: Link-Budget-Toolbox
date: 09/05/2021
author: lmaio
"""

# Two ways of importing the link element classes
import project.link_element as le       # Cleaner style (import numpy as np)
from project.link_element import *      # Also valid



if __name__ == '__main__':
    generic = le.LinkElement('Example 1', 'GENERIC', 3)

    eirp_example = EIRPElement('EIRP Example', parameters=[5, 23])

    print(generic)


    this is a syntax error, still not fixed

