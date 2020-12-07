import config
import db
import util_log
import datetime
import flask
import json
import re
import os
import zipfile


def parseEntries(data, type):
    """
    parse the results of CEA or CPA task in both old and new notation
    returns new notation as in { key1: X, key2: x, mapped: y }
    """
    # no data at all
    res = []
    if not data:
        pass
    # new notation
    elif isinstance(data, list):
        res = data
    # old notation
    else:
        for key, value in data.items():
            ids = key.split(',')
            if type == 'CEA':
                # CEA
                res.append({'row_id': ids[0], 'col_id': ids[1], 'mapped': value})
            elif type == 'CPA':
                # CPA
                res.append({'sub_id': ids[0], 'obj_id': ids[1], 'mapped': value})
            else:
                # CTA
                res.append({'col_id': key, 'mapped': value})
    # remove empty entries
    return [el for el in res if el['mapped']]


def storeResultFile(kind, filename, content):
    """
    store the respective result/error in a file and/or zip-archive
    """

    # determine paths
    if kind == 'result':
        path = os.path.join(config.RESULT_PATH, filename)
        zipPath = os.path.join(config.WORK_PATH, 'results.zip')
        store = config.STORE_RESULT
        storeZip = config.STORE_RESULT_ZIP
    else:
        path = os.path.join(config.ERROR_PATH, filename)
        zipPath = os.path.join(config.WORK_PATH, 'errors.zip')
        store = config.STORE_ERRORS
        storeZip = config.STORE_ERRORS_ZIP

    # write individual result file
    if store:
        with open(path, 'w') as out:
            out.write(content)

    # append to respective zip file
    if storeZip:
        with zipfile.ZipFile(zipPath, 'a') as zip:
            zip.write(
                path,
                arcname=filename
            )


def run(request, kind, table):
    """process a single request that hands in work results"""

    # get the client id
    clientID = request.args.get('client')
    if clientID is None:
        flask.abort(401)

    # check the assignment
    if not db.isAssignmentOpen(table, clientID):
        flask.abort(404)

    # determine parameters
    normalizedTime = re.sub('[^0-9TZ]', '_', datetime.datetime.now().isoformat())
    filename = "{}_{}".format(normalizedTime, table)
    payload = request.get_data(as_text=True)
    storeResultFile(kind, filename, payload)
    if kind == 'result':
        result = filename
        error = None
    else:
        result = None
        error = filename

    # try to parse the file and update results
    if kind == 'result':
        try:

            # get table id
            table_id = db.getIdForTable(table)

            # parse payload
            data = json.loads(payload)

            # update CEA result
            if data['cea']:
                entries = parseEntries(data['cea'], 'CEA')
                db.updateCEA(table_id, entries)

            # update CTA result
            if data['cpa']:
                entries = parseEntries(data['cpa'], 'CPA')
                db.updateCPA(table_id, entries)

            # update CTA result
            if data['cta']:
                entries = parseEntries(data['cta'], 'CTA')
                db.updateCTA(table_id, entries)

            # store non fatal errors
            if data['errors']:
                if isinstance(data['errors'], list):
                    data['errors'] = '\n\n----------------------------------------------\n\n'.join(data['errors'])
                storeResultFile('error', filename, data['errors'] )
                error = filename

        except Exception as ex:
            util_log.error(ex)

    # update assignment in database
    db.resolveAssignment(table, clientID, datetime.datetime.now().timestamp(), result, error)

    return '', 200


def storeAnalysisFile(request, table):
    """
    store a single analysis file
    """

    # only, if active
    if not config.ENABLE_ANALYSIS:
        return

    # store in file
    filename = os.path.join(config.ANALYSIS_PATH, '{}.json'.format(table))
    with open(filename, 'wb') as out:
        out.write(request.get_data())

    return '', 200
