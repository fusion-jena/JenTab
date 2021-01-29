from config import LABELS_FOR_BATCH_SIZE
import utils.string_dist as sDist


def get_batch(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]


def get_filtered_label_cands(endpointService, cells, instances, colType=None):
    """
    filter a list of candidates by their string similarity to cell values
    * runs in batched mode - fetching labels in chunks and not all at once
    * works for multiple cells, if they share the same candidates
    """
    # all filtered candidates across children instances batches.

    # make sure we have an array parameter
    if not isinstance(cells, list):
        cells = [cells]

    # short circuit: single cell, single candidate
    # always use that
    if len(cells) == 1 and len(instances) == 1:
        labels = endpointService.get_labels_for_lst.send([instances, "en"])
        cells[0]['cand'].append({
            'col_id': cells[0]['col_id'],
            'row_id': cells[0]['row_id'],
            'labels': [item['l'] for item in labels[instances[0]]],
            'uri': instances[0],
            'types': [colType] if colType is not None else [],
        })

    # unique values from cells
    # we dont need to repeat the comparisons for them. we can not distinguish them by label, anyhow
    unique_cells = {}
    for cell in cells:
        if cell['value'] not in unique_cells:
            unique_cells[cell['value']] = []
        unique_cells[cell['value']].append(cell)

    # process in batches
    changed = False
    for batch_q in get_batch(instances, LABELS_FOR_BATCH_SIZE):

        labels = endpointService.get_labels_for_lst.send([batch_q, "en"])

        # current entries (child + labels) per batch
        entries = [{'uri': qi, 'labels': [el['l'] for el in labels[qi]]} for qi in batch_q if qi in labels]

        # select as candidates those that are close enough to the cell value for current batch
        for cellset in unique_cells.values():
            batch_cands = filterCandidates(cellset[0], entries)

            if batch_cands:
                changed = True
                # add the candidate to all cells in this set
                for cell in cellset:
                    cell['cand'].extend({
                        'col_id': cell['col_id'],
                        'row_id': cell['row_id'],
                        'labels': c['labels'],
                        'uri': c['uri'],
                        'types': [colType] if colType is not None else [],
                    } for c in batch_cands)

    return changed


def filterCandidates(cell, cands):
    """
    select all candidates reasonably close (string distance) to the cell value
    """

    result = []
    cellVal = cell['value'].lower()
    for cand in cands:
        if any(
                label for label in cand['labels']
                if (sDist.levenshtein_norm(cellVal, label.lower()) <= 0.1)
            or (sDist.levenshtein(cellVal, label.lower()) <= 3)
        ):
            result.append(cand)
    return result
