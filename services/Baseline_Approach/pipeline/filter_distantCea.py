import config
import utils.string_dist as sDist


# threshold for the normalized Levenshtein distance; 0 is for identical strings
# pairs above that will be purged
UNRELATED_THRESHOLD = 0.5


def isDistant(base, labels):
    """
    compare list of labels against the base label to check
    whether at least one label is close enough wrt string distance
    """
    for label in labels:
        if label and sDist.levenshtein_norm(base, label.lower()) < UNRELATED_THRESHOLD:
            return False
    return True


def doFilter(pTable):
    """
    remove all cell candidates and corresponding cell pairs that are too far away from their respective cell values
    """

    # get all object cells
    obj_cells = pTable.getCells(unsolved=True, onlyObj=True)

    # purge the candidate lists
    purged = []
    for cell in obj_cells:

        # filter the candidate list
        new_cand = []
        add_purged = []
        for cand in cell['cand']:
            if isDistant(cell['value'].lower(), cand['labels']):
                add_purged.append(cand)
            else:
                new_cand.append(cand)

        if add_purged:
            # update the cell
            cell['cand'] = new_cand
            cell['purged_cand'].extend(add_purged)

            # collect purged candidates
            purged.extend(add_purged)

    # purge the cell-pair list
    pTable.purgeCellPairs(purged)

    # report whether we did something here
    return len(purged) > 0
