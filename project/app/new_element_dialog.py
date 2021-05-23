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

        # Add available parameters to Element Type combobox
        self.cmb_element_type.clear() # Ensures it start empty
        for input_type in self.element_ref.keys():
            self.cmb_element_type.addItem(input_type)
            
        # Start with an empty Element Type combobox
        self.cmb_set_param.clear() # Ensures it start empty    
            
    def get_element_name(self):

        element_name = self.txt_element_name.toPlainText()
        return(element_name)
        
    def element_type_selected(self):
        selected_elment_type = self.cmb_element_type.currentText()
        return(selected_elment_type)
    
    
    def yes_gain_clicked(self):
        ''' The user knows the gain/loss value. The only parameter is therefore
        the gain/loss value'''
        
        # Add gain_loss parameters to Parameters Set combobox
        self.cmb_set_param.clear() # Ensures it start empty
        self.cmb_set_param.addItem("gain_loss")

    
    def no_gain_clicked(self):
        ''' The user does not know the gain/loss value. The parameter is set based
        on the available sets that come with the selected Element Type'''
        
        selected_elment_type = self.element_type_selected()
        
        # Add available parameters to Parameters Set combobox
        self.cmb_set_param.clear() # Ensures it start empty
        for param_set in self.element_ref[selected_elment_type].keys():
            self.cmb_set_param.addItem(param_set)
    
    def continue_clicked(self):
        ''' Show all the data the user has selected for the new Element'''
        
        # Gather all the Element parameters
        element_name = self.get_element_name()  # Get the element name
    
