def support(pTable, col_id=None):
    """
    (re)calculate the support of CTA candidates among the cells in the column
    - count each type only once per cell
    """

    # for which cols to do the support-calculation?
    if col_id:
        cols = pTable.getCols(col_id)
    else:
        cols = pTable.getCols(onlyObj=True)

    # process all selected columns
    for col in cols:

        # count types per cell
        typeCount = {}
        for cell in pTable.getCells(col_id=col['col_id']):

            # collect all types of this cell
            cellTypes = set()
            if cell['cand']:
                for cand in cell['cand']:
                    if 'types' in cand:
                        for t in cand['types']:
                            cellTypes.add(t)

            # add to the column type count
            for t in cellTypes:
                if t in typeCount:
                    typeCount[t] += 1
                else:
                    typeCount[t] = 1

        # append to column
        col['cand'] = [{
            'uri': t,
            'support': cnt,
        } for t, cnt in typeCount.items()]
