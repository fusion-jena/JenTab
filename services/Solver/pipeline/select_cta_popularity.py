import config
from .support_cta import support as supportCTA
from audit.const import tasks, steps, methods


def select(pTable, proxyService):
    """
    choose among the remaning CTA candidates:
    - from the candidates with highest support, choose one by overall popularity
    only use this function, if all other attempts failed!
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

        # get popularity of remaining candidates
        uris = [cand['uri'] for cand in cands]

        # hack to prevent some timeouts
        for main in ['Q5', 'Q523', 'Q486972', 'Q318', 'Q16521', 'Q13442814', 'Q11173', 'Q8502']:
            if main in uris:
                col['sel_cand'] = [c for c in cands if c['uri'] == main][0]
        if col['sel_cand']:
            continue

        # fetch popularities
        popularity = proxyService.get_popularity_for_lst.send([uris])
        for cand in cands:
            if (cand['uri'] in popularity) and (len(popularity[cand['uri']]) > 0) and ('popularity' in popularity[cand['uri']][0]):
                cand['popularity'] = int(popularity[cand['uri']][0]['popularity'])
            else:
                cand['popularity'] = 0
        cands.sort(key=lambda x: x['popularity'], reverse=True)

        # pick first most popular if it is a clear winner (only one candidate is retrieved)
        if cands:
            solved_cnt = solved_cnt + 1
            col['sel_cand'] = cands[0]
        else:
            # [Audit] if no clear winner, then it still remaining
            remaining.extend([col])

    # [Audit] calculate remaining cols
    remaining_cnt = target_cols_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['col_id']) for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CTA, steps.selection,
                           methods.popularity, solved_cnt, remaining_cnt, remaining)
