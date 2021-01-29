import math
from .support_cta import support as supportCTA
from audit.const import tasks, steps, methods

def doFilter(pTable, minSupport=0.5):
    """
    filter candidates by column header candidates
    - column headers are kept, if they support at least (minSupport * #rows) many cells
    - only filter for columns that are part of the targets (if activated)

    subsequently remove:
    - CTA candidates with less support
    - CEA candidates that do not support any of the remaining CTA candidates of their column
    """

    # keep track, if this changed anything
    changed = False

    # table cols
    cols = pTable.getCols(unsolved=True)

    # [Audit] How many cols should be solved
    target_cols_cnt = len(cols)

    # [Audit] count how many cols are changes (solved by this method)
    solved_cnt = 0

    # [Audit] actual columns that are not changed
    remaining = []

    # process each column separately
    for col in cols:

        # check, if we have to process this column at all
        if not pTable.isTarget(col_id=col['col_id']):
            continue

        # grab all cells in this column
        cells = pTable.getCells(col_id=col['col_id'])

        # count types of each cell's candidates
        beforeCount = len(col['cand'])
        supportCTA(pTable, col_id=col['col_id'])

        # minimum count for a type to be kept
        minCount = math.trunc(len(cells) * minSupport)

        # remove all type from column with less than minCount occurrences
        col['cand'] = [cand for cand in col['cand'] if cand['support'] >= minCount]

        # only proceed, if we removed something
        if beforeCount != len(col['cand']):
            changed = True

            # increment solved columns
            solved_cnt = solved_cnt + 1

            # still supported types
            typesSupported = [cand['uri'] for cand in col['cand']]

            # remove all CEA candidates from the cells that are not associated with any remaining type
            for cell in cells:

                # do not remove the last candidate
                if len(cell['cand']) <= 1:
                    continue

                # calc the new candidates
                newCands = [
                    cand for cand in cell['cand']
                    if ('types' in cand) and any([t for t in cand['types'] if t in typesSupported])
                ]

                # only use the new candidates, if this leaves some candidates
                if len(newCands) >= 1:
                    cell['cand'] = newCands
        else:
            # [Audit] if unchanged col then it is still remaining
            remaining.extend([col])

    # [Audit] calculate remaining cols
    remaining_cnt = target_cols_cnt - solved_cnt

    # # [Audit] add audit record
    # pTable.audit.addRecord(tasks.CTA, steps.filteration,
    #                        methods.majority_vote, solved_cnt, remaining_cnt, remaining)
    # done
    return changed
