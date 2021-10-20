import datetime
import flask
import os
import config
import db
from inc.parse import parse
from inc.util import getWikiID


def run(request):
    """
    return a new work package including all necessary information
    """

    # get the client id
    clientID = request.form.get('client') or request.args.get('client')
    if clientID is None:
        flask.abort(401)

    # get a unprocessed table meta
    table = db.getUnsolvedTable(clientID, datetime.datetime.now().timestamp())
    if not table:
        flask.abort(410)

    return getData( table['id'], table['name'] )


def getDescription(rYear, rRound, rTablename):
    """
    get the description of the working package specified
    this does not assign the respective table
    meant for debug use; should mirror run()
    """

    # resolve to ID
    table = db.getIdForTable(rTablename)
    if not table:
        return flask.abort(404)

    # get work package
    res = getData( table, rTablename )

    # check, if there is also ground truth data
    GT_PATH = os.path.join( config.BASE_PATH, 'gt' )
    if os.path.exists( GT_PATH ):

        res['gt'] = {}

        # determine target files
        targets = [f for f in os.listdir(GT_PATH) if os.path.isfile(os.path.join(GT_PATH, f)) and f.endswith('.csv')]
        CEA_TARGET = [f for f in targets if 'CEA' in f]
        CEA_TARGET = CEA_TARGET[0] if len(CEA_TARGET) > 0 else None
        CTA_TARGET = [f for f in targets if 'CTA' in f]
        CTA_TARGET = CTA_TARGET[0] if len(CTA_TARGET) > 0 else None
        CPA_TARGET = [f for f in targets if 'CPA' in f]
        CPA_TARGET = CPA_TARGET[0] if len(CPA_TARGET) > 0 else None

        if CEA_TARGET:
            res['gt']['cea'] = []
            def cb(entry):
                res['gt']['cea'].append({
                  'row_id': entry[1],
                  'col_id': entry[2],
                  'mapped': get_min_id(entry[3].split(' ')),
                })
            parseTargetFile( os.path.join( GT_PATH, CEA_TARGET ), rTablename, cb)

        if CTA_TARGET:
            res['gt']['cta'] = []
            def cb(entry):
                res['gt']['cta'].append({
                  'col_id': entry[1],
                  'mapped': get_min_id(entry[2].split(' ')),
                })
            parseTargetFile( os.path.join( GT_PATH, CTA_TARGET ), rTablename, cb)

        if CPA_TARGET:
            res['gt']['cpa'] = []
            def cb(entry):
                res['gt']['cpa'].append({
                  'subj_id': entry[1],
                  'obj_id': entry[2],
                  'mapped': get_min_id(entry[3].split(' ')),
                })
            parseTargetFile( os.path.join( GT_PATH, CPA_TARGET ), rTablename, cb)

    # done
    return res


def get_min_id( entities ):
    """
    from a list of entities, retrieve the one with the lowest ID

    VERY crude heuristic; actually IRIs are "said to be the same" or are redirecting to the correct solution
    but this would be more difficult to determine automatically
    """
    entities = map( getWikiID, entities ) # remove the namespace
    entities = map( lambda x: int(x[1:]), entities ) # remove the leading Q
    entities = sorted( entities )
    return f"Q{entities[0]}"


def parseTargetFile( filePath, table, cb ):
    """
    retrieve the targets associated with table from the target file in path
    and call cb with each matching entry
    """
    with open(filePath, "r", encoding="utf-8") as file:
        for i, line in enumerate(file):
            entry = line.replace('"', '').strip().split(',')
            if entry[0] == table:
                cb( entry )



def getData( table, tableName ):
    """
    actually fetch all data
    used in both getWork() and getDescription()
    """

    # get corresponding targets
    cea = db.getCEA(table)
    cpa = db.getCPA(table)
    cta = db.getCTA(table)

    # determine, if there are headers in the file
    # signal: CEA in the first row, basically says there is no header, but already a content row
    hasHeaders = not any (el['row_id'] == 0 for el in cea)

    # get table contents
    tablePath = os.path.join(config.TABLES_PATH, tableName + '.csv')
    parsed = parse(tablePath, hasHeaders)

    # stitch everything together
    return {
        'analyze': config.ENABLE_ANALYSIS,
        'audit': config.ENABLE_AUDIT,
        'name': tableName,
        'targets': {
            'cea': cea,
            'cpa': cpa,
            'cta': cta,
        },
        'orientation': parsed['orientation'],
        'header': parsed['header'],
        'data': parsed['cols'],
    }
