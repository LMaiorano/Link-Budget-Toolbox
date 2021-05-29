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
from project.app.custom_objects import showdialog
from loguru import logger


newelement_form_class = uic.loadUiType('ui/new_element.ui')[0]

class NewElementDialog(QDialog, newelement_form_class):
    def __init__(self, element_reference, existing_names, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.element_ref = element_reference
        self.existing_names = existing_names

        # Add available parameters to Element Type combobox
        self.cmb_element_type.clear() # Ensures it start empty
        for input_type in self.element_ref.keys():
            self.cmb_element_type.addItem(input_type)
            
        # Start with an empty Parameters combobox
        self.cmb_set_param.clear() # Ensures it start empty


    def accept(self) -> None:
        '''Check that required fields are filled before continuing'''
        conditions_met = 0

        # Check Name
        name = self.txt_element_name.text()
        if len(name) == 0:
            showdialog(['The new element must have a name'])
        elif name.lower() in self.existing_names:
            showdialog(['This element name already exists'])
        else:
            conditions_met += 1

        # Check Radio button
        if self.rdl_yes.isChecked() or self.rdl_no.isChecked():
            conditions_met +=1
        else:
            showdialog(['Please select an option for total Gain/Loss'])

        # Do its normal accept stuff
        if conditions_met == 2:
            super().accept()

    def element_type_selected(self):
        selected_element_type = self.cmb_element_type.currentText()
        logger.debug(f'Element type selected {selected_element_type}')

        # Prevents error when starting and type is ''
        if selected_element_type in self.element_ref.keys():
            self.refresh_param_set(selected_element_type)

    
    def param_set_selected(self):
        param_set = self.cmb_set_param.currentText()
        logger.debug(f'Selected: {param_set}')
        if (param_set != '') and (self.rdl_yes.isChecked() or self.rdl_no.isChecked()):
            self.summarize_info()    

    def refresh_param_set(self, selected_elem_type):
        # Add available parameters to Parameters Set combobox
        self.cmb_set_param.clear()  # Ensures it start empty
        
        if self.rdl_yes.isChecked():
            self.cmb_set_param.addItem("gain_loss")
        
        elif self.rdl_no.isChecked():
            for param_set in self.element_ref[selected_elem_type].keys():
                if param_set != 'overall_description':
                    self.cmb_set_param.addItem(param_set)
    
    def yes_gain_clicked(self):
        # Add gain_loss parameters to Parameters Set combobox
        self.cmb_set_param.clear()  # Ensures it start empty
        self.cmb_set_param.addItem("gain_loss")
    
    def no_gain_clicked(self):
        ''' The user does not know the gain/loss value. The parameter is set based
                on the available sets that come with the selected Element Type'''

        self.element_type_selected()

    def summarize_info(self):
        ''' Show all the data the user has selected for the new Element'''
        
        # Gather all the Element parameters
        element_name = self.txt_element_name.text()  # Get the element name
        selected_elem_type = self.cmb_element_type.currentText()   # Get element type
        param_set = self.cmb_set_param.currentText()   # Get parameter set
        
        # Display information in the text box
        self.txt_summary.setPlainText("")   # Makes sure it starts empty
        #self.txt_summary.insertPlainText(f"Name: {element_name}")
        self.txt_summary.appendPlainText(f"Type: {selected_elem_type}")
        self.txt_summary.appendPlainText("Parameters: ")
        if self.rdl_yes.isChecked():
            self.txt_summary.appendPlainText("    - gain/loss")
        else:
            for parameters in self.element_ref[selected_elem_type][param_set].keys():
                self.txt_summary.appendPlainText(f"    - {parameters}")
        
        self.txt_summary.setReadOnly(True)  # Sets the text box as read-only
