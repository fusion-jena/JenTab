from pipeline.helpers.get_labels import get_filtered_label_cands


def generate(pTable, proxyService):
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

        # select the type(s) to look for
        if ('sel_cand' in col) and col['sel_cand']:
            # column type has already been selected
            col_types = [ col['sel_cand']['uri'] ]
        else:
            # there is still multiple options
            col_types = [ cand['uri'] for cand in col['cand'] ]

        # make sure we could collect some types
        if len( col_types ) < 1:
            continue

        # get the instances for this column's type
        instances = proxyService.get_children_for_lst.send([ col_types ])

        # properly append new, filtered candidates adding labels etc
        for type in instances.keys():
            cands = [el['child'] for el in instances[type]]
            changed = get_filtered_label_cands(proxyService, colCells, cands, type ) or changed

    # done
    return changed
