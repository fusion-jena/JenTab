def override_cands(pTable):
    # get a list of all object cells (we wont map others here)
    obj_cells = pTable.getCells(unsolved=False, onlyObj=True)

    # cells that have sel_cand
    cells = [cell for cell in obj_cells if  cell['sel_cand']]

    for cell in cells:
        cell['cand'] = [cell['sel_cand']]
