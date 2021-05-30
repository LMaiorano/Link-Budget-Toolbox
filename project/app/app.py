#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: app.py
project: Link-Budget-Toolbox
date: 13/05/2021
author: Luigi Maiorano
"""

import sys
from pathlib import Path

import yaml
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, \
    QHeaderView, QLineEdit
from loguru import logger
import numpy as np
import traceback


from project.app.new_element_dialog import NewElementDialog
from project.app.rename_element_dialog import RenameElementDialog
from project.process import main_process
from project.app.custom_objects import *

from project.settings import ELEMENT_REFERENCE, DEFAULT_APP_CONFIG, CONFIGS_DIR, APP_UI_DIR





mainwindow_form_class = uic.loadUiType(Path(APP_UI_DIR, 'main_window.ui'))[0]

class MainWindow(QMainWindow, mainwindow_form_class):
    '''Main window of the LinkBudget Toolbox

    All user-interface logic is defined here. This app purely assist in the creation and
    modification of LinkBudget configuration files. These can also be edited manually, but with
    the risk of improper parameters and/or attributes. The calculations are exclusively performed
    by process.py, which can be run independently of this User Interface.

    User Interface Design:
    ----------------------
    The layout and construction of each window or dialog is stored in the *.ui files,
    which are generated and modified using QtDesigner. The object names defined in QtDesigner
    automatically become class attributes here in Python, and can be used accordingly. These ui
    files are dynamically loaded at each run and SHOULD NEVER BE MODIFIED DIRECTLY. Modifications
    will be overwritten by QtDesigner.

    Signals/Slots:
    --------------
    Connections between UI objects and their corresponding functions is done using signals/slots.
    ALL of these are specified in QtDesigner, where the slot is the <class method name>+() added
    manually in the 'Signals/Slots of MainWindow - Qt Designer' editor.
    Any action by the user that should trigger a function is linked in this way. A regular naming
    scheme is used for these class methods: '_clicked' or '_edited' as the suffix of the method name.
    This clarifies for the developer which class methods are run by signals/slots and which are
    purely program logic.

    App Setup:
    ----------
    File paths of the default configuration to be loaded or element_reference should be changed
    in settings.py
    '''
    def __init__(self, **kwargs):
        '''Initialization of the Main Window

        Parameters
        ----------
        **kwargs : dict, optional
            Extra arguments to 'MainWindow'. See settings.py for default file paths
            | 'UI_decimal_accuracy': (Default = 2) Decimals to show in UI
        '''
        QMainWindow.__init__(self, parent=None)
        self.setupUi(self)

        self.decimals = kwargs.pop('UI_decimal_accuracy', 2)
        self.default_cfg = DEFAULT_APP_CONFIG

        # Set initial values and general attributes
        self.cfg_file = Path(self.default_cfg)
        self.cfg_data = self.read_config()
        self.element_details = self.read_config(file=ELEMENT_REFERENCE)

        # TABLE SETUP
        self.col_titles = ['Element Name', 'Attribute', 'Value', 'Units']
        self.res_col_titles = ['Total GAIN', 'Value', 'Units']
        self.name_col = 0
        self.attribute_col = 1
        self.value_col = 2
        self.units_col = 3


        # Load default configuration
        self.fill_input_table()
        self.fill_general_values()
        header = self.tbl_elements.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)


        # Ensure only numerical values are entered in input fields
        self.txt_in_power_W.setValidator(NotEmptyNumericValidator())
        self.txt_in_power_dbm.setValidator(NotEmptyNumericValidator())
        self.txt_threshold_W.setValidator(NotEmptyNumericValidator())
        self.txt_threshold_dbm.setValidator(NotEmptyNumericValidator())



    def open_config_clicked(self):
        '''Opens a file dialog to select a config file'''

        dlg = QFileDialog()
        
        file_path = dlg.getOpenFileName(self, 'Open YAML Configuration FIle',
                                        directory=str(CONFIGS_DIR),
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
            self.fill_general_values()
        except Exception as E:
            logger.debug(f'Error loading file: {E}')
            logger.debug(traceback.format_exc())
            if not isinstance(E, KeyError): # Some random exception that probably needs debugging
                msg = ''
            elif 'Configuration file' in E.args[0]: # KeyError originates from self.read_config()
                msg = E.args[0]
            else: # A different (unexpected) KeyError
                msg = f'Missing required section: "{E.args[0]}"'

            showdialog(['Please select a valid YAML configuration file', msg])


    def new_clicked(self):
        self.clear_table_elements()
        self.cfg_file = Path(self.default_cfg)
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
            required_sections = ['elements', 'general_values' ,'settings']
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

    def validate_input_values(self, allow_blank=False):
        '''Check whether all values in input table can be converted to float

        Parameters
        ----------
        allow_blank : bool, optional
            (Default False) Whether blank values are allowed. This is allowed when deleting
                an element

        Returns
        -------
        bool
        '''
        try:
            for r in range(self.tbl_elements.rowCount()):
                val = self.tbl_elements.item(r, self.value_col).text()
                if allow_blank and val == '':
                    return True
                float(val)
            return True
        except ValueError:
            showdialog(['Please check that only numerical values are entered in the table'])
            return False

    def save_input_table(self, **kwargs):
        '''Save contents of Input Table to self.cfg_data dictionary

        Converts PyQt Table to an 'elements' dictionary of the same format
        as the input config file. This can be passed to the main process

        NOTE: This method must be called explicitly by other methods and cannot
        be bound to a cell-changed event, because of how new elements are generated

        Returns
        -------
        None
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

        # Check if data in table is valid
        allow_blank = kwargs.pop('allow_blank', False)
        valid_data = self.validate_input_values(allow_blank=allow_blank)
        if not valid_data:
            return

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
            if element_link_type == 'GENERIC':
                units = self.get_attribute_details(data, gain=True)['units']
                descr = self.get_attribute_details(data, gain=True)['description']

                value = data['gain_loss']
                if value is None:
                    value = ''

                self.tbl_elements.setItem(row, self.attribute_col,
                                          AttributeTableItem('Gain',
                                                             type='gain_loss',
                                                             description=descr))
                self.tbl_elements.setItem(row, self.value_col,
                                          ValueTableItem(str(value)))
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

                    try:
                        value_text = f"{val:.{self.decimals}f}"
                    except ValueError:
                        # Occurs with new element where default value is ''
                        value_text = val

                    # Add attribute cells
                    self.tbl_elements.setItem(row, self.attribute_col,
                                              AttributeTableItem(param, description=descr))

                    self.tbl_elements.setItem(row, self.value_col,
                                              ValueTableItem(value_text, range=val_range))

                    self.tbl_elements.setItem(row, self.units_col,
                                              UnitsTableItem(units))
                    row += 1


            # Make name cell span all other rows
            self.tbl_elements.setSpan(start_row, self.name_col, row-start_row, 1)

        # Show table
        self.tbl_elements.show()


    def fill_general_values(self):
        in_power  = self.cfg_data['general_values']['input_power']
        threshold = self.cfg_data['general_values']['rx_sys_threshold']

        if in_power is None:
            in_power = 0
        if threshold is None:
            threshold = 0

        self.txt_in_power_dbm.setText(f'{in_power}')
        self.txt_threshold_dbm.setText(f'{threshold}')

        # Update Watt Fields
        self.sync_input_fields(self.txt_in_power_dbm, self.txt_in_power_W,
                               self.dBm_to_W, sigfigs=5)
        self.sync_input_fields(self.txt_threshold_dbm, self.txt_threshold_W,
                               self.dBm_to_W, sigfigs=5)


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

            title = AttributeTableItem(f'{name}', description=descr)
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

        Reads data from element_reference.yaml using a specific element.
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
        link_type = element['link_type']
        input_type = element['input_type']


        if link_type == 'gain_loss' or gain: # Parameter_set not relevant because gain is directly given
            return self.element_details['GENERIC']['gain_loss']['gain_loss']

        param_set_details = self.element_details[link_type][input_type]
        if specific_parameter: # If a specific parameter is requested
            return param_set_details[specific_parameter]

        # Otherwise return all parameters
        return param_set_details


    def add_element_clicked(self):
        '''Adds new row to column, could be expanded to add a preset number of rows'''
        self.save_input_table()

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
            data['gain_loss'] = ''
        else:
            param_set_details = self.get_attribute_details(data)
            data['parameters'] = {}
            for param in param_set_details.keys():
                data['parameters'][param] = ''

        return data


    def delete_element_clicked(self):
        '''Deletes the selected table element'''

        selected = self.tbl_elements.selectedItems()
        logger.debug(f'Num selected: {len(selected)}')
        if len(selected) == 0:
            return # quit because no rows selected


        col_L = selected[0].column()

        if col_L == 0: # Element name must be selected, so you cant remove individual attributes
            rows = sorted([cell.row() for cell in selected])
            logger.debug(f'Removing rows: {rows}')

            for row in reversed(rows): # Must remove from bottom up, else indexes gets confused
                self.tbl_elements.removeRow(row)

        self.save_input_table(allow_blank=True)


    def input_table_double_clicked(self, row, column):
        if column == self.name_col:
            self.rename_element()

    def rename_element(self):
        selected = self.tbl_elements.selectedRanges()
        if len(selected) == 0:
            return  # quit because no rows selected

        # Get existing names, (cannot have a dupicate, due to dictionary structure)
        existing_element_names = [name.lower() for name in self.cfg_data['elements'].keys()]

        col_L = selected[0].leftColumn()
        if col_L == 0:  # Element name must be selected
            old_name = self.tbl_elements.item(selected[0].topRow(), self.name_col).text()
            dlg = RenameElementDialog(old_name, existing_element_names)
            accepted = dlg.exec()

            if accepted:
                new_name = dlg.txt_name.text()

                old_elem = self.cfg_data['elements'].pop(old_name)
                self.cfg_data['elements'][new_name] = old_elem

                self.fill_input_table()

    def run_process_clicked(self):
        '''Run Analysis button clicked in UI, which calculates the link budget'''
        logger.info('Running main process')

        # Check if data in table is valid
        valid_data = self.validate_input_values()
        if not valid_data:
            return

        # Update cfg_data elements
        self.save_input_table()

        self.cfg_data = main_process(self.cfg_data)

        # Convert any possible float64 values to float
        for elem, data in self.cfg_data['elements'].items():
            for attr, val in data.items():
                try:
                    self.cfg_data['elements'][elem][attr] = float(val)
                except (ValueError, TypeError):
                    pass # Strings or None's do not need to be converted

        for name, val in self.cfg_data['general_values'].items():
            try:
                self.cfg_data['general_values'][name] = float(val)
            except (ValueError, TypeError):
                pass  # Strings or None's do not need to be converted

        self.fill_results_table(self.cfg_data['elements'])


        # Display Final Values
        gain_sum = self.cfg_data['general_values']['total_gain']
        margin = self.cfg_data['general_values']['total_margin']


        self.txt_total.setText(f'{gain_sum:.{self.decimals}f}')
        self.txt_margin.setText(f'{margin:.{self.decimals}f}')

        self.btn_save_results.setEnabled(True)

    def save_config_clicked(self):
        '''Save current configuration to yaml file'''

        # Update cfg_data elements
        valid_data = self.validate_input_values()
        if not valid_data:
            return  # Abort saving, values must first be fixed


        # Create file dialog to get save location
        dlg = QFileDialog()
        file_path = dlg.getSaveFileName(self, 'Save YAML Configuration FIle',
                                        directory=str(CONFIGS_DIR),
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


    @staticmethod
    def W_to_dBm(W):
        '''Converts Watts to Decibel-milliwatts

        Parameters
        ----------
        W   : float
            Watts to convert
        Returns
        -------
        float
        '''
        return 30 + 10 * np.log10(W)

    @staticmethod
    def dBm_to_W(dBm):
        '''Converts Decibel-milliwatts to Watts

        Parameters
        ----------
        dBm : float
            Decibel-milliwatts to convert
        Returns
        -------
        float
        '''
        return 10 ** ((dBm - 30) / 10)

    @staticmethod
    def sync_input_fields(in_field, out_field, convert_fn, sigfigs=4):
        '''Updates the text in one QLineEdit field based on another field

        Parameters
        ----------
        in_field : QLineEdit
            QLineEdit to source the value from
        out_field : QLineEdit
             QLineEdit to write the converted value to
        convert_fn : function
            Function used to convert the value from in_field to out_field
        sigfigs : int, optional
            Number of significant figures to display in out_field

        Returns
        -------
        None
            Modifies out_field directly
        '''
        if in_field.text() in ['', '-']:
            in_field.setText('0.0')

        val_in = float(in_field.text())
        out_field.setText(f'{convert_fn(val_in):.{sigfigs}g}')


    def input_power_W_edited(self):
        self.sync_input_fields(self.txt_in_power_W, self.txt_in_power_dbm,
                               self.W_to_dBm)
        self.txt_in_power_dbm_changed()

    def input_power_dbm_edited(self):
        self.sync_input_fields(self.txt_in_power_dbm, self.txt_in_power_W,
                               self.dBm_to_W, sigfigs=5)
        self.txt_in_power_dbm_changed()

    def threshold_W_edited(self):
        self.sync_input_fields(self.txt_threshold_W, self.txt_threshold_dbm,
                               self.W_to_dBm)
        self.txt_threshold_dbm_changed()

    def threshold_dbm_edited(self):
        self.sync_input_fields(self.txt_threshold_dbm, self.txt_threshold_W,
                               self.dBm_to_W, sigfigs=5)
        self.txt_threshold_dbm_changed()

    def txt_threshold_dbm_changed(self):
        threshold = float(self.txt_threshold_dbm.text())
        self.cfg_data['general_values']['rx_sys_threshold'] = threshold

    def txt_in_power_dbm_changed(self):
        power = float(self.txt_in_power_dbm.text())
        self.cfg_data['general_values']['input_power'] = power




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
    set_log_level('DEBUG')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    app.exec()