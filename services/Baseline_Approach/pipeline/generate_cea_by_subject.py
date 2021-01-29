import stringdist as sdist


def generate(pTable, endpointService):
    """
    for unmatched cells that have a matched subject cell and a given property,
    fill candidates with the corresponding property values
    """

    # get subject columns
    subj_col_ids = pTable.getSubjectCols()

    # get cells that are
    # a) object-cells
    # b) unmatched
    # c) have a corresponding, matched subject cell
    # d) the relation between both is matched
    emptyCells = [cell for cell in pTable.getCells(onlyObj=True, unsolved=True)]
    cellPairs = []
    for cell in emptyCells:

        # get corresponding subject cell
        subj_cells = pTable.getCells(row_id=cell['row_id'], col_id=subj_col_ids)

        # see, if they have a selected candidate
        for subj_cell in subj_cells:

            # skip for unmatched subject cells
            if ('sel_cand' not in subj_cell) or not subj_cell['sel_cand']:
                continue

            # get the corresponding column pair
            colPairs = pTable.getColPairs(subj_id=subj_cell['col_id'], obj_id=cell['col_id'])

            # add, if all requirements are fulfilled
            for colPair in colPairs:
                if ('sel_cand' in colPair) and colPair['sel_cand']:
                    cellPairs.append({
                        'subj': subj_cell,
                        'obj': cell,
                        'prop': colPair['sel_cand']
                    })

    # short-circuit, if we have no hits so far
    if not cellPairs:
        return False

    changed = False
    for pair in cellPairs:

        # get all properties of the subject cell
        props = endpointService.get_objects_for.send([pair['subj']['sel_cand']['uri']])
        props = props[pair['subj']['sel_cand']['uri']]

        # filter for the given property
        matches = [p['value'] for p in props if p['prop'] == pair['prop']]
        if not matches:
            continue

        # get the labels for all matches
        labels = endpointService.get_labels_for_lst.send([matches, 'en'])

        # add new candiates
        pair['obj']['cand'] = [{
            'col_id': pair['obj']['col_id'],
            'row_id': pair['obj']['row_id'],
            'labels': [label['l'] for label in labels[cand]],
            'uri': cand,
            'types': []
        } for cand in matches]
        changed = True

    return changed
