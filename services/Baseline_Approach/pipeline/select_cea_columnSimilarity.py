import config
import copy
import utils.string_dist as sDist
from audit.const import tasks, steps, methods

# how similar do two values have to be, to be considered equal?; 0 is identical
EQUALITY_THRESHOLD = 0.1


def select(pTable):
    """
    for unmatched object cells: look for similar values within the same column
    """

    # get all object cells
    cells = [cell for cell in pTable.getCells(onlyObj=True, unsolved=True)]

    # [Audit] How many cells should be solved a.k.a must have sel_cand
    target_cells_cnt = len(cells)

    # [Audit] unsolved cells a.k. cells with no sel_cand
    remaining = []

    # [Audit] How many cells with modified sel_cand by this method
    solved_cnt = 0

    # get the selected candidate
    for cell in cells:

        # get all cells of that column
        col_cells = pTable.getCells(col_id=cell['col_id'])

        sel_cand_changed = False

        # find similar ones
        for col_cell in col_cells:

            # if there is not a match either, we can skip
            if ('sel_cand' not in col_cell) or not col_cell['sel_cand']:
                continue

            # compare the labels
            if sDist.levenshtein_norm(col_cell['value'].lower(), cell['value'].lower()) <= EQUALITY_THRESHOLD:
                cell['sel_cand'] = copy.deepcopy(col_cell['sel_cand'])

                # [Audit] change detected
                sel_cand_changed = True

                cell['sel_cand']['row_id'] = cell['row_id']
                cell['sel_cand']['col_id'] = cell['col_id']
                cell['cand'].append(cell['sel_cand'])

        # [Audit] count one solved if any col_cell succeeded in changing the sel_cand
        if sel_cand_changed:
            solved_cnt = solved_cnt + 1
        else:
            remaining.extend([cell])

    # [Audit] calculate remaining cnt
    remaining_cnt = target_cells_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['value', 'clean_val', 'row_id', 'col_id'])
                 for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CEA, steps.selection,
                           methods.colSimilarity, solved_cnt, remaining_cnt, remaining)
