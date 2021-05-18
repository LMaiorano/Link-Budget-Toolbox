#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: app.py
project: Link-Budget-Toolbox
date: 13/05/2021
author: lmaio
"""

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, \
    QTableWidget, QCheckBox, QHeaderView, QRadioButton, QMessageBox, \
    QDialog
from PyQt5.QtGui import QFont

from pathlib import Path
import sys
from loguru import logger
import yaml
import numpy as np

from project.process import main_process
from project.app.new_element_dialog import NewElementDialog



mainwindow_form_class = uic.loadUiType('ui/main_window.ui')[0]




class MainWindow(QMainWindow, mainwindow_form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # Set initial values and general attributes
        self.cfg_file = Path('../configs/default_config.yaml')
        self.cfg_data = self.read_config()
        self.element_details = self.read_config(file='../element_config_reference.yaml')
        self.result_data = None

        # TABLE SETUP
        self.col_titles = ['Element Name', 'Attribute', 'Value', 'Units']
        self.name_col = 0
        self.attribute_col = 1
        self.value_col = 2
        self.units_col = 3

        # Load default configuration
        self.fill_table()
        header = self.tbl_elements.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)





    def open_config_clicked(self):
        '''Opens a file dialog to select a config file'''

        dlg = QFileDialog()
        
        file_path = dlg.getOpenFileName(self, 'Open YAML Configuration FIle',
                                        directory='../configs',
                                        filter='Config Files (*.yaml)')[0]
        if file_path == '':
            return # Dialog cancelled, Exit this
        
        self.cfg_file = Path(file_path)
        self.lbl_config_file.setText(self.cfg_file.name)
        
        logger.debug(f"Config file set to {self.cfg_file}")
        
        try:
            self.cfg_data = self.read_config()
            self.clear_table_elements()
            self.fill_table()
        except Exception as E:
            logger.debug(f'Error loading file: {E}')

            if not isinstance(E, KeyError): # Some random exception that probably needs debugging
                msg = ''
            elif 'Configuration file' in E.args[0]: # KeyError originates from self.read_config()
                msg = E.args[0]
            else: # A different (unexpected) KeyError
                msg = f'Missing required section: "{E.args[0]}"'

            showdialog(['Please select a valid YAML configuration file', msg])

    def new_clicked(self):
        self.clear_table_elements()
        self.cfg_file = Path('../configs/default_config.yaml')
        self.cfg_data = self.read_config()
        self.fill_table()


    def read_config(self, file=None):
        '''Reads and loads YAML configuration file to a dictionary

        Parameters
        ----------
        file: str
            (default: self.cfg_file) Filepath of yaml configuration to load

        Returns
        -------
        dict
            Dictionary from yaml file
        '''
        if file is None:
            file = self.cfg_file

        with open(file, 'r') as f:
            data = yaml.full_load(f)

        # verify basic elements
        if file == self.cfg_file:
            required_sections = ['elements', 'generic_values', 'settings']
            for sect in required_sections:
                if sect not in data.keys():
                    raise KeyError(f'Configuration file missing required section: "{sect}"')

            # Add a default index (top) if missing in element configuration
            for element in data['elements'].values():
                if 'index' not in element.keys():
                    element['index'] = 0


        return data

    def clear_table_elements(self):
        '''Clears input table'''
        self.tbl_elements.clearContents()

    def fill_table(self):
        '''Populate table with elements listed in config file

        This converts the data dictionary elements to the necessary table items
        The table consists of four columns: Element, Attribute, Value, Units
        '''
        # TODO: add index attribute to config file to remember order for results table
        elements = self.cfg_data['elements']       # Select sub-dictionary of elements from config

        # Determine number of rows needed for table  rows are: name + gainloss + each parameter
        n_rows = 0
        for elem in elements.values():
            try:
                n_rows += 1 + len(elem['parameters'])
            except KeyError: # this link element has no parameters, so just a gain_loss
                n_rows += 1

        # Create empty table of correct size
        self.tbl_elements.setColumnCount(len(self.col_titles))
        self.tbl_elements.setRowCount(n_rows)

        # Set row/column labels
        self.tbl_elements.setHorizontalHeaderLabels(self.col_titles)
        self.tbl_elements.verticalHeader().setVisible(False)

        # Set Font of element titles
        element_font = QFont()
        element_font.setBold(True)

        # Order elements according to their saved index
        elements_ordered = {key: val for key, val in sorted(elements.items(), key=lambda item: item[1]['index'])}

        row = 0
        for name, data in elements_ordered.items():
            start_row = row

            # ---------------------- Element Title ------------------------------------
            # fixes capitalization, keeping abbreviations in full caps
            name = name.replace("_", " ")
            name = " ".join([w.title() if w.islower() else w for w in name.split()])

            # Create element title table item, containing other attributes needed later for saving
            element_link_type = data['link_type']
            element_input_type = data['input_type']
            title = ElementTableItem(name,
                                     link_type=element_link_type,
                                     input_type=element_input_type)

            # Set to format as specified above (bold)
            title.setFont(element_font)
            # Add title element to table
            self.tbl_elements.setItem(row, self.name_col, title)

            # ------------------------- Attributes ------------------------------------
            units = self.get_attribute_details(data, gain=True)['units']
            descr = self.get_attribute_details(data, gain=True)['description']

            self.tbl_elements.setItem(row, self.attribute_col,
                                      AttributeTableItem('Gain', type='gain_loss',
                                                         description=descr))
            self.tbl_elements.setItem(row, self.value_col,
                                      QTableWidgetItem(str(data['gain_loss'])))
            self.tbl_elements.setItem(row, self.units_col,
                                      UnitsTableItem(units))
            row +=1

            # --------------------- Parameters
            try: # If link element has parameters
                for param, val in data['parameters'].items():
                    units = self.get_attribute_details(data, parameter=param)['units']
                    descr = self.get_attribute_details(data, parameter=param)['description']

                    self.tbl_elements.setItem(row, self.attribute_col,
                                              AttributeTableItem(param, description=descr))

                    self.tbl_elements.setItem(row, self.value_col,
                                              QTableWidgetItem(str(val)))

                    self.tbl_elements.setItem(row, self.units_col,
                                              UnitsTableItem(units))
                    row += 1
            except KeyError:
                logger.debug(f'{name} does not have parameters')

            # Make name cell span all other rows
            self.tbl_elements.setSpan(start_row, self.name_col, row-start_row, 1)

        # Show table
        self.tbl_elements.show()

    def get_attribute_details(self, element:dict, parameter=None, gain=False):
        '''Gets details about an element's parameters

        Reads data from element_config_reference.yaml using a specific element.
        The link_type and input_type are used to determine which parameter set is applicable

        Parameters
        ----------
        element : dict
            A specific element dictionary as specified in the configuration files
        parameter : dict
            (Default: None) Which parameter to return. If not specified, a full dict of all params will be returned.
            If input_type is 'gain_loss', then this is not relevant
        gain : bool
            (Default: False) Whether to return details only about the Gain attribute

        Returns
        -------
        dict
            {'description': xx, 'units': xx} of either: all parameters for a specific input_type or
            of a specific parameter (if specified)


        '''
        input_type = element['input_type']

        if input_type == 'gain_loss' or gain: # Parameter_set not relevant because gain is directly given
            return self.element_details['GENERIC']['gain_loss']

        param_set_details = self.element_details[element['link_type']][input_type]
        if parameter: # If a specific parameter is requested
            return param_set_details[parameter]

        # Otherwise return all parameters
        return param_set_details



    def add_element_clicked(self):
        '''Adds new row to column, could be expanded to add a preset number of rows'''
        # self.tbl_elements.insertRow(self.tbl_elements.rowCount())
        # self.tbl_elements.show()
        new = NewElementDialog()
        exit_successful = new.exec_()
        print(exit_successful)

        self.save_input_table_to_dict()

    def delete_element_clicked(self):
        '''Deletes the selected table element'''

        selected = self.tbl_elements.selectedRanges()
        if len(selected) == 0:
            return # quit because no rows selected

        col_L = selected[0].leftColumn()

        if col_L == 0: # Element name must be selected, so you cant remove individual attributes
            start = selected[0].topRow()
            end =  selected[-1].bottomRow()
            logger.debug(f'Delete range: {start} - {end}')

            for row in range(end, start-1, -1):
                self.tbl_elements.removeRow(row)

            self.save_input_table_to_dict()


    def run_process_clicked(self):
        '''Run Analysis button clicked in UI, which calculates the link budget'''
        logger.info('Running main process')
        self.result_data = main_process(self.cfg_data)
        # TODO: display results


    def display_results(self):
        '''Display the results in the results table'''
        raise NotImplementedError


    def save_config_clicked(self):
        '''Save current configuration to yaml file'''

        # Update cfg_data elements
        self.save_input_table_to_dict()

        # Create file dialog to get save location
        dlg = QFileDialog()
        file_path = dlg.getSaveFileName(self, 'Save YAML Configuration FIle',
                                        directory='../configs',
                                        filter='Config Files (*.yaml)')[0]
        if file_path == '':
            return  # Dialog cancelled, Exit this saving process

        file_path = Path(file_path)

        # Ensure file is saved as .yaml
        if file_path.suffix != '.yaml':  # Wrong suffix given
            file_path = Path(file_path.parent, file_path.name + '.yaml')

        # update current cfg file to the one being saved
        self.cfg_file = file_path
        self.lbl_config_file.setText(self.cfg_file.name)

        # Write full config to file specified above
        with open(self.cfg_file, 'w') as f:
            yaml.dump(self.cfg_data, f)

        logger.debug(f"Config saved to {self.cfg_file}")

    def save_input_table_to_dict(self):
        '''Convert PyQt Table to an 'elements' dictionary of the same format
        as the input config file. This can be passed to the main process

        Note: This must be called explicitly and cannot be bound to a cell-changed event,
        because of how new elements are generated
        '''
        data = {}
        parameters = {}
        element_name = None
        index = 0
        for r in range(self.tbl_elements.rowCount()):
            # Check if row is a new element
            elem_item = self.tbl_elements.item(r, self.name_col)
            if isinstance(elem_item, ElementTableItem):
                # save previous parameters if they exist
                if element_name and parameters:
                    data[element_name]['parameters'] = parameters
                    parameters = {} # reset to empty

                index += 1
                element_name = elem_item.text()
                link_type = elem_item.link_type
                input_type = elem_item.input_type

                data[element_name] = {'input_type': input_type,
                                      'link_type': link_type,
                                      'index': index}

            # Use last defined element name for the remaining parameters, skip if not defined
            if element_name:
                attribute = self.tbl_elements.item(r, self.attribute_col)

                # Extract attribute name, depending on how data was inserted into cell
                attribute_type = attribute.type
                if attribute_type == 'gain_loss':
                    name = 'gain_loss'
                else:
                    name = attribute.text()

                value = self.tbl_elements.item(r, self.value_col).text()

                # Decide where to save name:value
                if attribute_type == 'parameter':
                    parameters[name] = value
                else:
                    data[element_name][name] = value

        # save last set of parameters if they exist
        if element_name and parameters:
            data[element_name]['parameters'] = parameters

        self.cfg_data['elements'] = data






class ElementTableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        '''Custom TableWidgetItem to allow other attributes to be stored.

        This is necessary so that additional link element properties can be saved
        in the data dictionary which is passed to the main process
        '''
        self.link_type = kwargs.pop('link_type', 'gainloss')
        self.input_type = kwargs.pop('input_type', 'GENERIC')
        super().__init__(*args, **kwargs)
        self.setToolTip(f'Type: {self.link_type}')


class AttributeTableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        '''Custom TableWidgetItem to allow other attributes to be stored.

        This is necessary so that additional link element properties can be saved
        in the data dictionary which is passed to the main process
        '''
        self.type = kwargs.pop('type', 'parameter')
        self.description = kwargs.pop('description', 'Link element attribute')
        super().__init__(*args, **kwargs)
        self.setToolTip(self.description)

        self.setFlags(QtCore.Qt.ItemIsEnabled) # not selectable or editable

class UnitsTableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        '''Custom TableWidgetItem to allow other attributes to be stored.

        This is necessary so that additional link element properties can be saved
        in the data dictionary which is passed to the main process
        '''
        super().__init__(*args, **kwargs)
        self.setFlags(QtCore.Qt.ItemIsEnabled) # not selectable or editable




def showdialog(message: list, level='warning'):
    '''Popup dialog box to warn user of some sort of error or other information

    Parameters
    ----------
    message : [str]
        List of message strings. The first (required) is the main message. The
            second (optional) is additional detailed information
    level : str
        Sets type and icon of message box. (default: 'warning'),
        or 'question', 'information', 'critical'

    Returns
    -------
        Exit status of QMessageBox()
    '''
    if not isinstance(message, list):
        raise TypeError('Message must be a list of strings')
    icon = QMessageBox.Warning
    if level == 'question':
        icon = QMessageBox.Question
    elif level == 'information':
        icon = QMessageBox.Information
    elif level == 'critical':
        icon = QMessageBox.Critical

    msg = QMessageBox()
    msg.setIcon(icon)

    msg.setText(message[0])
    msg.setWindowTitle(level.capitalize())

    if len(message) > 1:
        msg.setInformativeText(message[1])
    if len(message) > 2:
        msg.setDetailedText(message[2])

    msg.setStandardButtons(QMessageBox.Ok)

    msg.exec_()
    return msg





if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    app.exec()