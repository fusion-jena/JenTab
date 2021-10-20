from utils.string_util import get_most_similar
from audit.const import tasks, steps, methods
import config


def select(pTable, proxyService):
    """
    for cells without mappings, try to find purged candidates that would have matched the column type
    """

    # get cells without candidates left
    empty_cells = pTable.getCells(unsolved=True, onlyObj=True)

    # [Audit] How many cells should be solved a.k.a must have sel_cand
    target_cells_cnt = len(empty_cells)

    # [Audit] unsolved cells a.k. cells with no sel_cand
    remaining = []

    # [Audit] How many cells with modified sel_cand by this method
    solved_cnt = 0

    for cell in empty_cells:

        # get the corresponding cta-results
        col = pTable.getCol(col_id=cell['col_id'])

        # we cant do something, if the column has not selected a candidate
        if 'sel_cand' not in col or not col['sel_cand']:
            continue

        # look for possible hits within the purged candidates
        new_cand = []
        for cand in cell['purged_cand']:
            if ('types' in cand) and (col['sel_cand']['uri'] in cand['types']):
                new_cand.append(cand)

        # select the most similar one
        if new_cand:
            cell['sel_cand'] = get_most_similar(new_cand, cell['value'], proxyService)
            # [Audit] Mark as solved
            solved_cnt = solved_cnt + 1
        else:
            # [Audit] add to remaining
            remaining.extend([cell])

    # [Audit] calculate remaining cnt
    remaining_cnt = target_cells_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['value', 'clean_val', 'row_id', 'col_id'])
                 for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CEA, steps.selection,
                           methods.missingCeaByCta, solved_cnt, remaining_cnt, remaining)
