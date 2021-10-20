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

    # identify target files
    # target filenames are somewhat changing, so we just look for specific acronyms
    targets = [f for f in os.listdir(config.TARGETS_PATH) if os.path.isfile(os.path.join(config.TARGETS_PATH, f)) and f.endswith('.csv')]
    CEA_TARGET = [f for f in targets if 'CEA' in f]
    CEA_TARGET = CEA_TARGET[0] if len(CEA_TARGET) > 0 else None
    CTA_TARGET = [f for f in targets if 'CTA' in f]
    CTA_TARGET = CTA_TARGET[0] if len(CTA_TARGET) > 0 else None
    CPA_TARGET = [f for f in targets if 'CPA' in f]
    CPA_TARGET = CPA_TARGET[0] if len(CPA_TARGET) > 0 else None

    # get a mapping from a table to its ID
    tableToId = db.getTableToId()

    # copy CTA targets to db
    util_log.info('Importing CTA')
    if CTA_TARGET:
        path = os.path.join(config.TARGETS_PATH, CTA_TARGET)
        parseFile(tableToId, path, 'addCTA')
        util_log.info('   ... done')
    else:
        util_log.info('   ... skipped')

    # copy CEA targets to db
    util_log.info('Importing CEA')
    if CEA_TARGET:
        path = os.path.join(config.TARGETS_PATH, CEA_TARGET)
        parseFile(tableToId, path, 'addCEA')
        util_log.info('   ... done')
    else:
        util_log.info('   ... skipped')

    # copy CPA targets to db
    util_log.info('Importing CPA')
    if CPA_TARGET:
        path = os.path.join(config.TARGETS_PATH, CPA_TARGET)
        parseFile(tableToId, path, 'addCPA')
        util_log.info('   ... done')
    else:
        util_log.info('   ... skipped')


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
