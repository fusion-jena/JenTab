import csv
import os
import config
import db
import util_log


def run():
    """
    initialize all components and get ready to go

    * scan for available tables
    * parse target files
    * put everything into the database
    """

    # scan for available tables
    util_log.info('Scanning tables')
    tables = [f.replace('.csv', '') for f in os.listdir(config.TABLES_PATH) if os.path.isfile(os.path.join(config.TABLES_PATH, f)) and f.endswith('.csv')]
    db.addTables(tables)
    util_log.info('   ... done')

    # get a mapping from a table to its ID
    tableToId = db.getTableToId()

    # copy CTA targets to db
    util_log.info('Importing CTA')
    path = os.path.join(config.TARGETS_PATH, "CTA_Round{0}_Targets.csv".format(config.ROUND))
    if not os.path.exists(path):
        path = os.path.join(config.TARGETS_PATH, "CTA_Round{0}_targets.csv".format(config.ROUND))
    parseFile(tableToId, path, 'addCTA')
    util_log.info('   ... done')

    # copy CEA targets to db
    util_log.info('Importing CEA')
    path = os.path.join(config.TARGETS_PATH, "CEA_Round{0}_Targets.csv".format(config.ROUND))
    if not os.path.exists(path):
        path = os.path.join(config.TARGETS_PATH, "CEA_Round{0}_targets.csv".format(config.ROUND))
    parseFile(tableToId, path, 'addCEA')
    util_log.info('   ... done')

    # copy CPA targets to db
    util_log.info('Importing CPA')
    path = os.path.join(config.TARGETS_PATH, "CPA_Round{0}_Targets.csv".format(config.ROUND))
    if not os.path.exists(path):
        path = os.path.join(config.TARGETS_PATH, "CPA_Round{0}_targets.csv".format(config.ROUND))
    parseFile(tableToId, path, 'addCPA')
    util_log.info('   ... done')


def parseFile(tableToId, filePath, targetFkt):
    """parse the given file and insert the values using the provided function of db"""
    method = getattr(db, targetFkt)
    with open(filePath, "r", encoding="utf-8") as file:
        entries = []
        for i, line in enumerate(file):
            entry = line.replace('"', '').strip().split(',')
            entry[0] = tableToId[entry[0]]
            entries = entries + [entry]
            if(len(entries) > 1000):
                method(entries)
                entries = []
        method(entries)
