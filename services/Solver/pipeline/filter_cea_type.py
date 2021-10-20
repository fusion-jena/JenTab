import math
from .support_cta import support as supportCTA
from audit.const import tasks, steps, methods

def doFilter(pTable, proxyService):
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
    cols = pTable.getCols(unsolved=False)

    # process each column separately
    for col in cols:

        if not col['sel_cand']:
            continue

        # check, if we have to process this column at all
        if not pTable.isTarget(col_id=col['col_id']):
            continue

        # grab all cells in this column
        cells = pTable.getCells(col_id=col['col_id'])

        beforeCount = len(cells)

        # get the hierarchy over our candidates
        hierarchy = proxyService.get_hierarchy_for_lst.send([col['sel_cand']['uri']])
        typesSupported = [col['sel_cand']['uri']]
        for parentList in hierarchy.values():
            typesSupported.extend([item['parent'] for item in parentList])
        typesSupported = list(set(typesSupported))

        # purge the candidate lists
        # for cell in cells:
        #     candSupport = {}
        #     for cand in cell['cand']:
        #         candSupport[cand['uri']] = 0
        #         try:
        #             foundTypes = [t for t in cand['types'] if t in typesSupported]
        #             candSupport[cand['uri']] += len(foundTypes)
        #         except KeyError as e:
        #             candSupport[cand['uri']] += 0
        #     # keep cands with highest support only
        #     maxFreq = max([candSupport[uri] for uri in candSupport.keys()])
        #     for cand in cell['cand']:
        #         if candSupport[cand['uri']] < maxFreq:
        #             cell['cand'].remove(cand)

        # purged = []
        # # remove all CEA candidates from the cells that are not associated with any remaining type
        for cell in cells:
            # add_purged = []
            # check if the sel_cand is semantically correct
            for cand in cell['cand']:
                try:
                    foundTypes = [t for t in cand['types'] if t in typesSupported]
                    if not foundTypes:
                        # add to purged cells
                        # add_purged.append(cand)
                        cell['cand'].remove(cand)
                except KeyError as e:
                    # print(e)
                    # add_purged.append(cand)
                    cell['cand'].remove(cand)
            # if add_purged:
            #     # update the cell
            #     cell['purged_cand'].extend(add_purged)

                # collect purged candidates
                # purged.extend(add_purged)
        # purge the cell-pair list
        # pTable.purgeCellPairs(purged)
    # done
    return changed
