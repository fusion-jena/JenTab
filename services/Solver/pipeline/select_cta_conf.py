from audit.const import tasks, steps, methods

def select(pTable, proxyService):
    """
    select the most-fine-grained based on confidence score (parents support based selection)
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

        cands = [cand for cand in col['cand'] ]
        # get the hierarchy over our candidates
        hierarchy = proxyService.get_hierarchy_for_lst.send([cand['uri'] for cand in cands])

        # we need the most specific from this list
        # this should be the one, with no children from the hierarchy
        # as per candidate generation, we should already have all elements of the hierarchy among our candidates
        parents = []
        for parentList in hierarchy.values():
            parents.extend([item['parent'] for item in parentList])
        parents = set(parents)

        solFound = False

        # if we are working with types that are connected via a tree
        if len(parents) > 0:
            # filtering candidates to only those with parents (ensure we are working in a tree, no an odd type)
            cands = [c for c in cands if len(hierarchy[c['uri']]) > 0]

        # leaves - most fine-grained types
        # if more than one leaf, this means we have types from two different trees
        leaves = {}
        for cand in cands:
            if cand['uri'] not in parents:
                leaves[cand['uri']] = [p['parent'] for p in hierarchy[cand['uri']]]

        # calculate confidence score of each leaf, confidence score is definded by #of supported parents in the original cands
        candsUris = [cand['uri'] for cand in cands ]
        confLeaves = {}
        for leaf, parents in leaves.items():
            confLeaves[leaf] = 0
            for p in parents:
                if p in candsUris:
                    confLeaves[leaf] += 1

        # select the most confident leaf
        maxConf = max([confLeaves[leaf] for leaf in confLeaves.keys()])
        selCand = [leaf for leaf in confLeaves.keys() if confLeaves[leaf] == maxConf]
        if len(selCand) == 1:
            # [Audit] Mark as solved
            solFound = True
            col['sel_cand'] = {'uri':selCand[0]}
            solved_cnt = solved_cnt + 1
            print('conf_type FOUND')
            # break
        else:
            # select the one with most retrieved parents (mock for popularity)
            maxParentsCnt = max([len(parents) for leaf, parents in leaves.items()])
            col['sel_cand'] = [{'uri':l} for l, ps in leaves.items() if len(ps) == maxParentsCnt][0]

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

