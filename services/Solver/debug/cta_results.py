'''
print an overview over the CTA solutions
'''

from tabulate import tabulate

def run( pTable, proxyService,
  MISSING='\033[91m[missing]\033[0m',
  gt = None
):

    # collect information
    cta = []
    for col in pTable.getCols( onlyObj=True ):

        # find corresponding ground truth
        gt_uri = ''
        if gt:
            match = [el for el in gt if (el['col_id'] == col['col_id'])]
            if match:
                gt_uri = match[0]['mapped']

        if ('sel_cand' not in col) or not col['sel_cand']:
            cta.append({ 'col_id': col['col_id'], 'mapped': None, 'gt': gt_uri })
        else:
            cta.append({ 'col_id': col['col_id'], 'mapped': col['sel_cand']['uri'], 'gt': gt_uri })

    # sort
    cta = sorted(cta, key=lambda k: k['col_id'])

    # get labels for CTA solutions
    entities = set(item['mapped'] for item in cta if item['mapped'])
    entities.update(item['gt'] for item in cta if item['gt'])
    labels = proxyService.get_labels_for_lst.send([list(entities), 'en'])
    for item in cta:
        item['label'] = labels[item['mapped']][-1]['l'] if item['mapped'] in labels else MISSING
        item['gt_label'] = labels[item['gt']][-1]['l'] if (item['gt'] in labels) and labels[item['gt']] else ''

    # highlight correct matches, if ground truth is available
    if gt:
        for item in cta:
            if item['mapped'] == item['gt']:
                item['mapped'] = f"\033[92m{item['mapped']}\033[0m"
                item['gt'] = f"\033[92m{item['gt']}\033[0m"
            else:
                item['mapped'] = f"\033[91m{item['mapped']}\033[0m"
                item['gt'] = f"\033[91m{item['gt']}\033[0m"

    # output
    print('\n====== CTA ======')
    cta = [[
      item['col_id'],
      item['mapped'],
      item['label'],
      item['gt'],
      item['gt_label'],
    ] for item in cta]
    print(tabulate(cta, headers=['col_id', 'mapped', 'label', 'gt', 'gt_label'], tablefmt='orgtbl'))
