import sys
import codecs

# set global encoding to UTF-8 in py3
# StreamWriter Wrapper around Stdout: http://www.macfreek.nl/memory/Encoding_of_Python_stdout
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import config
import db
from routes.getAnalysis import run as getAnalysis
from routes.getEvaluation import run as getEvaluation
from audit.routes.getInsights import run as getAudit
from routes.getMissingMappings import run as getMissingMappings
from routes.getStats import run as getStats
from routes.getWork import run as getWork, getDescription
from routes.init import run as init
from routes.store import run as store, storeAnalysisFile
from audit.inc import audit
from audit.routes import store as auditStore
from routes.download import downloadErrors, downloadResults, downloadTables, downloadSubmissions
import flask
from flask_httpauth import HTTPBasicAuth
import os
import util_log
from werkzeug.security import generate_password_hash, check_password_hash

app = flask.Flask(__name__, static_folder=os.path.join(config.CUR_PATH, 'static'))

# basic auth
if config.BASIC_AUTH_ENABLED:
    util_log.info('enabling Basic Auth')
auth = HTTPBasicAuth()
users = {
    config.USER_NAME: generate_password_hash(config.USER_PASSWORD)
}


@auth.verify_password
def verify_password(username, password):
    if not config.BASIC_AUTH_ENABLED:
        return True
    if username in users and check_password_hash(users.get(username), password):
        return True


# initialize our internal database, if needed
if db.isEmpty():
    util_log.info('initializing database')
    init()
else:
    util_log.info('using existing database')

# initialize audit database if not exists
util_log.info('initializing Audit database')
audit = audit.Audit()

@app.route('/test')
@auth.login_required
def test():
    return '/test'


@app.route('/downloadErrors', methods=['GET'])
@auth.login_required
def routeDownloadErrors():
    return downloadErrors()


@app.route('/downloadResults', methods=['GET'])
@auth.login_required
def routeDownloadResults():
    return downloadResults()


@app.route('/downloadSubmission/<string:challenge>', defaults={'missing': False}, methods=['GET'])
@app.route('/downloadSubmission/<string:challenge>/<string:missing>', methods=['GET'])
@auth.login_required
def routeDownloadSubmission(challenge, missing):
    challenge = challenge.lower()
    if challenge not in ['cea', 'cpa', 'cta']:
        abort(404)
    return downloadSubmissions(challenge, missing)


@app.route('/downloadTables', methods=['GET'])
@auth.login_required
def routeDownloadTables():
    return downloadTables()


@app.route('/getStats', methods=['POST'])
@auth.login_required
def routeGetStats():
    return getStats()


@app.route('/getMissingMappings', methods=['POST'])
@auth.login_required
def routeGetMissingMappings():
    return getMissingMappings()


@app.route('/getAnalysis', methods=['POST'])
@auth.login_required
def routeGetAnalysis():
    return getAnalysis()


@app.route('/getEvaluation', methods=['POST'])
# @auth.login_required
def routeGetEvaluation():
    return getEvaluation()


@app.route('/getAudit', methods=['POST'])
# @auth.login_required
def routeGetAudit():
    return getAudit()


@app.route('/getWork', methods=['POST'])
# @auth.login_required
def routeGetWork():
    return getWork(flask.request)


@app.route('/getDescription', methods=['POST'])
# @auth.login_required
def routeGetDescription():
    reqTable = flask.request.args.get('table')
    reqYear = flask.request.args.get('year')
    reqRound = flask.request.args.get('round')
    return getDescription(reqYear, reqRound, reqTable)


@app.route('/static/<path:file>')
@auth.login_required
def send_static(file):
    return flask.send_from_directory(app.static_folder, file)


@app.route('/storeAnalysisData/<string:table>/', methods=['PUT'])
@auth.login_required
def storeAnalysisData(table):
    return storeAnalysisFile(flask.request, table)


@app.route('/storeResult/<string:table>/', methods=['PUT'])
@auth.login_required
def storeResult(table):
    return store(flask.request, 'result', table)


@app.route('/storeError/<string:table>/', methods=['PUT'])
@auth.login_required
def storeError(table):
    return store(flask.request, 'error', table)


@app.route('/audit_lst', methods=['POST'])
@auth.login_required
def audit_lst():
    return auditStore.storeAuditRecords(flask.request, audit)


@app.route('/')
@auth.login_required
def root():
    return app.send_static_file('index.html')


# run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100)
