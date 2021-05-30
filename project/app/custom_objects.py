#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: custom_objects.py
project: Link-Budget-Toolbox
date: 29/05/2021
author: Luigi Maiorano
"""

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox


def showdialog(message: list, level='warning'):
    '''Popup dialog box to warn user of some sort of error or other information

    Parameters
    ----------
    message : list of str
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




class NotEmptyNumericValidator(QDoubleValidator):
    '''Custom Validator to ensure only numeric and non-empty values are entered

    This customizes the default behavior, such that if the line is left empty, the text
    is changed to an empty string and the state is returned as acceptable.

    The state change is necessary, to ensure that the editingFinished() signal is emitted. This
    triggers the slots in the mainwindow to update other fields (The editingFinished() signal
    is not emitted for Intermediate State)
    '''
    def validate(self, text, pos):
        #skip validation if negative number is being typed
        if text == '-':
            return QtGui.QValidator.Acceptable, text, pos

        # Otherwise, run standard validation for a float
        state, text, pos = super().validate(text, pos)

        # Modify possible Intermediate state to acceptable
        if (state == QtGui.QValidator.Intermediate) and \
                ('e' not in text): # allow entering scienfic notation
            text = ''
            state = QtGui.QValidator.Acceptable
        return state, text, pos


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

        Parameters
        ----------
        type : str, optional
            Whether the attribute is a 'parameter', or 'gain_loss'
        description: str, optional
            Description of the attribute to show as a tooltip
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

