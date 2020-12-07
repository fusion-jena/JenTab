import flask
import os
import tempfile
import zipfile
import config
import db
import util_log


def downloadErrors():
    """
    download the compressed archive of all errors
    """
    path = os.path.join(config.WORK_PATH, 'errors.zip')
    if os.path.exists(path):
        return flask.send_file(path, attachment_filename=os.path.basename(path), as_attachment=True)
    else:
        return flask.abort(404)


def downloadResults():
    """
    download the compressed archive of all results
    """
    path = os.path.join(config.WORK_PATH, 'results.zip')
    if os.path.exists(path):
        return flask.send_file(path, attachment_filename=os.path.basename(path), as_attachment=True)
    else:
        return flask.abort(404)


def downloadTables():
    """
    download the current version of the SQLite database used
    """
    if os.path.exists(db.DB_PATH):
        return flask.send_file(db.DB_PATH, attachment_filename=os.path.basename(db.DB_PATH), as_attachment=True)
    else:
        return flask.abort(404)


def downloadSubmissions(challenge, showMissing):
    """
    download submission ready data files
    """

    # generator depends on challenge type and sometimes mode (2019 vs 2020) active
    if challenge == 'cea':
        if config.OUTPUT_2019_FORMAT:
            def generate():
                """2019 format: col_id before row_id"""
                for row in db.getAllTargets('cea', not showMissing):
                    yield '{},{},{},{}{}\n'.format(
                        row['table_name'],
                        row['col_id'],
                        row['row_id'],
                        config.URL_PREFIX if config.OUTPUT_ADD_PREFIX else '',
                        row['mapped']
                    )
        else:
            def generate():
                """2020 format: row_id before col_id"""
                for row in db.getAllTargets('cea', not showMissing):
                    yield '{},{},{},{}{}\n'.format(
                        row['table_name'],
                        row['row_id'],
                        row['col_id'],
                        config.URL_PREFIX if config.OUTPUT_ADD_PREFIX else '',
                        row['mapped']
                    )
    elif challenge == 'cpa':
        def generate():
            for row in db.getAllTargets('cpa', not showMissing):
                yield '{},{},{},{}{}\n'.format(
                    row['table_name'],
                    row['sub_id'],
                    row['obj_id'],
                    config.URL_PREFIX if config.OUTPUT_ADD_PREFIX else '',
                    row['mapped']
                )
    elif challenge == 'cta':
        def generate():
            for row in db.getAllTargets('cta', not showMissing):
                yield '{},{},{}{}\n'.format(
                    row['table_name'],
                    row['col_id'],
                    config.URL_PREFIX if config.OUTPUT_ADD_PREFIX else '',
                    row['mapped']
                )
    else:
        raise Exception('Unknown challenge: {}'.format(challenge))

    # stream response
    filename = '{}{}.csv'.format(challenge, 'Missing' if showMissing else '')
    return flask.Response(
        generate(),
        mimetype='text/csv',
        headers={
            "Content-disposition": "attachment; filename={}".format(filename)
        }
    )
