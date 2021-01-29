
def doFilter(pTable):
    """
    for each row, see, which candidate in the subject cell matched best to the rest of the row
    remove candidates in other fields accordingly
    """

    # get subject cells
    subjColIds = pTable.getSubjectCols()
    subjCells = pTable.getCells(col_id=subjColIds, unsolved=True)

    # collect purged candidates to be removed from cell pair lists
    newPurged = []

    # filter the subject cell candidates
    for cell in subjCells:

        # skip, if only one candidate is left
        if len(cell['cand']) <= 1:
            continue

        # for each candidate get the number of matches within the row
        candMatches = {}
        for cand in cell['cand']:

            # get all matching cell pairs with candidates
            matchedCellPairs = [
                pair for pair in pTable.getCellPairs(subj_id=cell['col_id'], row_id=cell['row_id'], subj_cand=cand['uri'])
                if len(pair['cand']) > 0
            ]

            # count the number of matched columns
            # multiple matches to a cell in the same column are only counted once
            # gives a measure how good the coverage for the row actually is
            candMatches[cand['uri']] = len(set(p['obj_id'] for p in matchedCellPairs))

        # get count of best match and corresponding candidates
        bestMatchCount = max(candMatches.values())
        bestCand = [cand for cand, freq in candMatches.items() if freq == bestMatchCount]

        # remove other candidates
        newCand = []
        newPurged = []
        for cand in cell['cand']:
            if cand['uri'] in bestCand:
                newCand.append(cand)
            else:
                newPurged.append(cand)
        cell['cand'] = newCand
        cell['purged_cand'].extend(newPurged)

    # end here, if there was nothing to purge
    if not newPurged:
        return False

    # remove the cell pairs referring to purged subject-candidates
    pTable.purgeCellPairs(newPurged)

    # get all rows affected
    purgedRows = list(set(p['row_id'] for p in newPurged))

    # purge the candidates of other object cells in the table
    # that are those that are not referenced by any match to a subject-cell-candidate
    for targetCol in [col for col in pTable.getCols(onlyObj=True) if col['col_id'] not in subjColIds]:

        # look at every affected cell
        for targetCell in pTable.getCells(col_id=targetCol['col_id'], row_id=purgedRows):

            # dont remove the last candidate
            if len(targetCell['cand']) <= 1:
                continue

            # get all cell pairs that affect this target cell
            cellPairs = pTable.getCellPairs(obj_id=targetCell['col_id'], row_id=targetCell['row_id'])

            # get the candidates that are still used in some cell pair
            usedCands = set(pair['obj_cand'] for pair in cellPairs)

            # remove all candidates from the targetCell that are not used anymore
            targetCell['cand'] = [cand for cand in targetCell['cand'] if cand['uri'] in usedCands]

    # report that we changed something
    return True
