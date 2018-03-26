#!/usr/bin/env python

u"""
Einlesen der Issues aus einer Excel-Datei
"""

from __future__ import print_function

import os, sys
import exceptions

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'exceptions')))

class Issues(object):

    _app = (None,)*1

    def __init__(self, app):
        if not hasattr(app, 'salesforce'):
            raise AttributeError('Object \'app\' has no attribute \'salesforce\'')

        self._app = app
        print("Issues: sys.path == {}" . format(sys.path))


if __name__ == '__main__':
    print("This module is not for execution...")
