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

        # TABLE SETUP
        self.col_titles = ['Element Name', 'Attribute', 'Value']
        self.name_col = 0
        self.attribute_col = 1
        self.value_col = 2


        self.cfg_file = Path('../configs/default_config.yaml')
        self.cfg_data = self.read_config()
        self.tbl_elements: QTableWidget()
        self.fill_table()

        self.result_data = None

        # Setup Table Settings

        header = self.tbl_elements.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)


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
            self.clear_table()
        
            self.cfg_data = self.read_config()
        
            self.fill_table()
        except Exception as E:
            logger.debug(f'Error loading file: {E}')
            showdialog(['Please select a valid YAML configuration file'])

    def new_clicked(self):
        self.clear_table()
        self.cfg_file = Path('../configs/default_config.yaml')
        self.cfg_data = self.read_config()
        self.fill_table()


    def read_config(self) -> dict:
        '''Reads data out of a config file'''
        with open(self.cfg_file, 'r') as f:
            data = yaml.full_load(f)
        # TODO: check file for required basic structure/components, otherwise raise exception
        return data

    def clear_table(self):
        self.tbl_elements.clearContents()

    def fill_table(self):
        '''Populate table with elements listed in config file

        This converts the data dictionary elements to the necessary table items
        The table consists of three columns: Element, Attribute, Value
        The
        '''

        elements = self.cfg_data['elements']       # Select sub-dictionary of elements from config

        # Determine number of rows needed for table  rows are: name + gainloss + each parameter
        n_rows = sum([ (1 + len(elem['parameters'])) for elem in elements.values() ])

        self.tbl_elements.setColumnCount(len(self.col_titles))
        self.tbl_elements.setRowCount(n_rows)

        self.tbl_elements.setHorizontalHeaderLabels(self.col_titles)
        self.tbl_elements.verticalHeader().setVisible(False)

        element_font = QFont()
        element_font.setBold(True)

        row = 0
        for name, data in elements.items():
            start_row = row

            # ------ Element Title -------------
            # fixes capitalization, keeping abbreviations in full caps
            name = name.replace("_", " ")
            name = " ".join([w.title() if w.islower() else w for w in name.split()])

            # create custom table item, that contains other parameters needed later for saving
            title = LinkElementTableItem(name,
                                         link_type=data['link_type'],
                                         input_type=data['input_type'])

            # Set to format as specified above (bold)
            title.setFont(element_font)
            # disable editing of this item
            # title.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)

            self.tbl_elements.setItem(row, self.name_col, title)

            # ----- General Gain -------------
            self.tbl_elements.setItem(row, self.attribute_col, QTableWidgetItem('Gain [dB]'))
            self.tbl_elements.setItem(row, self.value_col, QTableWidgetItem(str(data['gain_loss'])))
            row +=1

            # Parameters
            for param, val in data['parameters'].items():
                # Give parameter a checkbox #TODO: enable checkbox only when necessary
                self.tbl_elements.setCellWidget(row, self.attribute_col, QCheckBox(param))
                self.tbl_elements.setItem(row, self.value_col, QTableWidgetItem(str(val)))
                row += 1

            # Make name cell span all other rows
            self.tbl_elements.setSpan(start_row, self.name_col, row-start_row, 1)

        # Set columns to automatically resize
        self.tbl_elements.show()


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
        element_name = None
        for r in range(self.tbl_elements.rowCount()):
            # Check if row is a new element
            new_elem_cell = self.tbl_elements.item(r, self.name_col)
            if isinstance(new_elem_cell, LinkElementTableItem):
                element_name = new_elem_cell.text()
                link_type = new_elem_cell.link_type
                input_type = new_elem_cell.input_type

                data[element_name] = {'input_type': input_type,
                                      'link_type': link_type}

            # Use last defined element name for the remaining parameters, skip if not defined
            if element_name:

                # Extract attribute name, depending on how data was inserted into cell
                if self.tbl_elements.cellWidget(r,
                                                self.attribute_col):  # returns none if incorrect cell type
                    attribute = self.tbl_elements.cellWidget(r, self.attribute_col).text()

                else:  # Assumes cell type is a QTableWidgetItem ('TWI')
                    attribute = self.tbl_elements.item(r, self.attribute_col).text()

                value = self.tbl_elements.item(r, self.value_col).text()

                data[element_name][attribute] = value

        self.cfg_data['elements'] = data






class LinkElementTableItem(QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        '''Custom TableWidgetItem to allow other attributes to be stored.

        This is necessary so that additional link element properties can be saved
        in the data dictionary which is passed to the main process
        '''
        self.link_type = kwargs.pop('link_type', 'gainloss')
        self.input_type = kwargs.pop('input_type', 'GENERIC')
        super().__init__(*args, **kwargs)
        self.setToolTip(f'Type: {self.link_type}')




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