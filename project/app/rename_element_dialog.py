#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: rename_element_dialog.py
project: Link-Budget-Toolbox
date: 29/05/2021
author: lmaio
"""


from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QDialog
from project.app.custom_objects import showdialog
from loguru import logger


rename_form_class = uic.loadUiType('ui/rename_element.ui')[0]

class RenameElementDialog(QDialog, rename_form_class):
    def __init__(self, current_name, existing_names, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.current_name = current_name
        self.existing_names = existing_names

        self.txt_name.setText(current_name)
        self.txt_name.setFocus()

    def accept(self) -> None:
        '''Check that required fields are filled before continuing'''
        conditions_unmet = 1

        # Check Name
        name = self.txt_name.text()
        if len(name) == 0:
            showdialog(['The new element must have a name'])
        elif name.lower() in self.existing_names:
            showdialog(['This element name already exists'])
        else:
            conditions_unmet -= 1

        if conditions_unmet == 0:
            super().accept()