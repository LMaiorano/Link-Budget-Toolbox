#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title: load_config.py
project: Link-Budget-Toolbox
date: 13/05/2021
author: lmaio
"""

from browser import document, window, console
import yaml
import json

def load_data():
    storage = window.sessionStorage

    data = storage.get("config")
    if data:
        return json.loads(data)
    else:
        storage["config"] = json.dumps({})
        return {}



def file_read(e):
    storage = window.sessionStorage
    def onload(e):

        try:
            # Print contents in textarea
            document['config-text'].value = e.target.result
        except KeyError as KE:
            console.log(f'Cannot show file contents, textarea "{KE}" does not exist')

        # save config to session storage
        data = yaml.safe_load(e.target.result)
        storage.setItem('config', data)


    file = document['file-loadconfig'].files[0]
    reader = window.FileReader.new()
    reader.readAsText(file)
    reader.bind('load', onload)


document['file-loadconfig'].bind('input', file_read)