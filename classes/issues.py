#!/usr/bin/env python
# -*- coding: utf-8 -*.

u"""
Einlesen der Issues aus einer Excel-Datei

TODO: Überschriften Case-Insensitive
"""

from __future__ import print_function

import os, sys
import exceptions
import copy
import string
import xlrd

from salesforce_connect import SalesforceConnect

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'exceptions')))

class Issues(object):

    _app = (None,)*1

    workbook, sheets, sheet, tour_date, sfc = (None,)*5
    row_object = (None,)*1
    issue_object_template = { u'id': None, u'data': { u'AD_Issue__c': None, u'BT_Issue__c': None, u'SW_Issue__c': None }}

    def __init__(self, app, issue_file, tour_date):
        if not hasattr(app, 'salesforce'):
            app.critical('Object \'app\' has no attribute \'salesforce\'')
            raise AttributeError('Object \'app\' has no attribute \'salesforce\'')

        self._app = app
        self.tour_date = tour_date

        self.sfc = SalesforceConnect(app, tour_date)

        self.workbook = xlrd.open_workbook(issue_file, encoding_override="utf8")
        self.sheets = self.workbook.sheet_names()
        self.sheet = self.workbook.sheet_by_name(self.sheets[0])

        cols = self.sheet.ncols
        for row_idx in range(0, self.sheet.nrows):
            self._app.logger.debug('Row: {0:3d} - {1:s}' . format(row_idx, self.getRowObject(self.sheet.row(row_idx))))
            if not self._app.options.quiet:
                self._app.printProgressBar(row_idx, self.sheet.nrows)



    def getRowObject(self, row):
        row_object = copy.deepcopy(self.issue_object_template)
        data = {}
        captions = self.sheet.row(0)
        inspectionIds = self.sfc.getInspectionIds()
        for idx, cell_obj in enumerate(row):
            caption = captions[idx].value
            if idx == 0:
                try:
                    id = inspectionIds[cell_obj.value]
                except KeyError:
                    id = cell_obj.value

                row_object[u'id'] = id
            elif caption.lower().startswith('ad'):
                data[u'AD_Issue__c'] = cell_obj.value
            elif caption.lower().startswith('bt'):
                data[u'BT_Issue__c'] = cell_obj.value
            elif caption.lower().startswith('sw'):
                data[u'SW_Issue__c'] = cell_obj.value

        row_object[u'data'] = data
        return row_object


if __name__ == '__main__':
    print("This module is not for execution...")
