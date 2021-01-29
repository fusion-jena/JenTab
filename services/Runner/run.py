import config
from externalServices.clean_cells import CleanCells
from externalServices.language_prediction import LanguagePrediction
from externalServices.manager import Manager
from externalServices.type_prediction import TypePrediction

from externalServices.baseline_approach_service import BaselineApproach

from externalServices.auditor_service import Auditor

import util
import util_log
from multiprocessing import Pool
import pprint
import json
import time

from os.path import realpath, join

# pretty print for debugging
pp = pprint.PrettyPrinter(indent=4)

# wait for all services to come online (only in docker mode)
if config.run_mode == 1:
    services = [CleanCells, LanguagePrediction, TypePrediction]
    while len(services) > 0:
        time.sleep(5)
        services = [s for s in services if not s.is_online()]
        if len(services) > 0:
            util_log.info('waiting for {} services to come online'.format(len(services)))
    util_log.info('All dependencies online')


def to_snake_case(text):
    new_text = text.replace('-', ' ')
    words = new_text.split()
    return "_".join(words)


def get_batch(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]


def prepareData(work):
    """
    data preparations like cell cleaning etc.
    separate function, so it can be easily reused in createExample.py to provide debug data
    """

    # prepare our result object
    result = {
        'orientation': work['orientation'],
        'header': work['header'],
        'name': work['name'],
        'data': []
    }
    for i, col in enumerate(work['data']):
        result['data'].append({'col_id': i, 'original_cell_vals': col})

    # clean cells
    for col in result['data']:
        # init clean_cell_vals holder
        col['clean_cell_vals'] = []

        # temp holder for col['original_cell_vals']
        fixed_original = []

        # start the batch processing of generic fixes...
        for b_original_cell_vals in get_batch(col['original_cell_vals'], config.BATCH_SIZE):
            # encoding fix + data cleaning + generic Parsing for "all"
            clean_res = CleanCells.fix_cell_lst.send([b_original_cell_vals])

            # data cleaned + encoding fix + parsing
            col['clean_cell_vals'].extend(clean_res['clean'])

            # encoding fix  is only included
            fixed_original.extend(clean_res['fixed_original'])

        # copy full lst to the col placeholder.
        col['original_cell_vals'] = fixed_original

    util_log.info('   cleaned cell values')

    # get columns' languages
    for col in result['data']:
        lang = []
        # start the batch processing of language prediction...
        for b_vals in get_batch(col['clean_cell_vals'], config.BATCH_SIZE):
            lang.extend(LanguagePrediction.get_language_lst.send(b_vals)['res'])

        # aggregate lang per column
        col['lang'] = util.get_most_frequent(lang)
    util_log.info('   retrieved languages')

    # get columns' types
    for col in result['data']:
        # init placeholder for full type list
        datatype = []
        # start the batch processing of type prediction...
        for b_vals in get_batch(col['clean_cell_vals'], config.BATCH_SIZE):
            datatype.extend(TypePrediction.get_type_lst.send(b_vals)['res'])

        # aggregate type per column
        col['type'] = util.get_most_frequent(datatype)
    util_log.info('   retrieved datatypes')

    # specific clean cells
    for col in result['data']:

        # data collector placeholders
        new_clean_lst = []

        # start the batch processing of specific clean cells...
        for b_vals in get_batch(col['clean_cell_vals'], config.BATCH_SIZE):
            # specific clean up per type
            # OBJECT: Autocorrect + remove special chars
            # QUANTITY: Custom parsing "137 km2 (2.3 mi)" --> 137
            clean_res = CleanCells.specific_clean_cell_lst.send([col['type'], b_vals])

            # collects new clean cell values in the corresponding placeholder
            new_clean_lst.extend(clean_res['clean'])

        # override clean_cell_vals with specific clean up if applied, otherwise, no change.
        col['clean_cell_vals'] = new_clean_lst

    util_log.info('   type based clean values')

    return result


def run():
    while True:

        # retrieve work package
        util_log.info('Retrieving Work')
        work = Manager.get_work()
        if not work:
            util_log.info('No more work. Shutting down.')
            exit()
        util_log.info('   got work package: {}'.format(work['name']))

        # enable analysis logging, if requested
        if work['analyze']:
            BaselineApproach.activateLogging.send([True])

        # enable auditing, if requested
        if work['audit']:
            BaselineApproach.activateAuditing.send([True])

        try:
            tablename = work['name']

            # Prepare the data
            result = prepareData(work)
            util_log.info("   prepared data")

            # Solve ...
            solution = BaselineApproach.solve.send([result, work['targets']])
            util_log.info("   baseline: Solved CEA, CTA and CPA... : {0}".format(tablename))

            # Assign solution parts to result
            result['cea'] = solution['cea']
            result['cta'] = solution['cta']
            result['cpa'] = solution['cpa']
            result['errors'] = solution['errors']

            # store the result
            resp = Manager.store_result(tablename, result)
            if resp:
                util_log.info('   stored results')
                if result['errors']:
                    util_log.warn('      including non-fatal errors')
            else:
                util_log.error('   failed to store results')

            # submit the analysis results, if this is requested by Manager
            if work['analyze'] and solution['checkpoints']:
                Manager.store_analysisData(tablename, solution['checkpoints'])

            # if auditing is requested and successfully included in the solution, then submit records
            if work['audit'] and solution['audit']:
                # Auditor.audit_lst.send(solution['audit'])
                Manager.audit_lst(solution['audit'])

            # Handles partial results if add back to errors with actual errors
            if config.RASIE_ERROR_FOR_INCOMPLETE_TABLES and 'timeout' in solution:
                raise TimeoutError()

        # "global" error catching
        except Exception as ex:
            # util_log.error(str(ex))  # stringify the error to encode it to UTF-8
            resp = Manager.store_error(tablename)
            if resp:
                util_log.info('   stored error')
            else:
                util_log.error('   failed to store error')
                # exit()


if __name__ == '__main__':
    run()
