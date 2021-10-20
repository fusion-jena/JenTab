from flask import Flask, request
from waitress import serve
from werkzeug.exceptions import InternalServerError
import traceback
import config
from approach.baseline_approach import BaselineApproach
import utils.util_log as util_log
from utils.time_scoped_run import time_scoped_run
from utils import res_IO

app = Flask(__name__)

# app.debug = False


def work(table, targets):
    """
    Actual work function. Encapsulates our logic
    """
    # init Baseline Approach
    ba = BaselineApproach(table, targets)

    # run pipeline
    ba.exec_pipeline()

    # ensure the final solution is also stored
    res_IO.set_res(table['name'], ba.get_Results())


@app.route('/solve', methods=['POST'])
def solve():
    # parameters
    table = request.json["table"]
    targets = request.json["targets"]

    # run actual work function given SLA in seconds
    res = time_scoped_run(work, (table, targets), {}, config.PIPELINE_SLA_SEC)

    if res:
        if res_IO.res_exists(table['name']):
            res_dict = res_IO.get_res(table['name'], True)
            # pipeline finished its work, we retrieve assigned result from the shared variable
            return res_dict
        else:
            raise Exception(f"Could not find solution file for table {table['name']}")
    else:
        # SLA passed, pipeline failed to continue execution, we raise timeout error
        if config.ENABLE_PARTIAL_RES_SUBMISSION:

            if res_IO.res_exists(table['name']):
                # loads last saved res from json file
                last_saved_res = res_IO.get_res(table['name'], False)
                # Timeout = pipeline failed to complete its work within the SLA. aka partial res returend
                last_saved_res['timeout_error'] = True
                return last_saved_res
            else:
                # Pipeline failed to even init a partial result. (too early timeout)
                raise TimeoutError()
        else:
            raise TimeoutError()


@app.route('/activateLogging', methods=['POST'])
def postActivateLogging():
    config.LOG_INTERMEDIATE_RESULTS = True
    return {'status': 'ok'}


@app.route('/activateAudit', methods=['POST'])
def postActivateAudit():
    config.AUDIT_ACTIVATED = True
    return {'status': 'ok'}


@app.route('/')
def hello():
    return 'Hello baseline.svc!'


@app.errorhandler(InternalServerError)
def handle_500(e):
    """output the internal error stack in case of unhandled exception"""
    return traceback.format_exc(), 500


if __name__ == '__main__':
    # util_log.init('baseline.log')
    # app.run(port=5000)
    serve(app, host='0.0.0.0', port=5000)
