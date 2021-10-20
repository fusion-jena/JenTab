# this creates the files necessary to run a particular table via the mocking of Solver
# needs to be kept in sync with run.py!

import config
from externalServices.manager import Manager

import util_log
import json
import os


def run():

    # configure the table you want to have exported
    year = 2020
    round = 1

    # example table
    # tablenames = ['3C3INQLM'] # BioTables
    # tablenames = ['0bc67e05a4d14011a2cf3fca2f869495', '097c576b688e46eca8583b1de1a84a59', 'd5542ea1fddf44c39d2bb70dc436ddf8', '1104b09c7f1f434a89a30a977b052c53', '39a2d36769294a0a846cc209c45234e4', '0be7652b187b45f5b111d51905c3c25b'] #BiodivTab
    # tablenames = ['00HP358M'] # HardTables 3.3
    tablenames  = ['GitTables_1501', 'GitTables_1612', 'GitTables_1737']
    # subset of data
    # including startrow, exclusing endrow
    startrow = 0
    endrow = -1 # -1 to disable

    for tablename in tablenames:

        # get the corresponding work item from the Manager
        work = Manager.get_desc(year, round, tablename)

        # filter data, if requested
        if endrow > 0:

            # rename files
            tablename = f"{tablename}.{startrow}_{endrow}"

            # filter data
            work['data'] = [col[startrow:endrow] for col in work['data']]

            # filter targets
            work['targets']['cea'] = [target for target in work['targets']['cea'] if (target['row_id'] >= startrow) and (target['row_id'] < endrow)]

        # write to files
        target_path = os.path.join(config.CUR_PATH, '..', 'Solver', 'mock')
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        with open(os.path.join(target_path, '{}.json'.format(tablename)), 'w') as file:
            file.write(json.dumps(work))
        with open(os.path.join(target_path, '{}.targets.json'.format(tablename)), 'w') as file:
            file.write(json.dumps(work['targets']))
        if 'gt' in work:
            with open(os.path.join(target_path, '{}.gt.json'.format(tablename)), 'w') as file:
                file.write(json.dumps(work['gt']))
        util_log.info('written files to {}'.format(target_path))


if __name__ == '__main__':
    run()
