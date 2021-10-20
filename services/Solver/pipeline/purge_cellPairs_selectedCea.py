def purge(pTable):
    """
    if a CEA candidate has been selected, purge all cell pairs that do not belong to this candiate
    """

    # inventorize cells with selected candidates
    selected = {}
    for cell in pTable.getCells():
        if ('sel_cand' in cell) and cell['sel_cand']:
            key = (cell['row_id'], cell['col_id'])
            selected[key] = cell['sel_cand']['uri']

    # filter the cell pair list
    newCellPairs = list(filter( lambda x: keep(x, selected), pTable.getCellPairs() ))

    # update the parsed table
    pTable.setCellPairs( newCellPairs )


def keep(pair, selected):
    """
    determine whether a cell pair shall be kept
    ie. there is no conflicting selected candidate already
    """

    # reject unselected subject
    key = (pair['row_id'], pair['subj_id'])
    if (key in selected) and (selected[key] != pair['subj_cand']):
        return False
    
    # reject unselected object
    key = (pair['row_id'], pair['obj_id'])
    if (key in selected) and (selected[key] != pair['obj_cand']):
        return False

    # anything else, we keep
    return True
