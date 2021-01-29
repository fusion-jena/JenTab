import config
from audit.const import tasks, steps, methods


def generate(pTable, endpointService):
    """
    fetch types for all OBJECT cells and aggregate the types as candidates for the respective columns
    """

    # only process columns which we dont have solutions so far
    unsolved_col_ids = [col['col_id'] for col in pTable.getCols(unsolved=True)]

    # get all object cells
    obj_cells = [cell for cell in pTable.getCells(col_id=unsolved_col_ids, onlyObj=True)]

    # ~~~~~~~~~~~~~~~~~~~~~~~~ resolve types ~~~~~~~~~~~~~~~~~~~~~~~~

    # get unique list of cell candidates
    uris = [cand['uri'] for cell in obj_cells for cand in cell['cand']]
    uris = list(set(uris))

    # fetch types for those
    res = endpointService.get_ancestors_for_lst.send(uris)

    # parse results
    for cell in obj_cells:
        for cand in cell['cand']:
            if (cand['uri'] in res) and res[cand['uri']]:
                cand['types'] = [item['type'] for item in res[cand['uri']]]

    # ~~~~~~~~~~~~~~~~~~~~~~~~ aggregate types ~~~~~~~~~~~~~~~~~~~~~~~~

    # aggregate types on cell level
    for cell in obj_cells:
        types = set()
        for cand in cell['cand']:
            if 'types' in cand:
                for typeCand in cand['types']:
                    types.add(typeCand)
        cell['types'] = list(types)

    # aggregate types on col level
    cols = [col for col in pTable.getCols(col_id=unsolved_col_ids, onlyObj=True)]

    # [Audit] How many cols should be solved
    target_cols_cnt = len(cols)

    # [Audit] init solved cnt of cols
    solved_cnt = 0

    for col in cols:
        # get all cells for this column
        # support is only affected by cells that have types, empty types are noise!
        cells = [cell for cell in obj_cells if (cell['col_id'] == col['col_id']) and cell['types']]
        types = list(set([t for cell in cells for t in cell['types']]))

        # [Audit] if some types are retrieved then count as solved
        if types:
            solved_cnt = solved_cnt + 1

        # store candidates
        col['cand'] = [{
            'uri': t
        } for t in types]

    # [Audit] calculate remaining cols
    remaining_cnt = target_cols_cnt - solved_cnt

    # [Audit] filter cols on not having candidates
    remaining = [col for col in cols if not col['cand']]

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['col_id']) for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CTA, steps.creation, methods.default, solved_cnt, remaining_cnt, remaining)