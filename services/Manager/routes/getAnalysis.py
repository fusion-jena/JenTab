import config
import db
import csv
import glob
import json
import re
import os
from inc.util import getWikiID


def find(arr, fkt):
    """find a specific element in the given array"""
    for el in arr:
        if fkt(el):
            return el


def evalTargets(type, solKeyFkt, solTargetFkt, submKeyFkt, trgtKeyFkt):

    # basic input check
    if type not in ['cea', 'cpa', 'cta']:
        raise Exception('Invalid type {}'.format(type))

    # parse the solution file
    lookup = {}
    with open(os.path.join(config.BASE_PATH, 'solution', type + '.csv'), mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        solutions = None
        unsolvedTables = set()
        for row in csv_reader:

            # make sure we have an entry
            if not row['Filename'] in lookup:
                lookup[row['Filename']] = {}

            # add the solution in this row
            cand = [getWikiID(item) for item in solTargetFkt(row).split(',')]
            lookup[row['Filename']][solKeyFkt(row)] = cand

    # reduce lookup to actually requested targets
    for table, tableLookup in lookup.items():

        # table to id
        table_id = db.getIdForTable(table)

        # get the actual target list
        targets = {
            'cea': db.getCEA,
            'cta': db.getCTA,
            'cpa': db.getCPA,
        }[type](table_id)

        # only keep targets that are requested
        filteredLookup = {}
        for row in targets:
            key = trgtKeyFkt(row)
            filteredLookup[key] = tableLookup[key]
        lookup[table] = filteredLookup

    # read intermediate solutions
    allStats = []
    for filename in glob.glob(os.path.join(config.ANALYSIS_PATH, '*.json')):
        with open(filename, mode='r') as json_file:

            # get table id
            table = os.path.basename(filename).replace('.json', '')

            # skip for tables with no mappings for this type
            if table not in lookup:
                continue

            # shortcuts
            tableSolution = lookup[table]
            entryStats = {}

            # each line contains data for a checkpoint in json format
            for line in json_file:
                submission = json.loads(line)

                # process each entry in the respective task
                for entry in submission[type]:
                    # make sure we have a stats entry for this kind
                    if entry['label'] not in entryStats:
                        entryStats[entry['label']] = {
                            'missing': 0,  # no candidates at all
                            'correct': 0,  # correct entries (one of the candidates matches)
                            'incorrect': 0,  # incorrect entries (none of the candidate matches)
                            'total': 0,  # targets overall
                        }

                    # build lookup for submission
                    submLookup = {}
                    for el in entry['state']:
                        submLookup[submKeyFkt(el)] = el['cand']

                    # check for all targets
                    for key, el in tableSolution.items():
                        entryStats[entry['label']]['total'] += 1
                        if (key not in submLookup) or not submLookup[key]:
                            entryStats[entry['label']]['missing'] += 1
                        elif any([(c in submLookup[key]) for c in el]):
                            entryStats[entry['label']]['correct'] += 1
                        else:
                            entryStats[entry['label']]['incorrect'] += 1

            # add to the global results
            allStats.append({
                'table': table,
                'stats': entryStats,
            })

    # aggregate stats over all tables
    aggStats = {}
    for table in allStats:
        for k, v in table['stats'].items():
            if k not in aggStats:
                aggStats[k] = {
                    'missing': 0,  # no candidates at all
                    'correct': 0,  # correct entries (one of the candidates matches)
                    'incorrect': 0,  # incorrect entries (none of the candidate matches)
                    'total': 0,  # targets overall
                }
            aggStats[k]['missing'] += v['missing']
            aggStats[k]['correct'] += v['correct']
            aggStats[k]['incorrect'] += v['incorrect']
            aggStats[k]['total'] += v['total']

    # done
    # TODO somehow track the order of labels for better display
    return {
        'tables': allStats,
        'agg': aggStats
    }


def run():

    # our solutions have to be present
    if not os.path.exists(os.path.join(config.BASE_PATH, 'solution')):
        return {}

    # assemble all parts
    return {
        'cea': evalTargets(
            type='cea',
            solKeyFkt=lambda row: (int(row['Col Id']), int(row['Row Id'])),
            solTargetFkt=lambda row: row['Entity URI'],
            submKeyFkt=lambda el: (el['col_id'], el['row_id']),
            trgtKeyFkt=lambda el: (el['col_id'], el['row_id']),
        ),
        'cpa': evalTargets(
            type='cpa',
            solKeyFkt=lambda row: (int(row['Col 1 Id']), int(row['Col 2 Id'])),
            solTargetFkt=lambda row: row['Property URI'],
            submKeyFkt=lambda el: (el['subj_id'], el['obj_id']),
            trgtKeyFkt=lambda el: (el['sub_id'], el['obj_id']),
        ),
        'cta': evalTargets(
            type='cta',
            solKeyFkt=lambda row: (int(row['Col Id'])),
            solTargetFkt=lambda row: row['Col Class URI'],
            submKeyFkt=lambda el: (el['col_id']),
            trgtKeyFkt=lambda el: (el['col_id']),
        ),
    }
