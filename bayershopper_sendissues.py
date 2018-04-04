#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Upload der Issues nach Salesforce
"""

from __future__ import print_function

import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'classes')))

import datetime

import logging
import json

from optparse import OptionParser
from ConfigParser import SafeConfigParser

from simple_salesforce import Salesforce, SalesforceLogin, SalesforceAuthenticationFailed
import requests

from issues import Issues
from classes.salesforce_connect import SalesforceConnect

class App(object):
    u"""Hauptklasse der Applikation. Hier werden die grundlegenden Applikationsglobalen Variablen initialisiert.
    """
    APPNAME = os.path.splitext(os.path.abspath(sys.argv[0]))[0]

    """ private """
    _instance, _session, _session_id, _sf_instance, _session_id, _sf_instance = (None,)*6
    _loggingLevels = { logging.NOTSET: "NOTSET", logging.DEBUG: "DEBUG", logging.INFO: "INFO",
            logging.WARNING: "WARNING", logging.ERROR: "ERROR", logging.CRITICAL: "CRITICAL" }

    """ public """
    config, logger, options, args, session, salesforce = (None,)*6

    def __init__(self):
        self.initConfig()
        self.initOptionParser()
        self.initLogging()
        self.initSalesforce()
        self.checkArguments()


    def initConfig(self):
        u"""
            Konfiguration einlesen.

            Liest die Konfiguration aus einer Datei mit dem Name <SCRIPTNAME>.cfg, die sich im selben
            Verzeichnis wie das Skript.

            Die Konfigurationsdatei hat folgenden Aufbau:

            <pre>
                [salesforce]
                soapUsername = <SALESFORCE-BENUTZER>
                soapPassword = <SALESFORCE-PASSWORD>
                soapSecurityToken = <SALESFORCE-SECURITY-TOKEN>
                soapSandbox = False|True
                soapVersion = <VERSION> ; aktuell 38.0

                [logging]
                formatstring = %%(asctime)s - %%(filename)s - %%(funcName)s - %%(levelname)s - %%(message)s
            </pre>

            Der Abschnitt 'salesforce' enthält die Zugangsdaten zum Salesforce-Server von Bayer. Im Abschnitt
            [logging] wird das Format des Log-Strings definiert.
        """
        self.config = SafeConfigParser()
        self.config.readfp(open(self.APPNAME + '.cfg'))


    def initLogging(self):
        u"""
            Logging in eine Datei initialisieren.

            Log-Meldungen können mit self.logger.<LEVEL> in eine externe Datei geschrieben werden.
            Die Loglevel werden mit einem Parameter -v oder --verbose beim Aufruf des Scriptes
            angegeben. Default-Level ist 'ERROR'.

            Es stehen folgende Level in aufsteigender Sortierung zur Verfügung:
                * DEBUG
                * INFO
                * WARNING
                * ERROR
                * CRITICAL

            Ausgegeben werden dann nur Meldungen, die mindestens dem eingestellten Loglevel entsprechen.
            Wurde zum beispiel 'WARNING' gesetzt, werden nur Meldungen mit dem Level 'WARNING', 'ERROR'
            und 'CRITICAL' ausgegeben. 'DEBUG' und 'INFO' werden unterdrückt.

            Der Name der Datei ist Standardmäßig der Skript-Name mit der Endung .log
        """
        try:
            loggingLevel = next(key for key, value in self._loggingLevels.items() if value == self.options.verbose)
        except (StopIteration,):
            loggingLevel = logging.NOTSET

        logging.basicConfig(filename=self.options.logging, format=self.config.get('logging', 'formatstring'), filemode='a')
        self.logger = logging.getLogger(self.APPNAME + ".logger")
        self.logger.setLevel(loggingLevel)
        self.logger.debug("options = {:s}" .  format(str(self.options)))


    def initOptionParser(self):
        u"""
            Option-Parser initialiseren.

            Das Skript kann mit diversen Optionen aufgerufen werden. Diese werden vom OptionParser
            verarbeitet. Aktuell sind folgende Optionen möglich:

                -v, --verbose <LOGLEVEL>
                    Loglevel: [DEBUG, INFO, WARNING, ERROR, CRITICAL]

                -l, --logging <LOGFILE>
                    Name des Logfiles. Default ist <SCRIPTNAME>.log

                -h, --help
                    Hilfetext
        """
        USAGE = "usage: %prog [options] /path/to/excelfile tourdate"
        DESCRIPTION = u"""Kommandozeilentool zum Upload der Issues zum Salesforce-Server von Bayer.
Das Skript erwartet als Parameter den Pfad zur Excel-Datei und das Datum zu dem die Inspections markiert
wurden. Die Excel-Datei muss dabei mindestens 4 Spalten enthalten. Die Spalte "A" enthält entweder
die Salesforce-Id der Apotheke oder die Salesforce-Id der Inspection. Das Skript ermittelt selbstständig,
welche ID angegeben wurde. Die Spalten "B" bis "D" enthalten die Issue-Texte. Die Reihenfolge der Spalten
spielt keine Rolle, jedoch müssen die Spaltennamen mit "AD", "SW" oder "BT" beginnen.
        """
        VERSION = "1.0"

        parser = OptionParser(usage=USAGE, version=VERSION, description=DESCRIPTION)
        parser.add_option("-v", "--verbose", dest="verbose", default="ERROR", 
                choices=[value for key, value in self._loggingLevels.items()],
                help="Loglevel: [" + ', '.join([value for key, value in self._loggingLevels.items()]) + ")")
        parser.add_option("-l", "--logging", dest="logging", default=self.APPNAME + ".log",
                help="Name and path of logfile")
        parser.add_option("-q", "--quiet", dest="quiet", action="store_true", help="don't show progress")

        (self.options, self.args) = parser.parse_args()


    def checkArguments(self):
        if len(self.args) < 2:
            self.logger.critical('Two few arguments found.')
            sys.exit('Zu wenig Argumente.')

        if not os.path.isfile(self.args[0]):
            self.logger.critical('File not found: {:s}' . format(self.args[0]))
            sys.exit('Datei \'{:s}\' nicht gefunden' . format(self.args[0]))

        try:
            date = datetime.datetime.strptime(self.args[1], '%d.%m.%Y')
        except ValueError, msg:
            self.logger.critical('{:s} is not a valid date' . format(self.args[1]))
            sys.exit('\'{:s}\' ist kein gültiges Datum' . format(self.args[1]))


    def initSalesforce(self):
        u"""
            Initialisiert die Salesforce-Verbindung

            Öffnet eine Verbindung zum Salesforce-Server und etabliert eine entsprechende Session.
            Zugriffe auf Salesforce können dann mit app.salesforce.<OBJECT>.<METHOD>() durchgeführt werden.

            Beispiel:
                app.salesforce.Shopper_Inspection__c.update(<INSPECTION_ID>, { <KEY>: <VALUE>[, <KEY>: <VALUE>[, ...]] })
                führt ein Update auf einen Datensatz der Tabelle Shopper_Inspection__c durch.
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
            Hauptklasse als Singleton instanziieren. Schlechter Stil, ich weiß aber nichts besseres... :-)
        """
        if not self._instance:
            self._instance = super(App, self).__new__(self, *args, **kwargs)

        return self._instance


    def printProgressBar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 70, fill = '#'):
        u"""
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required : current iteration (Int)
            total       - Required : total iterations (Int)
            prefix      - Optional : prefix string (Str)
            suffix      - Optional : suffix string (Str)
            decimals    - Optional : positive number of decimals in percent complete (Int)
            length      - Optional : character length of bar (Int)
            fill        - Optional : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}") . format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        sys.stdout.write('\r{:s} [{:s}] {:s}% {:s}' . format(prefix, bar, percent, suffix))
        sys.stdout.flush()
        if iteration == total:
            sys.stdout.write("\n")



if __name__ == '__main__':
    app = App()
    app.logger.debug("options: {0}, args: {1}" . format(app.options, app.args))

#    sfc = SalesforceConnect(app)
#    results = sfc.getInspectionIds("16.02.2018")
#    print("sfc = {}" . format(results))
    issues = Issues(app, app.args[0], app.args[1])

#    app.salesforce.Shopper_Inspection__c.update('a3wD0000001DApaIAG', data)

#    query = u"""
#        SELECT Id, Shopper_Contract__c, Name, SW_Issue__c, BT_Issue__c, AD_Issue__c, CreatedDate, Status__c
#            FROM Shopper_Inspection__c 
#            WHERE 
#            CreatedDate > {:s} AND CreatedDate < {:s}""" \
#            . format(from_date.strftime(SalesforceConnect.SOQL_DATEFORMAT), 
#                to_date.strftime(SalesforceConnect.SOQL_DATEFORMAT))
#
##                Id IN (
##                    'a3wD0000001DBEcIAO', 'a3wD0000001DB6mIAG', 'a3wD0000001DBBeIAO', 'a3wD0000001DBFAIA4',
##                    'a3wD0000001DAo4IAG', 'a3wD0000001DAeeIAG', 'a3wD0000001DAfMIAW')  AND
##
#    print("query = {:s}" . format(query))
#    records = app.salesforce.query_all(query)
#
#    for record in records['records']:
#        print(u"-" * 21 + "+" + "-"*80)
#        for key, value in record.items():
#            if key <> 'attributes':
#                print(u"{:<20} | {}" . format(key, value))
