def doFilter(pTable):
    """
    remove all cell candidates and corresponding cell pairs that have no CPA candidate
    """

    # get a list of all cell candidates that have at least one candidate in at least one cell pair
    mappedCands = {}
    for pair in pTable.getCellPairs():
        subjKey = (pair['subj_id'], pair['row_id'])
        objKey = (pair['obj_id'], pair['row_id'])
        if subjKey not in mappedCands:
            mappedCands[subjKey] = set()
        if objKey not in mappedCands:
            mappedCands[objKey] = set()
        if len(pair['cand']) > 0:
            mappedCands[subjKey].add(pair['subj_cand'])
            mappedCands[objKey].add(pair['obj_cand'])

    # get a list of object columns
    obj_cols = pTable.getCols(onlyObj=True, unsolved=True)

    # purge the candidate lists
    purged = []
    for col in obj_cols:
        for cell in pTable.getCells(col_id=col['col_id']):

            # skip, if we couldnt match anything
            key = (col['col_id'], cell['row_id'])
            if key not in mappedCands:
                continue

            # memorize those purged
            add_purged = [
                cand
                for cand in cell['cand']
                if (cand['uri'] not in mappedCands[key])
            ]
            cell['purged_cand'].extend(add_purged)
            purged.extend(add_purged)

            # purge from candidate list
            cell['cand'] = [
                cand for cand in cell['cand']
                if (cand['uri'] in mappedCands[key])
            ]

    # purge the cell-pair list
    pTable.purgeCellPairs(purged)

    # report whether we did something here
    return len(purged) > 0
