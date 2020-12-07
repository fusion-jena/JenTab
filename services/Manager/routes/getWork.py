import datetime
import flask
import os
import config
import db
from inc.parse import parse


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

    # get corresponding targets
    cea = db.getCEA(table['id'])
    cpa = db.getCPA(table['id'])
    cta = db.getCTA(table['id'])

    # get table contents
    tablePath = os.path.join(config.TABLES_PATH, table['name'] + '.csv')
    parsed = parse(tablePath)

    # stitch everything together
    return {
        'analyze': config.ENABLE_ANALYSIS,
        'audit': config.ENABLE_AUDIT,
        'name': table['name'],
        'targets': {
            'cea': cea,
            'cpa': cpa,
            'cta': cta,
        },
        'orientation': parsed['orientation'],
        'header': parsed['header'],
        'data': parsed['cols'],
    }


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

    # get corresponding targets
    cea = db.getCEA(table)
    cpa = db.getCPA(table)
    cta = db.getCTA(table)

    # get table contents
    tablePath = os.path.join(config.TABLES_PATH, rTablename + '.csv')
    parsed = parse(tablePath)

    # stitch everything together
    return {
        'analyze': config.ENABLE_ANALYSIS,
        'audit': config.ENABLE_AUDIT,
        'name': rTablename,
        'targets': {
            'cea': cea,
            'cpa': cpa,
            'cta': cta,
        },
        'orientation': parsed['orientation'],
        'header': parsed['header'],
        'data': parsed['cols'],
    }
