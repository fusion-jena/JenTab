import utils.string_dist as sDist


def generate(pTable, proxyService):
    """
    for rows without candidates in subject cells,
    try to deduce candidates from the object properties in the same row
    -> add CEA candidates for subject columns and the respective cell_pair candidates
    """

    # get subject columns
    subj_col_ids = pTable.getSubjectCols()

    # get all subject cells without candidates
    subj_cells = [cell for cell in pTable.getCells(col_id=subj_col_ids, unsolved=True) if not cell['cand']]

    # short-circuit, if there is nothing to do for us
    if not subj_cells:
        return False

    # collect all object candidates in the respective rows (without the subject column)
    obj_cands = set()
    obj_cols = [col['col_id'] for col in pTable.getCols(onlyObj=True) if col['col_id'] not in subj_col_ids]
    for subj_cell in subj_cells:

        # get object cells in this row
        obj_cells = pTable.getCells(row_id=subj_cell['row_id'], col_id=obj_cols)

        # collect all purged candidates
        # main candidates remain for those rows, where the subject column has no match
        for obj_cell in obj_cells:
            obj_cands.update([cand['uri'] for cand in obj_cell['purged_cand']])
            obj_cands.update([cand['uri'] for cand in obj_cell['cand']])

    # short-circuit, if there is nothing to do for us
    if not obj_cands:
        return False

    # reverse resolve the object candidates
    # aka "which subjects point to those objects?"
    lookup = proxyService.get_reverse_objects_for_lst.send([list(obj_cands)])

    # collect candidates supported by the remainder of the row
    subj_2_cand = {}
    for subj_cell in subj_cells:

        # get object cells in this row
        obj_cells = pTable.getCells(row_id=subj_cell['row_id'], col_id=obj_cols)

        # candidates should have a corresponding candidate in each object cell
        key = f"{subj_cell['row_id']},{subj_cell['col_id']}"
        subj_2_cand[key] = []
        firstHit = True
        for obj_cell in obj_cells:

            # get all subject candidates supported by any candidate of this object cell
            supp_cand = set()
            for obj_cand in obj_cell['purged_cand'] + obj_cell['cand']:
                if obj_cand['uri'] in lookup:
                    supp_cand.update([item['parent'] for item in lookup[obj_cand['uri']]])

            # need to be supported by all object columns
            if supp_cand:
                if firstHit:
                    subj_2_cand[key] = supp_cand
                    firstHit = False
                else:
                    subj_2_cand[key] = supp_cand.intersection(subj_2_cand[key])

    # label-lookup for all potential subject candidates
    allCandidates = [cand for cands in subj_2_cand.values() for cand in cands]
    labels = proxyService.get_labels_for_lst.send([allCandidates, "en"])
    labelLookup = {}
    for base, entry in labels.items():
        labelLookup[base] = [el['l'] for el in entry]

    # match the correct candidates
    changed = False
    for subj_cell in subj_cells:

        # get object cells in this row
        obj_cells = pTable.getCells(row_id=subj_cell['row_id'], col_id=obj_cols)

        # get the supported candidates
        key = f"{subj_cell['row_id']},{subj_cell['col_id']}"
        subj_cand = subj_2_cand[key]

        # filter potential candidates by string similarity to the subject column label
        subj_cand = filterCandidateLabel(subj_cell, subj_cand, labelLookup)
        if not subj_cand:
            continue
        changed = True

        # add all remaining candidates to the subject cell
        subj_cell['cand'] = [{
            'col_id': subj_cell['col_id'],
            'row_id': subj_cell['row_id'],
            'labels': labelLookup[cand],
            'uri': cand,
            'types': []
        } for cand in subj_cand]

        # rehabilitate all purged candidates
        # they will be filtered again in the next step(s)
        # TODO we could already filter here, ...
        for obj_cell in obj_cells:

            # rehabilitate candidates that now have a subject
            new_cand = obj_cell['cand']
            new_purged = []
            for cand in obj_cell['purged_cand']:

                # get parents from reverse lookup results for candidate
                parents = [item['parent'] for item in lookup[cand['uri']]]

                # does this object candidate have a corresponding subject candiate?
                if any(sub for sub in subj_cand if sub in parents):
                    new_cand.append(cand)
                else:
                    new_purged.append(cand)
            obj_cell['cand'] = new_cand
            obj_cell['purged_cand'] = new_purged

        # add corresponding cellpair-candidates
        pTable.initCellPairs(row_id=subj_cell['row_id'])
        for pair in pTable.getCellPairs(subj_id=subj_cell['col_id'], row_id=subj_cell['row_id']):

            # get candidate properties from reverse lookup
            if pair['obj_cand'] in lookup:
                for item in lookup[pair['obj_cand']]:
                    if item['parent'] == pair['subj_cand']:
                        pair['cand'].append({'prop': item['prop']})

    return changed


def filterCandidateLabel(cell, cands, labelLookup):
    """
    filter the list of candidates by their string similarity to the cell's label(s)
    """

    result = []
    cellVal = cell['value'].lower()
    for cand in cands:
        if any(
            label for label in labelLookup[cand]
            if (sDist.levenshtein_norm(cellVal, label.lower()) <= 0.1)
            or (sDist.levenshtein(cellVal, label.lower()) <= 3)
        ):
            result.append(cand)
    return result
