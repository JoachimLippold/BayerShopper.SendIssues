#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Upload der Issues nach Salesforce
"""

from __future__ import print_function

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.join(sys.path[0], 'classes'))

import logging
import json

from optparse import OptionParser
from ConfigParser import SafeConfigParser

from simple_salesforce import Salesforce, SalesforceLogin, SalesforceAuthenticationFailed
import requests

class App(object):
    u"""Hauptklasse der Applikation. Hier werden die grundlegenden Applikationsglobalen Variablen initialisiert.
    """
    APPNAME = os.path.splitext(os.path.abspath(sys.argv[0]))[0]

    """ private """
    _instance, _session, _session_id, _sf_instance, _session_id, _sf_instance = (None,)*6

    """ public """
    config, logger, options, args, session, salesforce = (None,)*6

    def __init__(self):
        self.initConfig()
        self.initOptionParser()
        self.initLogging()
        self.initSalesforce()


    def initConfig(self):
        u"""
            Initialize configuration parser
        """
        self.config = SafeConfigParser()
        self.config.readfp(open(self.APPNAME + '.cfg'))


    def initLogging(self):
        u"""
            Initialize logging
        """
        loggingLevels = { logging.NOTSET: "NOTSET", logging.DEBUG: "DEBUG", logging.INFO: "INFO", \
                logging.WARNING: "WARNING", logging.ERROR: "ERROR", logging.CRITICAL: "CRITICAL" }
        try:
            loggingLevel = next(key for key, value in loggingLevels.items() if value == self.options.verbose)
        except (StopIteration,):
            loggingLevel = logging.NOTSET

        logging.basicConfig(filename=self.options.logging, format=self.config.get('logging', 'formatstring'), filemode='a')
        self.logger = logging.getLogger(self.APPNAME + ".logger")
        self.logger.setLevel(loggingLevel)
        self.logger.debug("options = {:s}" .  format(str(self.options)))


    def initOptionParser(self):
        u"""
            Initialize option parser
        """
        USAGE = "usage: %prog [options]"
        DESCRIPTION = """Wrapper zum Abgleich des Bayer-Datenbestandes mit dem Sit&Watch-Datenbestand"""
        VERSION = "1.0"

        parser = OptionParser(usage=USAGE, version=VERSION, description=DESCRIPTION)
        parser.add_option("-v", "--verbose", dest="verbose", default="ERROR", 
                help="Loglevel: [DEBUG, INFO, WARNING, ERROR, CRITICAL]")
        parser.add_option("-l", "--logging", dest="logging", default=self.APPNAME + ".log",
                help="Logfile")
        (self.options, self.args) = parser.parse_args()


    def initSalesforce(self):
        u"""
            Initialize Salesforce connection
        """
        self.session = requests.Session()
        try:
            self._session_id, self._sf_instance = SalesforceLogin(username=self.config.get('salesforce', 'soapUsername'), \
                    password=self.config.get('salesforce', 'soapPassword'),
                    sf_version=self.config.get('salesforce', 'soapVersion'),
                    sandbox=(self.config.get('salesforce', 'soapSandbox') == 'True'))
        except SalesforceAuthenticationFailed as e:
            self.logger.critical("login to salesforce failed: {:s}" . format(e.message))
            print("Login to salesforce failed: {:s}" . format(e.message))
            exit()

        self.salesforce = Salesforce(instance=self._sf_instance, session_id=self._session_id, session=self.session)


    def __new__(self, *args, **kwargs):
        u"""
            Run app as a singleton... (bad style, I know...)
        """
        if not self._instance:
            self._instance = super(App, self).__new__(self, *args, **kwargs)

        return self._instance



if __name__ == '__main__':
    app = App()
    app.logger.debug("object '{:s}' initialized..." . format(type(app).__name__))

#    data = {
#        'SW_Issue__c': '21.03.2018: dies ist ein kleiner Test'
#    }
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DApaIAG', data)
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEcIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6mIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBeIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFAIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBYIA4', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Stecker nicht eingesteckt','SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Stecker nicht eingesteckt, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEAIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Stecker nicht eingesteckt, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEGIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Stecker nicht eingesteckt, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBENIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Stecker nicht eingesteckt, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6yIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5mIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6HIAW', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5cIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB7CIAW', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBCdIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Stecker nicht eingesteckt'})
#    "app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEyIAO', {'BT_Issue__c': 'KW 09/2018: Schaufensterdisplay funktioniert nicht, Stecker nicht angeschlossen; Freiwahlregal funktioniert nicht, Stecker nicht eingesteckt'})"
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6UIAW', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6NIAW', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB7fIAG', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8hIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8gIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBxIAO', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDMIA4', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Stecker nicht eingesteckt','SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9uIAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBzIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9vIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBByIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB79IAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBCjIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB76IAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBnIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht','SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5eIAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Sprechblase abgebrochen'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDiIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6tIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8WIAW', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDzIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9eIAG', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBjIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBLIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6nIAG', {'AD_Issue__c': 'KW 09/2018: Dekoration verweigert'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBA3IAO', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9qIAG', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFnIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDVIA4', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB7uIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDDIA4', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig','SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBApIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDjIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5uIAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBA9IAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDTIA4', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB68IAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBAtIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFMIA4', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBC5IAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFmIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt','SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBAPIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5sIAG', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBAEIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB83IAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEkIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB7IIAW', {'BT_Issue__c': 'KW 09/2018: Schaufensterdisplay funktioniert nicht, Stecker nicht angeschlossen'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB7jIAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBHIA4', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5yIAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8iIAG', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBElIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBGIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDHIA4', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBE3IAO', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBAgIAO', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9DIAW', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6FIAW', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt','SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFLIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBE4IAO', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB97IAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB7dIAG', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDkIAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Zeitschaltuhr verbaut, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBC2IAO', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9mIAG', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBPIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Zeitschaltuhr verbaut, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9gIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Zeitschaltuhr verbaut, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEmIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFaIAO', {'AD_Issue__c': 'KW 09/2018: vom Apotheker nicht vorraetig'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBF4IAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEeIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFRIA4', {'BT_Issue__c': 'KW 09/2018: Schaufensterdisplay funktioniert nicht, Zeitschaltuhr verbaut'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9NIAW', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Zeitschaltuhr verbaut, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDmIAO', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEjIAO', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBB9IAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Zeitschaltuhr verbaut, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8JIAW', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDYIA4', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8oIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6VIAW', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Zeitschaltuhr verbaut, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBABIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBD9IAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB7mIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFFIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBBVIA4', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5pIAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBAAIA4', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBArIAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager','BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDIIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8IIAW', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager','BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBCKIA4', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Sprechblase abgebrochen, Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBB0IAO', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9oIAG', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6pIAG', {'AD_Issue__c': 'KW 09/2018: Originalpackungen verweigert'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5bIAG', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBCpIAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBB1IAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBB2IAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8GIAW', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB65IAG', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8ZIAW', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9HIAW', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEKIA4', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8aIAG', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBAZIA4', {'AD_Issue__c': 'KW 09/2018: Originalpackungen verweigert'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEfIAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBCnIAO', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEFIA4', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBC7IAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBCiIAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5qIAG', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBEMIA4', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFPIA4', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBB7IAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB7FIAW', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Leuchte am Trafo blinkt','SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBD4IAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBAeIAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBD6IAO', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6rIAG', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB8KIAW', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBD0IAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFoIAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9wIAG', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBA2IAO', {'AD_Issue__c': 'KW 09/2018: keine Dekoration - Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6CIAW', {'AD_Issue__c': 'KW 09/2018: Originalpackungen verweigert'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBDAIA4', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Monitor defekt, Korpus defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6DIAW', {'SW_Issue__c': 'KW 09/2018: HV-Display funktioniert nicht, Sprechblase defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFrIAO', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DBFEIA4', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB5rIAG', {'BT_Issue__c': 'KW 09/2018: Freiwahlregal funktioniert nicht, Bayer-Kreuz defekt, Leuchte am Trafo blinkt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB99IAG', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB6iIAG', {'AD_Issue__c': 'KW 09/2018: Originalpackungen verweigert'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DB9AIAW', {'AD_Issue__c': 'KW 09/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAlFIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAh0IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAjiIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAnYIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAj3IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Freiwahlregal: Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAlkIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAk1IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhGIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAlzIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Freiwahlregal: Bayer-Kreuz defekt, Schienen defekt, Stecker nicht eingesteckt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhJIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAgXIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAjqIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhAIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAobIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAgDIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhVIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhbIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAfEIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAnxIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Freiwahlregal: Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAkPIAW', {'AD_Issue__c': 'KW 02/2018: Dekoration verweigert'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAj9IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Freiwahlregal: Bayer-Kreuz defekt, Schienen defekt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DApQIAW', {'AD_Issue__c': 'KW 02/2018: Dekoration verweigert'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAj0IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAkcIAG', {'AD_Issue__c': 'KW 02/2018: Dekoration verweigert'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAl3IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAmtIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAeXIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhHIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Freiwahlregal: keine Zeitschaltuhr verbaut'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAkOIAW', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAkMIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAnOIAW', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAebIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAiJIAW', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhtIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAkxIAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAj7IAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAivIAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAiuIAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhMIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhaIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAj6IAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAmoIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAnrIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAnwIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAeEIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAk3IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAjLIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAf1IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhjIAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAefIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAmQIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAk5IAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAiZIAW', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAetIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Freiwahlregal: keine Zeitschaltuhr verbaut','SW_Issue__c': 'KW 02/2018: HV-Display: keine Funktion, nicht an Strom angeschlossen'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAjuIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAlhIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay unerwuenscht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAgJIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay unerwuenscht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAelIAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAmGIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay unerwuenscht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAnVIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay unerwuenscht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAhLIAW', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAn1IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay unerwuenscht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAeCIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay unerwuenscht'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAfYIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAmCIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAmTIAW', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAm2IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAfqIAG', {'AD_Issue__c': 'KW 02/2018: keine Dekoration Vertrag gekuendigt'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAo4IAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAeeIAG', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay im Lager'})
#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DAfMIAW', {'AD_Issue__c': 'KW 02/2018: HV-Display im Lager','BT_Issue__c': 'KW 02/2018: Schaufensterdisplay im Lager'})

    records = app.salesforce.query_all(u"""
        SELECT Id, Shopper_Contract__c, Name, SW_Issue__c, BT_Issue__c, AD_Issue__c, CreatedDate, Status__c
            FROM Shopper_Inspection__c 
            WHERE Id IN (
                'a3wD0000001DBEcIAO', 'a3wD0000001DB6mIAG', 'a3wD0000001DBBeIAO', 'a3wD0000001DBFAIA4',
                'a3wD0000001DB6YIAW', 'a3wD0000001DBDuIAO', 'a3wD0000001DB8UIAW', 'a3wD0000001DB6EIAW',
                'a3wD0000001DBBYIA4', 'a3wD0000001DBEAIA4', 'a3wD0000001DBEGIA4', 'a3wD0000001DBENIA4',
                'a3wD0000001DB6yIAG', 'a3wD0000001DB5mIAG', 'a3wD0000001DB6HIAW', 'a3wD0000001DB5cIAG',
                'a3wD0000001DB7CIAW', 'a3wD0000001DBCdIAO', 'a3wD0000001DBEyIAO', 'a3wD0000001DB6UIAW',
                'a3wD0000001DB6NIAW', 'a3wD0000001DB7fIAG', 'a3wD0000001DB8hIAG', 'a3wD0000001DB8gIAG',
                'a3wD0000001DBBxIAO', 'a3wD0000001DBDMIA4', 'a3wD0000001DB9uIAG', 'a3wD0000001DBBzIAO',
                'a3wD0000001DB9vIAG', 'a3wD0000001DBDSIA4', 'a3wD0000001DBByIAO', 'a3wD0000001DB79IAG',
                'a3wD0000001DBCjIAO', 'a3wD0000001DB76IAG', 'a3wD0000001DBBnIAO', 'a3wD0000001DB5eIAG',
                'a3wD0000001DBDiIAO', 'a3wD0000001DB6tIAG', 'a3wD0000001DB8WIAW', 'a3wD0000001DBDzIAO',
                'a3wD0000001DB9eIAG', 'a3wD0000001DBBjIAO', 'a3wD0000001DBBLIA4', 'a3wD0000001DB6nIAG',
                'a3wD0000001DBA3IAO', 'a3wD0000001DB9qIAG', 'a3wD0000001DBFnIAO', 'a3wD0000001DBDVIA4',
                'a3wD0000001DB7uIAG', 'a3wD0000001DBDDIA4', 'a3wD0000001DBApIAO', 'a3wD0000001DBDjIAO',
                'a3wD0000001DB5uIAG', 'a3wD0000001DBA9IAO', 'a3wD0000001DBDTIA4', 'a3wD0000001DB68IAG',
                'a3wD0000001DBAtIAO', 'a3wD0000001DBFMIA4', 'a3wD0000001DBC5IAO', 'a3wD0000001DBFmIAO',
                'a3wD0000001DBAPIA4', 'a3wD0000001DB5sIAG', 'a3wD0000001DBAEIA4', 'a3wD0000001DB83IAG',
                'a3wD0000001DBEkIAO', 'a3wD0000001DB7IIAW', 'a3wD0000001DB7jIAG', 'a3wD0000001DBBHIA4',
                'a3wD0000001DB5yIAG', 'a3wD0000001DB8iIAG', 'a3wD0000001DBElIAO', 'a3wD0000001DBBGIA4',
                'a3wD0000001DBDHIA4', 'a3wD0000001DBE3IAO', 'a3wD0000001DBAgIAO', 'a3wD0000001DB9DIAW',
                'a3wD0000001DB6FIAW', 'a3wD0000001DBFLIA4', 'a3wD0000001DBE4IAO', 'a3wD0000001DB97IAG',
                'a3wD0000001DB7dIAG', 'a3wD0000001DBDkIAO', 'a3wD0000001DBC2IAO', 'a3wD0000001DB9mIAG',
                'a3wD0000001DBBPIA4', 'a3wD0000001DB9gIAG', 'a3wD0000001DBEmIAO', 'a3wD0000001DBFaIAO',
                'a3wD0000001DBF4IAO', 'a3wD0000001DBEeIAO', 'a3wD0000001DBFRIA4', 'a3wD0000001DB9NIAW',
                'a3wD0000001DBDmIAO', 'a3wD0000001DBEjIAO', 'a3wD0000001DBB9IAO', 'a3wD0000001DB8JIAW',
                'a3wD0000001DBDYIA4', 'a3wD0000001DB8oIAG', 'a3wD0000001DB6VIAW', 'a3wD0000001DBABIA4',
                'a3wD0000001DBD9IAO', 'a3wD0000001DB7mIAG', 'a3wD0000001DBFFIA4', 'a3wD0000001DBBVIA4',
                'a3wD0000001DB5pIAG', 'a3wD0000001DBAAIA4', 'a3wD0000001DBArIAO', 'a3wD0000001DBDIIA4',
                'a3wD0000001DB8IIAW', 'a3wD0000001DBCKIA4', 'a3wD0000001DBB0IAO', 'a3wD0000001DB9oIAG',
                'a3wD0000001DB6pIAG', 'a3wD0000001DB5bIAG', 'a3wD0000001DBCpIAO', 'a3wD0000001DBB1IAO',
                'a3wD0000001DBB2IAO', 'a3wD0000001DB8GIAW', 'a3wD0000001DB65IAG', 'a3wD0000001DB8ZIAW',
                'a3wD0000001DB9HIAW', 'a3wD0000001DBEKIA4', 'a3wD0000001DB8aIAG', 'a3wD0000001DBAZIA4',
                'a3wD0000001DBEfIAO', 'a3wD0000001DBCnIAO', 'a3wD0000001DBEFIA4', 'a3wD0000001DBC7IAO',
                'a3wD0000001DBCiIAO', 'a3wD0000001DB5qIAG', 'a3wD0000001DBEMIA4', 'a3wD0000001DBFPIA4',
                'a3wD0000001DBB7IAO', 'a3wD0000001DB7FIAW', 'a3wD0000001DBD4IAO', 'a3wD0000001DBAeIAO',
                'a3wD0000001DBD6IAO', 'a3wD0000001DB6rIAG', 'a3wD0000001DB8KIAW', 'a3wD0000001DBD0IAO',
                'a3wD0000001DBFoIAO', 'a3wD0000001DB9wIAG', 'a3wD0000001DBA2IAO', 'a3wD0000001DB6CIAW',
                'a3wD0000001DBDAIA4', 'a3wD0000001DB6DIAW', 'a3wD0000001DBFrIAO', 'a3wD0000001DBFEIA4',
                'a3wD0000001DB5rIAG', 'a3wD0000001DB99IAG', 'a3wD0000001DB6iIAG', 'a3wD0000001DB9AIAW',
                'a3wD0000001DAlFIAW', 'a3wD0000001DAh0IAG', 'a3wD0000001DAjiIAG', 'a3wD0000001DAnYIAW',
                'a3wD0000001DAj3IAG', 'a3wD0000001DAlkIAG', 'a3wD0000001DAk1IAG', 'a3wD0000001DAhGIAW',
                'a3wD0000001DAlzIAG', 'a3wD0000001DAhJIAW', 'a3wD0000001DAgXIAW', 'a3wD0000001DAjqIAG',
                'a3wD0000001DAhAIAW', 'a3wD0000001DAobIAG', 'a3wD0000001DAgDIAW', 'a3wD0000001DAhVIAW',
                'a3wD0000001DAhbIAG', 'a3wD0000001DAfEIAW', 'a3wD0000001DAnxIAG', 'a3wD0000001DAkPIAW',
                'a3wD0000001DAj9IAG', 'a3wD0000001DApQIAW', 'a3wD0000001DAj0IAG', 'a3wD0000001DAkcIAG',
                'a3wD0000001DAl3IAG', 'a3wD0000001DAmtIAG', 'a3wD0000001DAeXIAW', 'a3wD0000001DAhHIAW',
                'a3wD0000001DAkOIAW', 'a3wD0000001DAkMIAW', 'a3wD0000001DAnOIAW', 'a3wD0000001DAebIAG',
                'a3wD0000001DAiJIAW', 'a3wD0000001DAhtIAG', 'a3wD0000001DAkxIAG', 'a3wD0000001DAj7IAG',
                'a3wD0000001DAivIAG', 'a3wD0000001DAiuIAG', 'a3wD0000001DAhMIAW', 'a3wD0000001DAhaIAG',
                'a3wD0000001DAj6IAG', 'a3wD0000001DAmoIAG', 'a3wD0000001DAnrIAG', 'a3wD0000001DAnwIAG',
                'a3wD0000001DAeEIAW', 'a3wD0000001DAk3IAG', 'a3wD0000001DAjLIAW', 'a3wD0000001DAf1IAG',
                'a3wD0000001DAhjIAG', 'a3wD0000001DAefIAG', 'a3wD0000001DAmQIAW', 'a3wD0000001DAk5IAG',
                'a3wD0000001DAiZIAW', 'a3wD0000001DAetIAG', 'a3wD0000001DAjuIAG', 'a3wD0000001DAlhIAG',
                'a3wD0000001DAgJIAW', 'a3wD0000001DAelIAG', 'a3wD0000001DAmGIAW', 'a3wD0000001DAnVIAW',
                'a3wD0000001DAhLIAW', 'a3wD0000001DAn1IAG', 'a3wD0000001DAeCIAW', 'a3wD0000001DAfYIAW',
                'a3wD0000001DAmCIAW', 'a3wD0000001DAmTIAW', 'a3wD0000001DAm2IAG', 'a3wD0000001DAfqIAG',
                'a3wD0000001DAo4IAG', 'a3wD0000001DAeeIAG', 'a3wD0000001DAfMIAW')""")

    for record in records['records']:
        print(u"-" * 21 + "+" + "-"*80)
        for key, value in record.items():
            if key <> 'attributes':
                print(u"{:<20} | {}" . format(key, value))
