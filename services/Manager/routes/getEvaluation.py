import config
import db
import csv
import json
import os
from inc.util import getWikiID


def find(arr, fkt):
    """find a specific element in the given array"""
    for el in arr:
        if fkt(el):
            return el


def evalTargets(type, mappingHeader, findFkt):

    # basic input check
    if type not in ['cea', 'cpa', 'cta']:
        raise Exception('Invalid type {}'.format(type))

    # wrapper for our result (define the structure here for overview)
    results = {
        'missingSolutions': 0,
        'missingSubmissions': 0,
        'superfluousMappings': 0,
        'missingMappings': 0,
        'correctMappings': 0,
        'incorrectMappings': 0,
    }

    # get a list of solved tables
    solvedTables = db.getSolvedTables()
    solvedTableLookup = {}
    for t in solvedTables:
        solvedTableLookup[t['table_name']] = t['table_id']

    # check cea
    missingSolutions = set([t['table_name'] for t in solvedTables])
    with open(os.path.join(config.BASE_PATH, 'solution', type + '.csv'), mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        solutions = None
        unsolvedTables = set()
        for row in csv_reader:

            # skip tables with no solutions
            if row['Filename'] not in solvedTableLookup:
                unsolvedTables.add(row['Filename'])
                continue

            # memorize that we have solutions for this table
            missingSolutions.discard(row['Filename'])

            # fetch our results, if necessary
            curTable = solvedTableLookup[row['Filename']]
            if not solutions or (solutions[0]['table_id'] != curTable):
                solutions = db.getSolutions(type, curTable)

            # find the submission that corresponds to our current line (solution)
            submission = find(solutions, findFkt(row))
            if not submission:
                results['superfluousMappings'] += 1
                continue

            # no solution for this target (yet)
            if not submission['mapped']:
                results['missingMappings'] += 1
                continue

            # compare submission and our ground truth
            targets = [getWikiID(t) for t in row[mappingHeader].split(',')]
            if find(targets, lambda x: x == getWikiID(submission['mapped'])):
                results['correctMappings'] += 1
            else:
                results['incorrectMappings'] += 1

    # store results
    results['missingSolutions'] = len(missingSolutions)
    results['missingSubmissions'] = len(unsolvedTables)

    # done
    return results


def run():

    # our solutions have to be present
    if not os.path.exists(os.path.join(config.BASE_PATH, 'solution')):
        return {}

    # assemble all parts
    return {
        'cea': evalTargets(
            type='cea',
            mappingHeader='Entity URI',
            findFkt=lambda row: lambda x: (str(row['Row Id']) == str(x['row_id'])) and (str(row['Col Id']) == str(x['col_id'])),
        ),
        'cpa': evalTargets(
            type='cpa',
            mappingHeader='Property URI',
            findFkt=lambda row: lambda x: (str(row['Col 1 Id']) == str(x['sub_id'])) and (str(row['Col 2 Id']) == str(x['obj_id'])),
        ),
        'cta': evalTargets(
            type='cta',
            mappingHeader='Col Class URI',
            findFkt=lambda row: lambda x: str(row['Col Id']) == str(x['col_id']),
        )
    }
