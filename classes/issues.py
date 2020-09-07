#!/usr/bin/env python
# -*- coding: utf-8 -*.

u"""
Einlesen der Issues aus einer Excel-Datei

TODO: Überschriften Case-Insensitive
"""

import os, sys
import exceptions
import copy
import string
import xlrd

from salesforce_connect import SalesforceConnect
from simple_salesforce.exceptions import SalesforceGeneralError, SalesforceResourceNotFound

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'exceptions')))

class Issues(object):

    _app = (None,)*1

    workbook, sheets, sheet, tour_date, sfc = (None,)*5
    row_object = (None,)*1
    issue_object_template = { u'id': None, u'data': { u'AD_Issue__c': None, 
            u'BT_Issue__c': None, u'SW_Issue__c': None, u'Status__c': None }}

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

        attributes = [attribute for attribute in dir(self._app.salesforce)]

        cols = self.sheet.ncols
        for row_idx in range(1, self.sheet.nrows):
            row = self.getRowObject(self.sheet.row(row_idx))
            self._app.logger.debug('Row: {} - Id: {}, Data: {}' . \
                    format(row_idx, row['id'], row['data']))
            try:
                self._app.salesforce.Shopper_Inspection__c.update(row['id'], row['data'])
            except SalesforceResourceNotFound as msg:
                print(msg)
                pass
            except SalesforceGeneralError as msg:
                print("row = {}".format(row))
                sys.exit(msg)

            if not self._app.options.quiet:
                self._app.printProgressBar(row_idx, self.sheet.nrows, length=100)



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
                data[u"AD_Issue__c"] = cell_obj.value
            elif caption.lower().startswith('bt'):
                data[u"BT_Issue__c"] = cell_obj.value
            elif caption.lower().startswith('sw'):
                data[u"SW_Issue__c"] = cell_obj.value
            elif caption.lower().startswith('date') and cell_obj.value != '':
                data[u"SW_Issue_Solved_Date__c"] = cell_obj.value
            elif caption.lower().startswith('status'):
                data[u"Status__c"] = cell_obj.value

        row_object[u'data'] = data
        return row_object


if __name__ == '__main__':
    sys.exit("This module is not for execution...")
