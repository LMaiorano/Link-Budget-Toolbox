#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: new_element_dialog.py
project: Link-Budget-Toolbox
date: 17/05/2021
author: Nicolas Fosseprez
"""

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QDialog
from project.app.custom_objects import showdialog
from loguru import logger
from pathlib import Path
from project.settings import APP_UI_DIR


newelement_form_class = uic.loadUiType(Path(APP_UI_DIR, 'new_element.ui'))[0]

class NewElementDialog(QDialog, newelement_form_class):
    ''' Dialog window when creating a New Element in the LinkBudget Toolbox
    
    This code defines the user-interface logic for the New Element dialog. It is
    an extension to the code defined in app.py and cannot be run on its own. To see
    this code in action, you have to run app.py.  
    
    User Interface Design:
    ----------------------
    PLEASE READ the instructions on how to use QtDesigner in app.py. 
    
    App Setup:
    ----------
    File paths of the default configuration to be loaded or element_reference should be changed
    in settings.py
    
    '''
    
    
    def __init__(self, element_reference, existing_names, parent=None):
        '''Initialization of the New Element dialog window

        Parameters
        ----------
        element_reference : dict
            Dictionary of the default elements defined in element_reference.yaml.
        existing_names : list
            List of the element names in the configuration file.
        parent : class, optional
            Parent classes can be specified. The default is None.

        Returns
        -------
        None.

        '''
        
        
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
        
        conditions_unmet = 2

        # Check Name
        name = self.txt_element_name.text()
        if len(name) == 0:  # Check that a name has been written
            showdialog(['The new element must have a name'])
        elif name.lower() in self.existing_names:   # Check if that name was already given previously
            showdialog(['This element name already exists'])
        else:
            conditions_unmet -= 1

        # Check Radio button
        if self.rdl_yes.isChecked() or self.rdl_no.isChecked():
            conditions_unmet -=1    # The Yes or No radio button must be clicked
        else:
            showdialog(['Please select an option for total Gain/Loss'])

        # Do its normal accept stuff
        if conditions_unmet == 0:
            super().accept()

    def yes_gain_clicked(self):
        ''' The user already knows the gain or loss of the new element. 
        
        The element is therefore a Generic type of element. The only parameter 
        for that is the gain/loss. 
        When clicked, the comboboxes are updated.   
        
        '''
        
        
        # Add available parameters to Element Type combobox
        self.cmb_element_type.clear() # Ensures it start empty
        self.cmb_element_type.addItem("GENERIC")
            
        # Add gain_loss parameters to Parameters Set combobox
        self.cmb_set_param.clear()  # Ensures it start empty
        self.cmb_set_param.addItem("gain_loss")
        
    
    def no_gain_clicked(self):
        ''' The user does not know the gain/loss value. 
        
        A few element types are suggested in the combobox that the user can
        choose from.
        The Generic type is not suggested as the user does not know the gain
        nor loss.        
        
        '''

        # Add available parameters to Element Type combobox except Generic Type.
        self.cmb_element_type.clear() # Ensures it start empty
        for input_type in self.element_ref.keys():
            if input_type != 'GENERIC':
                self.cmb_element_type.addItem(input_type)   


    def element_type_selected(self):
        ''' The user selects an element type in the combobox.

        When an element type is selected, the parameter set combobox is refreshed
        with the according sets of parameters for that particular element type.
        
        The Description textbox is updated.

        '''
        
        selected_element_type = self.cmb_element_type.currentText()
        logger.debug(f'Element type selected {selected_element_type}')

        # Prevents error when starting and type is ''
        if selected_element_type in self.element_ref.keys():
            # Refresh Parameter Set combobox
            self.refresh_param_set(selected_element_type)
            # Display Element Type description
            self.show_overall_desc(selected_element_type)   

    
    def param_set_selected(self):
        ''' The user selects a parameter set in the combobox.

        When a parameter set is selected, the Required Inputs textbox is updated.

        '''
        param_set = self.cmb_set_param.currentText()
        logger.debug(f'Selected: {param_set}')
        
        # Conditions MUST be met before displaying information on parameter set:
        #   a paramater set is chosen AND yes/no radial is checked
        if (param_set != '') and (self.rdl_yes.isChecked() or self.rdl_no.isChecked()):
            self.summarize_info()    

    def refresh_param_set(self, selected_elem_type):
        ''' The parameter set combobox is refreshed when an element type has
        been chosen.
        
        If the user knows the gain or loss of the element type, only the gain_loss 
        is proposed as parameters.
        Otherwise, all parameter sets of the selected element type are proposed.

        Parameters
        ----------
        selected_elem_type : string
            Dictionary key of the element type.

        Returns
        -------
        None.

        '''
        # Add available parameters to Parameters Set combobox
        self.cmb_set_param.clear()  # Ensures it start empty
        
        # If Yes is checked, only gain_loss is proposed
        if self.rdl_yes.isChecked():    
            self.cmb_set_param.addItem("gain_loss")
        
        # If No checked, propose all parameter sets
        elif self.rdl_no.isChecked():
            for param_set in self.element_ref[selected_elem_type].keys():
                # overall_description is not a parameter set in the dictionary
                if param_set != 'overall_description':
                    self.cmb_set_param.addItem(param_set) # Add each parameter set
    
    def show_overall_desc(self, selected_element_type):
        '''Shows description of the selected element type. 
        
        The Description textbox is updated with the description of the element
        type as defined in element_reference.yaml.
        The textbox can only be read by the user.
        
        Parameters
        ----------
        selected_element_type : string
            Dictionary key of the element type.

        Returns
        -------
        None.

        '''
        # Only updates if a radio button is checked
        if self.rdl_yes.isChecked() or self.rdl_no.isChecked():
            description = self.element_ref[selected_element_type]['overall_description']
            # Display information in the text box
            self.txt_description.setPlainText("")   # Makes sure it starts empty
            self.txt_description.insertPlainText(f"{description}")

    def summarize_info(self):
        ''' Show a summary of the inputs the user will have to specif for the
        new Element.
        
        A summary is given of the selected element type and the parameters 
        that the user will have to specify later.
        The textbox can only be read by the user.
        
        '''
        
        # Gather all the Element parameters
        selected_elem_type = self.cmb_element_type.currentText()   # Get element type
        param_set = self.cmb_set_param.currentText()   # Get parameter set
        
        # Display information in the text box
        self.txt_summary.setPlainText("")   # Makes sure it starts empty
        self.txt_summary.appendPlainText(f"Type: {selected_elem_type}")
        self.txt_summary.appendPlainText("Parameters: ")
        if self.rdl_yes.isChecked():
            self.txt_summary.appendPlainText("    - gain/loss")
        else:
            for parameters in self.element_ref[selected_elem_type][param_set].keys():
                self.txt_summary.appendPlainText(f"    - {parameters}")
        
        self.txt_summary.setReadOnly(True)  # Sets the text box as read-only
