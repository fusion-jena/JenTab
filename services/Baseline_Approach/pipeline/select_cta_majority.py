import config
from .support_cta import support as supportCTA
from audit.const import tasks, steps, methods

def select(pTable, endpointService):
    """
    choose among the remaning CTA candidates:
    - highest frequencies among cells in the column
    - lowest common subsumer in the hierarchy
    """

    # get all object columns
    cols = pTable.getCols(unsolved=True, onlyObj=True)

    # [Audit] How many cols should be solved
    target_cols_cnt = len(cols)

    # [Audit] init solved cnt of cols
    solved_cnt = 0

    # [Audit] actual col that have no sel_cand for type
    remaining = []

    for col in cols:

        # default cases: there is no choice
        if not col['cand']:
            # [Audit] cols with no candidates are still remaining
            remaining.extend([col])
            continue

        if len(col['cand']) == 1:
            # [Audit] default solution by LCS
            solved_cnt = solved_cnt + 1

            col['sel_cand'] = col['cand'][0]

        # count types of each cell's candidates
        supportCTA(pTable, col_id=col['col_id'])

        # short-circuit if there are no candidates
        if len(col['cand']) < 1:
            # [Audit] cols with no candidates are still remaining
            remaining.extend([col])
            continue

        # get the maximum frequency
        maxFreq = max([cand['support'] for cand in col['cand']])

        # get types with max frequency
        # our final result will be among those
        cands = [cand for cand in col['cand'] if cand['support'] == maxFreq]

        # pick first most frequent if it is a clear winner (only one candidate is retrieved)
        if len(cands) == 1:
            solved_cnt = solved_cnt + 1
            col['sel_cand'] = cands[0]
        else:
            # [Audit] if no clear winner, then it still remaining
            remaining.extend([col])

    # [Audit] calculate remaining col pairs
    remaining_cnt = target_cols_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['col_id']) for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CTA, steps.selection,
                       methods.majority_vote, solved_cnt, remaining_cnt, remaining)


