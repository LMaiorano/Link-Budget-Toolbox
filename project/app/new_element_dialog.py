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
from project.app.notification_dialog import showdialog
from loguru import logger


newelement_form_class = uic.loadUiType('ui/new_element.ui')[0]

class NewElementDialog(QDialog, newelement_form_class):
    def __init__(self, element_reference, existing_names, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.element_ref = element_reference
        self.existing_names = existing_names

        # Add available elements to combobox
        self.cmb_element_type.clear() # Ensures it start empty
        for input_type in self.element_ref.keys():
            self.cmb_element_type.addItem(input_type)

        # Initially hide parameters
        self.rdl_yes.setChecked(True)
        self.group_parameters.hide()

    def accept(self) -> None:
        '''Check that required fields are filled before continuing'''
        name = self.txt_element_name.text()
        if len(name) == 0:
            showdialog(['The new element must have a name'])
        elif name.lower() in self.existing_names:
            showdialog(['This element name already exists'])
        else:
            # Do its normal accept stuff
            super().accept()

    def elem_type_selected(self):
        type = self.cmb_element_type.currentText()
        logger.debug(f'Element type selected {type}')

    def param_set_selected(self):
        logger.debug(f'New parameter set selected')

    def continue_clicked(self):
        pass
    
    def yes_gain_clicked(self):
        self.group_parameters.hide()
    
    def no_gain_clicked(self):
        self.group_parameters.show()
    
    
