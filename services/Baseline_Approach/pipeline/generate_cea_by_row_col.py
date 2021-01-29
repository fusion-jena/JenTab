from .support_cta import support as supportCTA
from pipeline.helpers.get_labels import get_filtered_label_cands


def generate(pTable, endpointService):
    """
    for rows without candidates in subject cells,
    try to deduce candidates from the object properties in the same row and their values
    as well as the potential column headers
    -> add CEA candidates for subject columns and the respective cell_pair candidates
    """

    # get subject columns
    subj_col_ids = pTable.getSubjectCols()

    # get all subject cells without candidates
    subj_cells = [cell for cell in pTable.getCells(col_id=subj_col_ids, unsolved=True) if not cell['cand']]

    # short-circuit, if there is nothing to do for us
    if not subj_cells:
        return False

    # recalc support for all affected columns
    subj_cols = pTable.getCols(col_id=[c['col_id'] for c in subj_cells])
    supportCTA(pTable, col_id=[c['col_id'] for c in subj_cols])

    # what are the object columns
    obj_cols = [col['col_id'] for col in pTable.getCols(onlyObj=True) if col['col_id'] not in subj_col_ids]
    changed = False
    for subj_cell in subj_cells:

        # get the corresponding col object
        col = pTable.getCol(subj_cell['col_id'])

        # get a list of possible types or by their support
        if 'sel_cand' in col and col['sel_cand']:
            typeCands = [col['sel_cand']]
        else:
            typeCands = [t for t in sorted(col['cand'], key=lambda x: x['support'], reverse=True)]

        # get the object cells for this row
        obj_cells = pTable.getCells(row_id=subj_cell['row_id'], col_id=obj_cols)

        for typeCand in typeCands:

            # get the reverse matches from each object cell in this row
            supp_cand = None
            matches_per_col = {}
            for trg_cell in obj_cells:

                # candidates for this object cell
                if 'sel_cand' in trg_cell and trg_cell['sel_cand']:
                    obj_cands = [trg_cell['sel_cand']['uri']]
                else:
                    obj_cands = [cand['uri'] for cand in trg_cell['cand']] + [cand['uri'] for cand in trg_cell['purged_cand']]

                # get reverse matches for this object
                matches = endpointService.get_reverse_objects_classed_for_lst.send([list(obj_cands), typeCand['uri']])
                matches_per_col[trg_cell['col_id']] = matches

                # extract the error message, if existing
                if '__err' in matches:
                    errors = matches['__err']
                    pTable.addError(errors)
                    del matches['__err']

                # filter the candidates all columns have in common
                matched_values = set(m['parent'] for mset in matches.values() for m in mset)
                if supp_cand is None:
                    supp_cand = matched_values
                else:
                    supp_cand = supp_cand.intersection(matched_values)

                # we are passed the first column and
                # there are already no common candidates anymore,
                # so we dont have to check the remaining columns
                if not supp_cand:
                    break

            # we found no matches with this type, so continue with the next
            if not supp_cand:
                continue

            # fetch labels for all supp_cand instances
            q = list(supp_cand)

            # get filtered labels in batch style.
            changedCell = get_filtered_label_cands(endpointService, subj_cell, q)
            if not changedCell:
                continue
            changed = True

            # rehabilitate all purged candidates
            # they will be filtered again in the next step(s)
            # TODO we could already filter here, ...
            matched_cand = [c['uri'] for c in subj_cell['cand']]
            for obj_cell in obj_cells:

                # rehabilitate candidates that now have a subject
                new_cand = obj_cell['cand']
                new_purged = []
                for cand in obj_cell['purged_cand']:

                    # get parents from reverse lookup results for candidate
                    parents = [item['parent'] for item in matches_per_col[obj_cell['col_id']][cand['uri']]]

                    # does this object candidate have a corresponding subject candiate?
                    if any(sub for sub in matched_cand if sub in parents):
                        new_cand.append(cand)
                    else:
                        new_purged.append(cand)
                obj_cell['cand'] = new_cand
                obj_cell['purged_cand'] = new_purged

            # add corresponding cellpair-candidates
            pTable.initCellPairs(row_id=subj_cell['row_id'])
            for pair in pTable.getCellPairs(subj_id=subj_cell['col_id'], row_id=subj_cell['row_id']):

                # get candidate properties from reverse lookup
                if (pair['obj_id'] in matches_per_col) and (pair['obj_cand'] in matches_per_col[pair['obj_id']]):
                    for item in matches_per_col[pair['obj_id']][pair['obj_cand']]:
                        if item['parent'] == pair['subj_cand']:
                            pair['cand'].append({'prop': item['prop']})

            # we found some candidates, so we dont have to check the other types
            break

    return changed
