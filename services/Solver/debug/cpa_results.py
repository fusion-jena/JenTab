'''
print an overview over the CPA solutions
'''

from tabulate import tabulate

def run( pTable, proxyService,
  MISSING='\033[91m[missing]\033[0m',
):

    # collect information
    cpa = []
    for pair in pTable.getColPairs():
        if ('sel_cand' not in pair) or not pair['sel_cand']:
            cpa.append({ 'subj_id': pair['subj_id'], 'obj_id': pair['obj_id'], 'mapped': None })
        else:
            cpa.append({ 'subj_id': pair['subj_id'], 'obj_id': pair['obj_id'], 'mapped': pair['sel_cand'] })

    # sort
    cpa = sorted(cpa, key=lambda k: (k['subj_id'], k['obj_id']) )

    # get labels for cpa solutions
    enitities = set(item['mapped'] for item in cpa if item['mapped'])
    labels = proxyService.get_labels_for_lst.send([list(enitities), 'en'])

    # output
    print('\n====== CPA ======')
    cpa = [[
      item['subj_id'],
      item['obj_id'],
      item['mapped'],
      labels[item['mapped']][0]['l'] if item['mapped'] in labels else MISSING
    ] for item in cpa]
    print(tabulate(cpa, headers=['subj_id', 'obj_id', 'mapped', 'label'], tablefmt='orgtbl'))
