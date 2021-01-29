from audit.const import tasks, steps, methods

def select(pTable):
    """
    choose among the remaning CPA candidates by majority vote per pair
    """

    colPairs = pTable.getColPairs(unsolved=True)

    # [Audit] How many col pairs should be solved a.k.a has a sel_cand
    target_colpairs_cnt = len(colPairs)

    # [Audit] count how many col pair got one prop by this method
    solved_cnt = 0

    # [Audit] actual col pairs that have no properties
    remaining = []

    for colPair in colPairs:

        # get all cellpairs for this col pair
        cellPairs = pTable.getCellPairs(subj_id=colPair['subj_id'], obj_id=colPair['obj_id'])

        # count the frequency of occurring properties
        propCount = countPropFrequencies(cellPairs)

        # short-circuit if there are no candidates
        if len(propCount) < 1:
            continue

        # get the maximum count
        maxFrequency = max(propCount.values())

        # flag for having a solution
        solFound = False

        # find the property with the highest count and select it
        for prop, freq in propCount.items():
            if freq == maxFrequency:
                colPair['sel_cand'] = prop

                # [Audit] mark as solved
                solFound = True
                solved_cnt = solved_cnt + 1
                break

        # [Audit] add to remaining if no solution found
        if not solFound:
            remaining.extend([colPair])

    # [Audit] calculate remaining col pairs
    remaining_cnt = target_colpairs_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['subj_id', 'obj_id']) for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CPA, steps.selection,
                           methods.majority_vote, solved_cnt, remaining_cnt, remaining)

def countPropFrequencies(pairs):
    """
    count prop of all pairs' candidates
    make sure to count each type only once per row
    """

    # aggregate per row
    perRow = {}
    for pair in pairs:
        if pair['row_id'] not in perRow:
            perRow[pair['row_id']] = set()
        if pair['cand']:
            for cand in pair['cand']:
                perRow[pair['row_id']].add(cand['prop'])

    # count
    propCount = {}
    for propSet in perRow.values():
        for prop in propSet:
            if prop not in propCount:
                propCount[prop] = 0
            propCount[prop] += 1

    return propCount
