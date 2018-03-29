#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Zugriff auf Salesforce
"""

from __future__ import print_function

import os, sys
import datetime

from simple_salesforce import Salesforce

class SalesforceConnect(object):

    SOQL_DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
    one_day = datetime.timedelta(days = 1)

    app, inspection_ids, inspection_date = (None,)*3

    def __init__(self, app, inspection_date):
        if not hasattr(app, 'salesforce'):
            raise AttributeError('Object \'app\' has no attribute \'salesforce\'')

        self.app = app
        self.inspection_date = inspection_date


    def getInspectionIds(self):
        tour_date = datetime.datetime.strptime(self.inspection_date, '%d.%m.%Y')
        from_date = tour_date - self.one_day
        to_date = tour_date + self.one_day

        query = u"""
            SELECT Shopper_Contract__c, Id FROM Shopper_Inspection__c 
                WHERE CreatedDate > {:1} AND CreatedDate < {:1}""" . format(
                    from_date.strftime(self.SOQL_DATEFORMAT), \
                    to_date.strftime(self.SOQL_DATEFORMAT))

        records = self.app.salesforce.query_all(query)
        results = {}
        for record in records['records']:
            inspection, contract = (None,)*2
            for key, value in record.items():
                if key == 'Id':
                   inspection = value
                if key == 'Shopper_Contract__c':
                   contract = value

            results[contract] = inspection

        return results
                

if __name__ == '__main__':
    print("This module is not for execution")
