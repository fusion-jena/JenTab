# this creates the files necessary to run a particular table via the mocking of Baseline_Approach
# needs to be kept in sync with run.py!

import config
from externalServices.clean_cells import CleanCells
from externalServices.language_prediction import LanguagePrediction
from externalServices.manager import Manager
from externalServices.type_prediction import TypePrediction
from externalServices.baseline_approach_service import BaselineApproach
from externalServices.auditor_service import Auditor

import util
import util_log
import pprint
import json
import os

from os.path import realpath, join
from run import to_snake_case, prepareData


def run():
    # configure the table you want to have exported
    year = 2020
    round = 4
    tablename = 'OHGI1JNY'

    # get the corresponding work item from the Manager
    work = Manager.get_desc(year, round, tablename)

    # activate auditing in baseline_approach...
    if work['audit']:
        BaselineApproach.activateAuditing.send([True])

    if work['analyze']:
        BaselineApproach.activateLogging.send([True])

    # run all data preparations
    result = prepareData(work)

    solution = BaselineApproach.solve.send([result, work['targets']])

    if work['audit'] and solution['audit']:
        # Auditor.audit_lst.send(solution['audit'])
        Manager.audit_lst(solution['audit'])
        print("Done")

    # submit the analysis results, if this is requested by Manager
    if work['analyze'] and solution['checkpoints']:
        Manager.store_analysisData(tablename, solution['checkpoints'])
        print("Done")


if __name__ == '__main__':
    run()
