#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: app.py
project: Link-Budget-Toolbox
date: 13/05/2021
author: lmaio
"""

import sys
from pathlib import Path

import yaml
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, \
    QHeaderView
from loguru import logger
# DO NOT REMOVE astropy
from astropy import units as u
import numpy as np

from project.app.new_element_dialog import NewElementDialog
from project.app.notification_dialog import showdialog
from project.process import main_process





mainwindow_form_class = uic.loadUiType('ui/main_window.ui')[0]

class MainWindow(QMainWindow, mainwindow_form_class):
    def __init__(self, parent=None, **kwargs):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        default_cfg = kwargs.pop('default_config_yaml', '../configs/default_config.yaml')
        element_ref = kwargs.pop('element_reference_yaml', '../element_config_reference.yaml')
        self.decimals = kwargs.pop('UI_decimal_accuracy', 2)

        # Set initial values and general attributes
        self.cfg_file = Path(default_cfg)
        self.cfg_data = self.read_config()
        self.element_details = self.read_config(file=element_ref)
        self.result_data = None

        # TABLE SETUP
        self.col_titles = ['Element Name', 'Attribute', 'Value', 'Units']
        self.res_col_titles = ['Total GAIN', 'Value', 'Units']
        self.name_col = 0
        self.attribute_col = 1
        self.value_col = 2
        self.units_col = 3


        # Load default configuration
        self.fill_input_table()
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
            self.fill_input_table()
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
        self.fill_input_table()


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
            required_sections = ['elements', 'settings']
            for sect in required_sections:
                if sect not in data.keys():
                    raise KeyError(f'Configuration file missing required section: "{sect}"')

            # Add a default index (top) if missing in element configuration
            for element in data['elements'].values():
                if 'idx' not in element.keys():
                    element['idx'] = 0


        return data


    def clear_table_elements(self):
        '''Clears input table'''
        self.tbl_elements.clearContents()
        self.tbl_elements.setRowCount(0)

        self.tbl_results.clearContents()
        self.tbl_results.setRowCount(0)
        self.tbl_results.setColumnCount(0)


    def clear_all_clicked(self):
        self.clear_table_elements()


    def save_input_table_to_dict(self, convert_SI_units=False):
        '''Convert PyQt Table to an 'elements' dictionary of the same format
        as the input config file. This can be passed to the main process

        NOTE: This method must be called explicitly by other methods and cannot
        be bound to a cell-changed event, because of how new elements are generated

        Parameters
        ----------
        convert_SI_units : bool
            Whether to convert values to standard SI units. This is used exclusively
            when called by self.run_process()

        Returns
        -------

        '''
        def wrap_up_previous_element(elem_name, params):
            '''Saves previous parameters if they exist to overall element dictionary'''
            if elem_name:  # Does not run for first element in table

                if len(params) > 0:  # Checks if parameters contain any values
                    data[elem_name]['parameters'] = params
                else:
                    # Saves parameters entry as null instead of empty dict
                    # a {key: empty dict} pair is ignored when writing to yaml, but null values are not
                    data[elem_name]['parameters'] = None

                # if gain_loss is not already added, include the default value of None
                if not data[elem_name].get('gain_loss'):
                    data[elem_name]['gain_loss'] = None


        data = {}               # Empty dict to build
        parameters = {}         # Parameter attributes that may be present in a link element
        element_name = None     # The current element being read, initialized to none
        idx = 0                 # The position in the table of the element (1 = top element)


        # Walk through each row of the table to detect new elements and read attributes
        for r in range(self.tbl_elements.rowCount()):
            # Check if this row is a new element
            elem_item = self.tbl_elements.item(r, self.name_col)
            if isinstance(elem_item, ElementTableItem):

                # First, wrap up previous element
                wrap_up_previous_element(element_name, parameters)
                parameters = {}

                # Then, start constructing next element
                idx += 1
                element_name = elem_item.text()
                link_type = elem_item.link_type
                input_type = elem_item.input_type

                data[element_name] = {'input_type': input_type,
                                      'link_type': link_type,
                                      'idx': idx}

            # Use last defined element name for the remaining parameters, skip if not yet defined
            if element_name:
                attribute = self.tbl_elements.item(r, self.attribute_col)

                # Extract attribute name, depending on how data was inserted into cell
                attribute_type = attribute.type
                if attribute_type == 'gain_loss':
                    name = 'gain_loss'
                else:
                    name = attribute.text()

                # if strings are entered, this will raise a TypeError to be caught by the click action
                value = self.tbl_elements.item(r, self.value_col).text()
                if value == '':
                    value = 0
                value = float(value)


                # Decide where to save name:value
                if attribute_type == 'parameter':
                    parameters[name] = value
                else:
                    data[element_name][name] = value


        wrap_up_previous_element(element_name, parameters)

        self.cfg_data['elements'] = data

        self.fill_input_table() # reload table with saved values (fills empty cells with 0)


    def fill_input_table(self):
        '''Populate table with elements in stored in the cfg_data attribute

        This converts the data dictionary elements to the necessary table items
        The table consists of four columns: Element, Attribute, Value, Units
        '''
        elements = self.cfg_data['elements']       # Select sub-dictionary of elements from config

        # Determine number of rows needed for table  rows are: name + gainloss + each parameter
        n_rows = 0
        for elem in elements.values():
            try:
                n_rows += len(elem['parameters'])
            except (KeyError, TypeError): # this link element has no parameters, so just a gain_loss
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
        elements_ordered = {key: val for key, val in sorted(elements.items(), key=lambda item: item[1]['idx'])}

        # Iterate through elements and add to rows
        row = 0
        for name, data in elements_ordered.items():
            start_row = row

            # ---------------------- Element Title ------------------------------------
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
            if element_input_type == 'gain_loss':
                units = self.get_attribute_details(data, gain=True)['units']
                descr = self.get_attribute_details(data, gain=True)['description']

                self.tbl_elements.setItem(row, self.attribute_col,
                                          AttributeTableItem('Gain',
                                                             type='gain_loss',
                                                             description=descr))
                self.tbl_elements.setItem(row, self.value_col,
                                          ValueTableItem(str(data['gain_loss'])))
                self.tbl_elements.setItem(row, self.units_col,
                                          UnitsTableItem(units))
                row +=1

            else: # If link element has parameters
            # --------------------- Parameters
                for param, val in data['parameters'].items():
                    # get attribute details
                    att_details = self.get_attribute_details(data, specific_parameter=param)
                    units = att_details.get('units')
                    descr = att_details.get('description')
                    val_range = att_details.get('range')

                    # Add attribute cells
                    self.tbl_elements.setItem(row, self.attribute_col,
                                              AttributeTableItem(param, description=descr))

                    self.tbl_elements.setItem(row, self.value_col,
                                              ValueTableItem(f"{val:.{self.decimals}f}", range=val_range))

                    self.tbl_elements.setItem(row, self.units_col,
                                              UnitsTableItem(units))
                    row += 1


            # Make name cell span all other rows
            self.tbl_elements.setSpan(start_row, self.name_col, row-start_row, 1)

        # Show table
        self.tbl_elements.show()


    def fill_results_table(self, results_data):

        # Determine number of rows needed for table. Stored to dict of element_name: rows
        n_rows = 0
        elem_rows = {}
        for name, elem in results_data.items():
            try:
                rows = len(elem['parameters'])
            except (KeyError, TypeError):  # this link element has no parameters, so just a gain_loss
                rows = 1
            elem_rows[name] = rows
            n_rows += rows


        # Create empty table of correct size
        self.tbl_results.setColumnCount(len(self.res_col_titles))
        self.tbl_results.setRowCount(n_rows)

        # Set row/column labels
        self.tbl_results.setHorizontalHeaderLabels(self.res_col_titles)
        self.tbl_results.verticalHeader().setVisible(False)

        title_font = QFont()
        title_font.setBold(True)


        # Order elements according to their saved index
        elements_ordered = {key: val for key, val in
                            sorted(results_data.items(), key=lambda item: item[1]['idx'])}

        row = 0
        for name, data in elements_ordered.items():
            start_row = row

            # Load these from element_config_reference for consistency, so it can be changed elsewhere
            units = self.get_attribute_details(data, gain=True)['units']
            descr = self.get_attribute_details(data, gain=True)['description']

            gain_item = QTableWidgetItem(f"{data['gain_loss']:.{self.decimals}f}")
            gain_item.setFlags(QtCore.Qt.ItemIsEnabled)

            title = AttributeTableItem(f'{name} Gain', description=descr)
            title.setFont(title_font)
            self.tbl_results.setItem(row, 0, title)
            self.tbl_results.setItem(row, 1, gain_item)
            self.tbl_results.setItem(row, 2, UnitsTableItem(units))


            # Make cells span all other rows of this element
            for r in range(len(self.res_col_titles)):
                self.tbl_results.setSpan(start_row, r, elem_rows[name], 1)

            row += elem_rows[name]

        # Show table
        self.tbl_results.show()
        header = self.tbl_results.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)


    def get_attribute_details(self, element:dict, specific_parameter=None, gain=False):
        '''Gets details about an element's parameters

        Reads data from element_config_reference.yaml using a specific element.
        The link_type and input_type are used to determine which parameter set is applicable

        Parameters
        ----------
        element : dict
            A specific element dictionary as specified in the configuration files
        specific_parameter : dict
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
        if specific_parameter: # If a specific parameter is requested
            return param_set_details[specific_parameter]

        # Otherwise return all parameters
        return param_set_details


    def add_element_clicked(self):
        '''Adds new row to column, could be expanded to add a preset number of rows'''
        # self.tbl_elements.insertRow(self.tbl_elements.rowCount())
        # self.tbl_elements.show()

        # Get existing names, (cannot have a dupicate, due to dictionary structure)
        existing_element_names = [name.lower() for name in self.cfg_data['elements'].keys()]

        # Open Dialog
        new_dlg = NewElementDialog(self.element_details, existing_element_names)
        exit_successful = new_dlg.exec_()

        if exit_successful:
            name = new_dlg.txt_element_name.text()              # get name
            elem_type = new_dlg.cmb_element_type.currentText()  # get link type
            gain_loss = new_dlg.rdl_yes.isChecked()             # get if total gain is known
            if gain_loss:
                param_set = 'gain_loss'
            else:
                param_set = new_dlg.cmb_set_param.currentText() # get parameter set

            # Create blank element dict
            new_element = self.build_empty_element(elem_type, param_set)

            # Add to active config
            self.cfg_data['elements'][name] = new_element
            logger.debug(f'Added element: {name}')

            # Reload table
            self.fill_input_table()


    def build_empty_element(self, link_type, input_type):
        # basic data
        data = {'gain_loss': None,
                'idx': np.inf,
                'input_type': input_type,
                'link_type': link_type,
                'parameters': None}

        # get exact parameters from reference (if not a basic gain_loss element)
        if input_type == 'gain_loss':
            data['gain_loss'] = '??'
        else:
            param_set_details = self.get_attribute_details(data)
            data['parameters'] = {}
            for param in param_set_details.keys():
                data['parameters'][param] = '??'

        return data


    def delete_element_clicked(self):
        '''Deletes the selected table element'''

        selected = self.tbl_elements.selectedRanges()
        if len(selected) == 0:
            return # quit because no rows selected

        col_L = selected[0].leftColumn()

        if col_L == 0: # Element name must be selected, so you cant remove individual attributes
            rows = sorted([cell.topRow() for cell in selected])
            logger.debug(f'Removing rows: {rows}')

            for row in reversed(rows): # Must remove from bottom up, else indexes gets confused
                self.tbl_elements.removeRow(row)



    def run_process_clicked(self):
        '''Run Analysis button clicked in UI, which calculates the link budget'''
        logger.info('Running main process')

        # Update cfg_data elements
        try:
            self.save_input_table_to_dict()
        except ValueError:
            showdialog(['Please check that only numerical values are entered'])
            return  # Abort saving file

        self.result_data = main_process(self.cfg_data)

        self.fill_results_table(self.cfg_data['elements'])

        self.sum_results() # Sum the values in the gain column and display in totals

        self.btn_save_results.setEnabled(True)


    def sum_results(self):
        sum = 0

        for r in range(self.tbl_results.rowCount()):
            gain_item = self.tbl_results.item(r, 1)
            if isinstance(gain_item, QTableWidgetItem):
                gain = gain_item.text()
                try:
                    sum += float(gain)

                except ValueError as E:
                    logger.debug(E)
                    showdialog([f'An error has occurred during the analysis:', 'One or more elements '
                                f'are missing a total gain'])

        # self.txt_total = QtWidgets.QLineEdit()
        self.txt_total.setText(f'{sum:.1f}')


    def save_config_clicked(self):
        '''Save current configuration to yaml file'''

        # Update cfg_data elements
        try:
            self.save_input_table_to_dict()
        except ValueError:
            showdialog(['Please check that only numerical values are entered'])
            return # Abort saving file


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


    def save_results_table_to_dict(self): # TODO: in progress. Not used anywhere yet
        '''Convert PyQt Table to an 'elements' dictionary of the same format
                as the input config file. This can be passed to the main process

                Note: This must be called explicitly and cannot be bound to a cell-changed event,
                because of how new elements are generated
                '''

        def wrap_up_previous_element(elem_name, params):
            if elem_name:  # Does not run for first element in table
                # Save previous parameters if they exist
                if len(params) > 0:  # Checks if parameters contain any values
                    data[elem_name]['parameters'] = params
                else:
                    # Saves parameters entry as null instead of empty dict
                    # a {key: empty dict} pair is ignored when writing to yaml, but null values are not
                    data[elem_name]['parameters'] = None

                # if gain_loss is not already added, include the default value of None
                if not data[elem_name].get('gain_loss'):
                    data[elem_name]['gain_loss'] = None

        data = {}  # Empty dict to build
        parameters = {}  # Parameter attributes that may be present in a link element
        element_name = None  # The current element being read, initialized to none
        idx = 0  # The position in the table of the element (1 = top element)

        # Walk through each row of the table to detect new elements and read attributes
        for r in range(self.tbl_elements.rowCount()):
            # Check if this row is a new element
            elem_item = self.tbl_elements.item(r, self.name_col)
            if isinstance(elem_item, ElementTableItem):
                # First, wrap up previous element
                wrap_up_previous_element(element_name, parameters)
                parameters = {}

                # Then, start constructing next element
                idx += 1
                element_name = elem_item.text()
                link_type = elem_item.link_type
                input_type = elem_item.input_type

                data[element_name] = {'input_type': input_type,
                                      'link_type': link_type,
                                      'idx': idx}

            # Use last defined element name for the remaining parameters, skip if not defined
            if element_name:
                attribute = self.tbl_elements.item(r, self.attribute_col)

                # Extract attribute name, depending on how data was inserted into cell
                attribute_type = attribute.type
                if attribute_type == 'gain_loss':
                    name = 'gain_loss'
                else:
                    name = attribute.text()

                # if strings are entered, this will raise a TypeError to be caught by the click action
                value = self.tbl_elements.item(r, self.value_col).text()
                if value == '':
                    value = 0
                value = float(value)

                # Decide where to save name:value
                if attribute_type == 'parameter':
                    parameters[name] = value
                else:
                    data[element_name][name] = value

        wrap_up_previous_element(element_name, parameters)

        self.cfg_data['elements'] = data

        self.fill_input_table()  # reload table with saved values (fills empty cells with 0)



class ElementTableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        '''Custom TableWidgetItem to allow other attributes to be stored.

        This is necessary so that additional link element properties can be saved
        in the data dictionary which is passed to the main process
        '''
        self.link_type = kwargs.pop('link_type', 'gain_loss')
        self.input_type = kwargs.pop('input_type', 'GENERIC')
        super().__init__(*args, **kwargs)
        self.setToolTip(f'Type: {self.link_type}')

        # not directly editable to prevent duplicate naming
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)


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


class ValueTableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        '''Custom TableWidgetItem to allow other attributes to be stored.

        This is necessary so that additional link element properties can be saved
        in the data dictionary which is passed to the main process
        '''
        self.range_raw = kwargs.pop('range', None)
        self.range_msg = ''
        self.bounds = self.eval_range()
        super().__init__(*args, **kwargs)


    def eval_range(self):
        range_raw = self.range_raw
        if range_raw is None:
            return None

        bounds = {}
        L, R = range_raw.replace(' ', '').split(',')

        # Left bound
        if L[0] == '(':
            bounds['left'] = L[1:] + ' <'
        else:
            bounds['left'] = L[1:] + ' <='

        # Right Bound
        if R[-1] == ')':
            bounds['right'] = '< ' + R[:-1]
        else:
            bounds['right'] = '<= ' + R[:-1]

        self.range_msg = self.format_range(bounds.copy()) # this can be used for information dialogs


        # convert inf to float("inf") which can be evaluated
        for k, v in bounds.items():
            bounds[k] = v.replace('inf', 'float("inf")')

        return bounds

    @staticmethod
    def format_range(b_dict):
        for k, v in b_dict.items():
            if 'inf' in v:
                b_dict[k] = ''

        return f"{b_dict['left']} Value {b_dict['right']}"


    def setData(self, role: int, value) -> None:
        # check input
        try:
            val_in = float(value)
        except ValueError:
            showdialog(['Only numerical values are allowed'], level='information')
        else:
            if self.bounds is None:
                super().setData(role, value)

            elif eval(f'{self.bounds["left"]} {val_in}') and eval(f'{val_in} {self.bounds["right"]}'):
                super().setData(role, value)

            else:
                showdialog([f'Entered value is not valid \n\n'
                            f'Required interval:\n{self.range_msg}'], level='information')


class UnitsTableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        '''Custom TableWidgetItem to allow other attributes to be stored.

        This is necessary so that additional link element properties can be saved
        in the data dictionary which is passed to the main process
        '''
        super().__init__(*args, **kwargs)
        self.setFlags(QtCore.Qt.ItemIsEnabled) # not selectable or editable



def set_log_level(log_level='INFO'):
    logger.remove()
    format_clean = '<cyan>{time:HH:mm:ss}</cyan> | ' \
                   '<level>{level: <8}</level> | ' \
                   '<level>{message}</level>'

    if log_level in ['INFO', 'SUCCESS']:
        logger.add(sys.stderr, level=log_level, format=format_clean)
    else:
        logger.add(sys.stderr, level="DEBUG")



if __name__ == '__main__':
    set_log_level('INFO')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow(UI_decimal_accuracy=2)
    window.show()
    app.exec()