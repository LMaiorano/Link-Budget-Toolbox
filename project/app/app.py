#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: app.py
project: Link-Budget-Toolbox
date: 13/05/2021
author: lmaio
"""

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem as TWI, \
    QTableWidget, QCheckBox, QHBoxLayout, QRadioButton
from PyQt5.QtGui import QFont

from pathlib import Path
import sys
from loguru import logger
import yaml
import numpy as np



mainwindow_form_class = uic.loadUiType('ui/main_window.ui')[0]

class MainWindow(QMainWindow, mainwindow_form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.cfg_file = Path('../configs/default_config.yaml')
        self.cfg_data = self.load_config()
        self.fill_table()


    def open_config_clicked(self):
        '''Opens a file dialog to select a config file'''
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)

        self.cfg_file = Path(dlg.getOpenFileName(self, directory='../configs')[0])
        self.lbl_config_file.setText(self.cfg_file.name)

        logger.debug(f"Config file set to {self.cfg_file}")

        self.cfg_data = self.load_config()

        self.fill_table()


    def load_config(self) -> dict:
        '''Reads data out of a config file'''
        with open(self.cfg_file, 'r') as f:
            data = yaml.full_load(f)
        return data


    def fill_table(self):
        '''Populate table with elements listed in config file'''
        # self.tbl_elements = QTableWidget()


        # TABLE SETUP
        col_titles = ['Element', 'Attribute', 'Value']
        name_col = 0
        param_col = 1
        value_col = 2



        elements = self.cfg_data['elements']       # Select sub-dictionary of elements from config

        # Determine number of rows needed for table  rows are: name + gainloss + each parameter
        n_rows = sum([ (1 + len(elem['parameters'])) for elem in elements.values() ])

        self.tbl_elements.setColumnCount(len(col_titles))
        self.tbl_elements.setRowCount(n_rows)

        self.tbl_elements.setHorizontalHeaderLabels(col_titles)
        self.tbl_elements.verticalHeader().setVisible(False)

        element_font = QFont()
        element_font.setBold(True)

        row = 0
        for name, data in elements.items():
            start_row = row

            # Element name. Fixes capitalization, keeping abbreviations in full caps
            name = name.replace("_", " ")
            name = " ".join([w.title() if w.islower() else w for w in name.split()])

            title = LinkElementTableItem(name)
            title.setFont(element_font)
            self.tbl_elements.setItem(row, name_col, title)

            # General Gain
            self.tbl_elements.setItem(row, param_col, TWI('Gain [dB]'))
            self.tbl_elements.setItem(row, value_col, TWI(str(data['gain_loss'])))
            row +=1

            # Parameters
            for param, val in data['parameters'].items():

                self.tbl_elements.setCellWidget(row, param_col, QCheckBox(param))
                self.tbl_elements.setItem(row, value_col, TWI(str(val)))
                row += 1

            # Make name cell span all other rows
            self.tbl_elements.setSpan(start_row, name_col, row-start_row, 1)


        self.tbl_elements.resizeColumnsToContents()
        self.tbl_elements.show()


    def add_row_clicked(self):
        '''Adds new row to column, could be expanded to add a preset number of rows'''
        self.tbl_elements.insertRow(self.tbl_elements.rowCount())
        self.tbl_elements.show()

    def run_process_clicked(self):
        a = np.pi
        logger.info(f'Running main process. Pi = {round(a, 3)} . more stuff')


    def save_config_clicked(self):
        '''Save table to dictionary'''
        # self.tbl_elements = QTableWidget()

        # Convert pyqt table to numpy array
        data = []
        for r in range(self.tbl_elements.rowCount()):
            row = []
            for c in range(self.tbl_elements.columnCount()):
                cell_item = self.tbl_elements.item(r, c)
                if cell_item is not None:
                    row.append(cell_item.text())
                else:
                    row.append(None)

            data.append(row)

        arr = np.array(data)

        # Parse numpy array to dictionaries
        print(arr)


class LinkElementTableItem(TWI):
    pass




if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    app.exec()