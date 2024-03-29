from cells_lookup_strategies.strategy_factory import StrategyFactory
import config
import copy
from utils import util_log

from audit.const import tasks, steps


def generate(pTable, proxyService):
    """
    create the initial CEA mappings for all cells in OBJECT columns
    """
    sFact = StrategyFactory()

    # get a list of all object cells (we wont map others here)
    obj_cells = pTable.getCells(unsolved=True, onlyObj=True)
    cells = [cell for cell in obj_cells if not cell['cand']]

    # skipp if nothing remains
    if not cells:
        return False

    # get list of available priorities
    prios = sFact.getPriorities()

    # apply all strategies by priority
    for prio in prios:

        # How many cells should be solved (target changes based on the remaining from the previous strat)
        target_cells_cnt = len(cells)

        # retrieve all strategies of the current priority
        strats = sFact.getByPriority(prio)

        # run the strategies
        for strat in strats:
            util_log.info('Get mappings by strategy: {}'.format(strat.name))

            # apply the strategy
            strat.get_mappings(cells)

            # add a checkpoint
            pTable.checkPoint.addCheckPoint('cea_{}'.format(strat.name), pTable, cea=True)

            # we only keep on considering cells with no candidates so far (remaining)
            cells = [cell for cell in cells if not cell['cand']]

            # [Audit] calculate cnts for auditing
            remaining_cnt = len(cells)
            solved_cnt = target_cells_cnt - remaining_cnt

            # [Audit] get important keys only
            remaining = [pTable.audit.getSubDict(cell, ['value', 'clean_val', 'row_id', 'col_id'])
                         for cell in cells]

            # [Audit] add audit record
            pTable.audit.addRecord(tasks.CEA, steps.creation, strat.name, solved_cnt, remaining_cnt, remaining)

            # short-circuit (in case of equal priorities) if all cells have candidates
            if not cells:
                break

        # short-circuit if all cells are candidates
        if not cells:
            break

    # there might be redirects we need to resolve
    cands = [cand['uri'] for cell in obj_cells for cand in cell['cand']]
    cands = list(set(cands))
    redirects = proxyService.resolve_redirects.send([cands])
    for cell in obj_cells:
        for cand in cell['cand']:
            if cand['uri'] in redirects:
                cand['uri'] = redirects[cand['uri']][0]["redirect"]

    # there might be disambiguation pages we need to resolve
    cands = [cand['uri'] for cell in obj_cells for cand in cell['cand']]
    disambiguations = proxyService.resolve_disambiguations.send([cands])
    for cell in obj_cells:
        add_cand = []
        for cand in cell['cand']:
            if cand['uri'] in disambiguations:
                # the disambiguation targets are inserted with all the same data
                # but just have a different URI
                # label, e.g., should still match the cell value as closely as possible
                for disamb in disambiguations[cand['uri']]:
                    new_cand = copy.deepcopy(cand)
                    new_cand['uri'] = disamb['target']
                    add_cand.append(new_cand)
        cell['cand'].extend(add_cand)

    # remove duplicates from candidates
    # and augment with more data
    for cell in obj_cells:
        seen = set()
        cands = []
        for cand in cell['cand']:
            if cand['uri'] not in seen:
                uniqueCand = copy.deepcopy(cand)
                uniqueCand['col_id'] = cell['col_id']
                uniqueCand['row_id'] = cell['row_id']
                cands.append(uniqueCand)
                seen.add(cand['uri'])
        cell['cand'] = cands
    pTable.checkPoint.addCheckPoint('cea_remove_dupes', pTable, cea=True)
