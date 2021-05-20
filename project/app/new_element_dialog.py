#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: new_element_dialog.py
project: Link-Budget-Toolbox
date: 17/05/2021
author: nicolas Fosseprez
"""

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QDialog


newelement_form_class = uic.loadUiType('ui/new_element.ui')[0]

class NewElementDialog(QDialog, newelement_form_class):
    def __init__(self, element_reference:dict, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.element_ref = element_reference

        # Add available elements to combobox
        self.cmb_element_type.clear() # Ensures it start empty
        for input_type in self.element_ref.keys():
            self.cmb_element_type.addItem(input_type)

    def continue_clicked(self):
        pass
    
    def yes_gain_clicked(self):
        pass
    
    def no_gain_clicked(self):
        pass
    
    
