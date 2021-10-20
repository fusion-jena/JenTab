import mock.loader as loader
from approach.baseline_approach import BaselineApproach
from tabulate import tabulate
from dateutil.relativedelta import relativedelta
import datetime
import utils.util_log
import logging

# current test file; needs to reside in /mock
# may include a range like 'abcdef.0_500'
# TEST_FILE = '097c576b688e46eca8583b1de1a84a59' # chemical elements table col id = 14 fe should be the iron
# TEST_FILE = '0bc67e05a4d14011a2cf3fca2f869495' #Unknown / Undetermined
TEST_FILE = 'GitTables_1612'
# see log messages
# utils.util_log.logger.setLevel(logging.INFO)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HELPER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def humanTimeDiff(sec):
    """
    get a human readable formating of a time difference
    https://stackoverflow.com/a/11157649/1169798
    """
    delta = relativedelta(seconds=sec)
    return ('%02d:%02d:%02d' % (getattr(delta, 'hours'), getattr(delta, 'minutes'), getattr(delta, 'seconds')))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Process ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    table = loader.load_file( TEST_FILE )
    targets = loader.load_targets( TEST_FILE )
    gt = loader.load_gt( TEST_FILE )

    # during testing make sure we do not even have partial results
    for task in ['cea', 'cta', 'cpa']:
        if task in targets:
            for el in targets[task]:
                if el['mapped']:
                    el['mapped'] = None
        if task in table['targets']:
            for el in table['targets'][task]:
                if el['mapped']:
                    el['mapped'] = None

    # run the pipeline
    start = datetime.datetime.now().timestamp()
    ba = BaselineApproach(table, targets)
    ba.exec_pipeline()

    res = {}
    res['cea'] = ba.generate_CEA(targets['cea'])
    res['cta'] = ba.generate_CTA(targets['cta'])
    res['cpa'] = ba.generate_CPA(targets['cpa'])
    pTable = ba.get_parsedTable()
    proxyService = ba.get_proxyService()
    end = datetime.datetime.now().timestamp()
    print('time taken: {}'.format(humanTimeDiff(end - start)))

    # overall
    print('CEA: {} / {}'.format(len(res['cea']), len(targets['cea'])))
    print('CTA: {} / {}'.format(len(res['cta']), len(targets['cta'])))
    print('CPA: {} / {}'.format(len(res['cpa']), len(targets['cpa'])))

    # disable detailed logging again
    utils.util_log.logger.setLevel(logging.WARNING)

    # table overview
    from debug.table_overview import run as print_tableOverview
    print_tableOverview( pTable, proxyService, MAX_LINES=50 )

    # CEA solution overview
    from debug.cea_results import run as print_ceaResults
    print_ceaResults( pTable, proxyService, gt=gt['cea'] if gt and ('cea' in gt) else None )

    # CTA solution overview
    from debug.cta_results import run as print_ctaResults
    print_ctaResults( pTable, proxyService, gt=gt['cta'] if gt and ('cta' in gt) else None )

    # CPA solution overview
    from debug.cpa_results import run as print_cpaResults
    print_cpaResults( pTable, proxyService )

    # CTA candidate details
    #from debug.cta_finalCandidates import run as print_ctaCandiates
    #print_ctaCandiates( pTable, proxyService )

    # generate solution files for this table
    #from debug.table_createSolutionFile import run as createSolutionFile
    #createSolutionFile( pTable, proxyService, res=res )

    # errors if thrown
    errs = ba.get_Errors()
    if errs:
        print('\n\033[91m====== Errors ======\033[0m\n')
        for err in errs:
            print(err)
