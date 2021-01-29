from pipeline.helpers.get_labels import get_filtered_label_cands


def generate(pTable, endpointService):
    """
    for cells without candidates with a corresponding selected CTA solution,
    fetch all instances of the CTA solution and try to match against the cell value
    """

    # get all cells without candidates
    cells = [cell for cell in pTable.getCells(onlyObj=True, unsolved=True) if not cell['cand']]

    # short-circuit, if there is nothing to do for us
    if not cells:
        return False

    # group cells by column
    cellsByCol = {}
    for cell in cells:
        if not cell['col_id'] in cellsByCol:
            cellsByCol[cell['col_id']] = []
        cellsByCol[cell['col_id']].append(cell)

    # process per column
    changed = False
    for colCells in cellsByCol.values():

        # get corresponding column
        col = pTable.getCol(col_id=colCells[0]['col_id'])

        # we need a selected CTA candidate
        if ('sel_cand' not in col) or not col['sel_cand']:
            continue

        # get the instances for this column's type
        instances = endpointService.get_children_for_lst.send([[col['sel_cand']['uri']]])
        instances = [el['child'] for el in instances[col['sel_cand']['uri']]]

        # get filtered labels in batch style.
        changed = changed or get_filtered_label_cands(endpointService, colCells, instances, col['sel_cand']['uri'])

    # done
    return changed
