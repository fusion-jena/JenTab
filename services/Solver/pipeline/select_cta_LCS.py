import config
from .support_cta import support as supportCTA
from audit.const import tasks, steps, methods
from config import ONE_CTA

def select(pTable, proxyService):
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


        # short-circuit if there are no candidates
        if len(col['cand']) < 1:
            # [Audit] cols with no candidates are still remaining
            remaining.extend([col])
            continue

        # we might have calculated support in a previous step and might not.
        try:
            # get the maximum frequency
            maxFreq = max([cand['support'] for cand in col['cand']])
        except KeyError:
            # count types of each cell's candidates
            supportCTA(pTable, col_id=col['col_id'])
            # get the maximum frequency
            maxFreq = max([cand['support'] for cand in col['cand']])

        # get types with max frequency
        # our final result will be among those
        cands = [cand for cand in col['cand'] if cand['support'] == maxFreq]

        # get the hierarchy over our candidates
        hierarchy = proxyService.get_hierarchy_for_lst.send([cand['uri'] for cand in cands])

        solFound = False

        # we need the most specific from this list
        # this should be the one, with no children from the hierarchy
        # as per candidate generation, we should already have all elements of the hierarchy among our candidates
        parents = []
        for parentList in hierarchy.values():
            parents.extend([item['parent'] for item in parentList])
        parents = set(parents)

        # if we are working with types that are connected via a tree
        if len(parents) > 0:
            # filtering candidates to only those with parents (ensure we are working in a tree, no an odd type)
            cands = [c for c in cands if len(hierarchy[c['uri']]) > 0]

        # select the lowest node of the created tree
        for cand in cands:
            if cand['uri'] not in parents:
                col['sel_cand'] = cand
                # [Audit] Mark as solved
                solFound = True
                solved_cnt = solved_cnt + 1
                break

        if not ONE_CTA:
            # the result in this case is a concatenation of the entire hierarchy
            if solFound:
                col['sel_cands'] = [col['sel_cand']]
                col['sel_cands'] += [{'uri':p['parent']} for p in hierarchy[col['sel_cand']['uri']]]

        # [Audit] add to remaining if no solution found
        if not solFound:
            remaining.extend([col])

    # [Audit] calculate remaining col pairs
    remaining_cnt = target_cols_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['col_id']) for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CTA, steps.selection,
                       methods.lcs, solved_cnt, remaining_cnt, remaining)

    # if we couldnt find an LCS, this means we have a cycle in our candidates
    # TODO get distance from actual cell values and select the one with lowest average distance
    # for now delegate to select_cta_support to pick one at random
