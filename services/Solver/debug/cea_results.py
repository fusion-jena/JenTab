"""
print an overview over the first X rows of CEA solutions
"""

from tabulate import tabulate

def run( pTable, proxyService,
  MAX_LINES=10,
  MISSING='\033[91m[missing]\033[0m',
  EMPTY = '\033[93m[empty]\033[0m',
  gt = None
):

    # cells to show
    cells = [cell for cell in pTable.getTargets( cea=True ) if cell['row_id'] < MAX_LINES]

    # get labels for ground truth if available
    if gt:
        entities = [cell['mapped'] for cell in gt]
        labels = proxyService.get_labels_for_lst.send([list(entities), 'en'])

    # collect information
    cea = []
    for cell in cells:

        # find corresponding ground truth, if available
        gt_uri = ''
        gt_label = ''
        if gt:
            match = [el for el in gt if (el['row_id'] == cell['row_id']) and (el['col_id'] == cell['col_id'])]
            if match:
                gt_uri = match[0]['mapped']
                if gt_uri in labels:
                    try:
                        gt_label = labels[ gt_uri ][-1]['l']
                    except:
                        pass

        # select what to print
        if not cell['value']:
            cea.append( [cell['col_id'], cell['row_id'], EMPTY, gt_uri, cell['value'], '', gt_label ] )
        elif ('sel_cand' not in cell) or not cell['sel_cand']:
            cea.append( [cell['col_id'], cell['row_id'], MISSING, gt_uri, cell['value'], MISSING, gt_label ] )
        else:
            cea.append( [cell['col_id'], cell['row_id'], cell['sel_cand']['uri'], gt_uri, cell['value'], cell['sel_cand']['labels'][0] if len(cell['sel_cand']['labels']) > 0 else MISSING, gt_label ] )

    # highlight correct matches, if ground truth is available
    if gt:
        for item in cea:
            if item[2] == item[3]:
                item[2] = f"\033[92m{item[2]}\033[0m"
                item[3] = f"\033[92m{item[3]}\033[0m"
            else:
                item[2] = f"\033[91m{item[2]}\033[0m"
                item[3] = f"\033[91m{item[3]}\033[0m"

    # sort
    cea = sorted(cea, key=lambda k: (k[0], k[1]))

    # output
    print('\n====== CEA ======')
    print(tabulate(cea, headers=['col_id', 'row_id', 'mapped', 'gt', 'value', 'mapped label', 'gt label'], tablefmt='orgtbl'))
