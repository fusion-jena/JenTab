# this creates the files necessary to run a particular table via the mocking of Baseline_Approach
# needs to be kept in sync with run.py!

import config
from externalServices.clean_cells import CleanCells
from externalServices.language_prediction import LanguagePrediction
from externalServices.manager import Manager
from externalServices.type_prediction import TypePrediction

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

    # run all data preparations
    result = prepareData(work)

    # write to files
    target_path = os.path.join(config.CUR_PATH, '..', 'Baseline_Approach', 'mock')
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    with open(os.path.join(target_path, '{}.json'.format(tablename)), 'w') as file:
        file.write(json.dumps(result))
    with open(os.path.join(target_path, '{}.targets.json'.format(tablename)), 'w') as file:
        file.write(json.dumps(work['targets']))
    util_log.info('written files to {}'.format(target_path))


if __name__ == '__main__':
    run()
