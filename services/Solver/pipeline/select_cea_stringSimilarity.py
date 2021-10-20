import config
from utils.string_util import get_most_similar
from audit.const import tasks, steps, methods


def select(pTable, purged=False, proxyService=None):
    """
    for all OBJECT cells select the candidate whose value is most similar to the original one
    ties are broken by popularity, i.e. the entity with the most incoming links
    can be executed either on the remaining candidates or the purged candidates
    """

    # get all object cells
    cells = [cell for cell in pTable.getCells(unsolved=True, onlyObj=True)]

    # [Audit] How many cells should be solved a.k.a must have sel_cand
    target_cells_cnt = len(cells)

    # [Audit] unsolved cells a.k. cells with no sel_cand
    remaining = []

    # [Audit] How many cells with modified sel_cand by this method
    solved_cnt = 0

    # get the selected candidate
    for cell in cells:

        # select the candidates to consider
        if purged:
            cands = cell['purged_cand']
        else:
            cands = cell['cand']

        # skip cells without candidates
        if not cands:
            # [Audit] cells with no candidates are still remaining!
            remaining.extend([cell])
            continue

        # if there is only one candidate, we select that one
        if len(cands) == 1:
            cell['sel_cand'] = cands[0]
            # [Audit] special case solution
            solved_cnt = solved_cnt + 1
            if purged:
                cell['cand'] = [cell['sel_cand']]
            continue

        # for all others check the string similarity
        best_match = get_most_similar(cands, cell['value'], proxyService)

        # add match to candidate
        cell['sel_cand'] = best_match

        # [Audit] if change detected then count as solved otherwise, add to remaining
        solved_cnt = solved_cnt + 1

        if purged:
            cell['cand'] = [cell['sel_cand']]

    # [Audit] calculate remaining cnt
    remaining_cnt = target_cells_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['value', 'clean_val', 'row_id', 'col_id'])
                 for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CEA, steps.selection,
                           methods.stringSimilarity, solved_cnt, remaining_cnt, remaining)
