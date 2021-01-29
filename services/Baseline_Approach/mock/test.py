import mock.loader as loader
from approach.baseline_approach import BaselineApproach
from tabulate import tabulate
from dateutil.relativedelta import relativedelta
import datetime
import config


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HELPER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def humanTimeDiff(sec):
    """
    get a human readable formating of a time difference
    https://stackoverflow.com/a/11157649/1169798
    """
    delta = relativedelta(seconds=sec)
    attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds', 'microseconds']
    return ('%02d:%02d:%02d' % (getattr(delta, 'hours'), getattr(delta, 'minutes'), getattr(delta, 'seconds')))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Process ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


table = loader.load_file()
targets = loader.load_targets()

start = datetime.datetime.now().timestamp()
ba = BaselineApproach(table, targets)
ba.exec_pipeline()

res = {}
res['cea'] = ba.generate_CEA(targets['cea'])
res['cta'] = ba.generate_CTA(targets['cta'])
res['cpa'] = ba.generate_CPA(targets['cpa'])
end = datetime.datetime.now().timestamp()
print('time taken: {}'.format(humanTimeDiff(end - start)))


print('CEA: {} / {}'.format(len(res['cea']), len(targets['cea'])))
print('CTA: {} / {}'.format(len(res['cta']), len(targets['cta'])))
print('CPA: {} / {}'.format(len(res['cpa']), len(targets['cpa'])))

missed = []
for entry in targets['cea']:
    if not any(resEntry for resEntry in res['cea'] if resEntry['col_id'] == entry['col_id'] and resEntry['row_id'] == entry['row_id']):
        missed.append({
            'col_id': entry['col_id'],
            'row_id': entry['row_id'],
            'mapped': '\033[91m[missing]\033[0m'
        })
res['cea'].extend(missed)
res['cea'] = sorted(res['cea'], key=lambda k: (k['col_id'], k['row_id']))

missed = []
for entry in targets['cta']:
    if not any(resEntry for resEntry in res['cta'] if resEntry['col_id'] == entry['col_id']):
        missed.append({
            'col_id': entry['col_id'],
            'mapped': '\033[91m[missing]\033[0m'
        })
res['cta'].extend(missed)
res['cta'] = sorted(res['cta'], key=lambda k: (k['col_id']))

missed = []
for entry in targets['cpa']:
    if not any(resEntry for resEntry in res['cpa'] if resEntry['subj_id'] == entry['sub_id'] and resEntry['obj_id'] == entry['obj_id']):
        missed.append({
            'subj_id': entry['sub_id'],
            'obj_id': entry['obj_id'],
            'mapped': '\033[91m[missing]\033[0m'
        })
res['cpa'].extend(missed)
res['cpa'] = sorted(res['cpa'], key=lambda k: (k['subj_id'], k['obj_id']))

print('\n====== Input Table ======')
ba.pipeline.pTable.printTable()

print('\n====== CEA ======')
cea = [[item['col_id'], item['row_id'], item['mapped']] for item in res['cea']]
print(tabulate(cea, headers=['col_id', 'row_id', 'mapped'], tablefmt='orgtbl'))

print('\n====== CTA ======')
cta = [[item['col_id'], item['mapped']] for item in res['cta']]
print(tabulate(cta, headers=['col_id', 'mapped'], tablefmt='orgtbl'))

print('\n====== CPA ======')
cpa = [[item['subj_id'], item['obj_id'], item['mapped']] for item in res['cpa']]
print(tabulate(cpa, headers=['subj_id', 'obj_id', 'mapped'], tablefmt='orgtbl'))

errs = ba.get_Errors()
if errs:
    print('\n\033[91m====== Errors ======\033[0m\n')
    for err in errs:
        print(err)
