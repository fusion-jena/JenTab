# this creates the files necessary to run a particular table via the mocking of Solver
# needs to be kept in sync with run.py!

from externalServices.manager import Manager
from externalServices.baseline_approach_service import BaselineApproach



def run():
    # configure the table you want to have exported
    year = 2021
    round = 1.2
    tablename = 'RYTFLT5K'

    # get the corresponding work item from the Manager
    work = Manager.get_desc(year, round, tablename)

    # activate auditing in baseline_approach...
    if work['audit']:
        BaselineApproach.activateAuditing.send([True])

    if work['analyze']:
        BaselineApproach.activateLogging.send([True])

    # run all data preparations
    result = work

    solution = BaselineApproach.solve.send([result, work['targets']])
    print(solution['cta'])
    if work['audit'] and solution['audit']:
        # Auditor.audit_lst.send(solution['audit'])
        Manager.audit_lst(solution['audit'])
        print("Done")

    # submit the analysis results, if this is requested by Manager
    if work['analyze'] and solution['checkpoints']:
        Manager.store_analysisData(tablename, solution['checkpoints'])
        print("Done")

    resp = Manager.store_result(tablename, work)
    if resp:
        print('   stored results')
    else:
        print('   sotred error')


if __name__ == '__main__':
    run()
