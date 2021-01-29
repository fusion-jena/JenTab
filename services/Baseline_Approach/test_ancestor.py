import mock.loader as loader
from tabulate import tabulate
from approach.baseline_approach import BaselineApproach



if __name__ == '__main__':
    table = loader.load_file()
    targets = loader.load_targets()

    ba = BaselineApproach(table, targets)
    ba.exec_pipeline()

    res = {}
    res['cea'] = ba.generate_CEA(targets['cea'])
    res['cta'] = ba.generate_CTA(targets['cta'])
    res['cpa'] = ba.generate_CPA(targets['cpa'])

    print('\n====== CEA ======')
    cea = [[item['col_id'], item['row_id'], item['mapped']] for item in res['cea']]
    print(tabulate(cea, headers=['col_id', 'row_id', 'mapped'], tablefmt='orgtbl'))

    print('\n====== CTA ======')
    cta = [[item['col_id'], item['mapped']] for item in res['cta']]
    print(tabulate(cta, headers=['col_id', 'mapped'], tablefmt='orgtbl'))

    print('\n====== CPA ======')
    cpa = [[item['subj_id'], item['obj_id'], item['mapped']] for item in res['cpa']]
    print(tabulate(cpa, headers=['subj_id', 'obj_id', 'mapped'], tablefmt='orgtbl'))