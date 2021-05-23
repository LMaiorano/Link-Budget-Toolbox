#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: notification_dialog.py
project: Link-Budget-Toolbox
date: 23/05/2021
author: lmaio
"""

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