#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: app.py
project: Link-Budget-Toolbox
date: 13/05/2021
author: lmaio
"""

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem as TWI
from PyQt5.QtGui import QFont

from pathlib import Path
import sys
from loguru import logger
import yaml
import numpy as np

from project.process import main_process


mainwindow_form_class = uic.loadUiType('ui/main_window_nico.ui')[0]

class MainWindow(QMainWindow, mainwindow_form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.cfg_file = None
        self.cfg_data = None


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

        elements = self.cfg_data['elements']       # Select sub-dictionary of elements from config

        # Determine number of rows needed for table  rows are: name + gainloss + each parameter
        n_rows = sum([ (2 + len(elem['parameters'])) for elem in elements.values() ])

        self.tbl_elements.setColumnCount(2)
        self.tbl_elements.setRowCount(n_rows)

        self.tbl_elements.setHorizontalHeaderLabels(['Element', 'Value'])
        self.tbl_elements.verticalHeader().setVisible(False)

        element_font = QFont()
        element_font.setBold(True)

        row = 0
        for name, data in elements.items():
            title = TWI(name)
            title.setFont(element_font)
            self.tbl_elements.setItem(row, 0, title)
            row += 1

            self.tbl_elements.setItem(row, 0, TWI('Gain [dB]'))

            self.tbl_elements.setItem(row, 1, TWI(str(data['gain_loss'])))
            row +=1
            
            for param, val in data['parameters'].items():
                self.tbl_elements.setItem(row, 0, TWI(param))
                self.tbl_elements.setItem(row, 1, TWI(str(val)))
                row += 1

        self.tbl_elements.resizeColumnsToContents()
        self.tbl_elements.show()


    def add_row_clicked(self):
        '''Adds new row to column, could be expanded to add a preset number of rows'''
        self.tbl_elements.insertRow(self.tbl_elements.rowCount())
        self.tbl_elements.show()

    def run_process_clicked(self):
        a = np.pi
        logger.info(f'Running main process. Pi = {round(a, 3)} . more stuff')


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    app.exec()