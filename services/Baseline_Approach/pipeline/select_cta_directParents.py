import config
from .support_cta import support as supportCTA
from audit.const import tasks, steps, methods

def select(pTable, endpointService):
    """
    For columns with no selected_candidate a.k.a no solution of CTA
    1. Generate candidates for Objec_cell ==> P31 and P279 only
    2. Select column type with a majority vote on these generated candidates from step 1
    only use this function, if all other attempts failed!
    """

    # get all object columns
    cols = pTable.getCols(unsolved=True, onlyObj=True)

    # [Audit] How many cols should be solved
    target_cols_cnt = len(cols)

    # [Audit] init solved cnt of cols
    solved_cnt = 0

    # [Audit] actual col that have no sel_cand for type
    remaining = []

    for col in cols:

        # get all object cells per current column
        obj_cells = [cell for cell in pTable.getCells(col_id=col['col_id']) if (cell['type'] == config.OBJ_COL)]

        # get unique list of cell candidates
        uris = [cand['uri'] for cell in obj_cells for cand in cell['cand']]
        uris = list(set(uris))

        # fetch types for those
        res = endpointService.get_direct_types_for_lst.send(uris)

        # types per col level ...
        col_types = []
        # parse results
        for cell in obj_cells:
            for cand in cell['cand']:
                if (cand['uri'] in res) and res[cand['uri']]:
                    cand['directTypes'] = [item['type'] for item in res[cand['uri']]]

                    # Append types for column types aggregation
                    col_types.extend(cand['directTypes'])

        # aggregate types on cell level (include all candidates types)
        for cell in obj_cells:
            types = set()
            for cand in cell['cand']:
                if 'directTypes' in cand:
                    for typeCand in cand['directTypes']:
                        types.add(typeCand)
            cell['directTypes'] = list(
                types)  # cell['directTypes'] represent the key with direct parents, to keep cell['types'] for others

        # store candidates, this overrides the old candidates (doesn't harm, no further use of it - can be
        # recalculated using other cell['Types'])
        col['cand'] = [{
            'uri': t
        } for t in col_types]

        # Populates support per candidate type of that column
        supportCTA(pTable, col_id=col['col_id'])

        # short-circuit if there are no candidates
        if len(col['cand']) < 1:
            # [Audit] cols with no candidates are still remaining
            remaining.extend([col])
            continue

        # get the maximum frequency
        maxFreq = max([cand['support'] for cand in col['cand']])

        # get types with max frequency
        # our final result will be among those
        cands = [cand for cand in col['cand'] if cand['support'] == maxFreq]

        # pick first most frequent if it is a clear winner (only one candidate is retrieved)
        if len(cands) == 1:
            solved_cnt = solved_cnt + 1
            col['sel_cand'] = cands[0]
        else:
            # [Audit] if no clear winner, then it still remaining
            remaining.extend([col])

    # [Audit] calculate remaining cols
    remaining_cnt = target_cols_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['col_id']) for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CTA, steps.selection,
                           methods.directParents, solved_cnt, remaining_cnt, remaining)
