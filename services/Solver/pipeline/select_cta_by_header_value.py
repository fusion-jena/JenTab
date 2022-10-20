def select(pTable):
    """
    overrides the CTA by the header entity if it exists
    """

    # only process columns which we dont have solutions so far
    col_ids = [col['col_id'] for col in pTable.getCols(onlyObj=True)]

    # get all object cells - we pic the CTA solutions from them
    obj_cells = [cell for cell in pTable.getCells(col_id=col_ids, onlyObj=True) if cell['row_id'] == 0]

    # get all object columns - it should override them all
    cols = pTable.getCols(onlyObj=True)

    remaining = []

    for col in cols:
        # default cases: there is no choice
        if not col['cand']:
            # [Audit] cols with no candidates are still remaining
            remaining.extend([col])
            continue

        # TODO: Override in case of Numerical Column Only!
        # get corresponding header of the current column
        header_cand = [c for c in obj_cells if c['col_id'] == col['col_id']]
        # if the header is annotated using CEA, use it as a CTA as well.
        if header_cand[0]['sel_cand']:
            col['sel_cand'] = header_cand[0]['sel_cand']

