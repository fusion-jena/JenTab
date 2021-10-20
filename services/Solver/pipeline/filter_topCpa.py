from .support_cta import support as supportCTA

def doFilter(pTable):
    """
    determine which subject-candidates match their rows best (== have candidates for most CPA targets)
    only keep those subject-candidates that satisfy at least one of the following:
    * tie in the count of matching cells in their row
    * share a type with one of the top matches
    * is connected to a subject-candidate of another subject-column (NOT IMPLEMENTED)
    also remove all other candidates that are not connected to one of the chosen subject-candidates
    """
    # TODO currently assumes a single subject-column; needs to be adapted to multiple subject columns
    # TODO we could actually remove candidates from other object columns as well

    # get a list of all cell candidates that have at least one candidate in at least one cell pair
    supportCount = {}
    for pair in pTable.getCellPairs():
        key = (pair['subj_id'], pair['row_id'], pair['subj_cand'])
        if len(pair['cand']) > 0:
            if key not in supportCount:
                supportCount[key] = 0
            supportCount[key] += 1

    # maximum support
    supports = supportCount.values()
    if not supports:
        return False
    maxSupport = max(supportCount.values())

    # short-circuit if the situation is dire anyhow
    if maxSupport < 1:
        return False

    # collect candidates with max support
    maxSupportEntries = {}
    for key, support in supportCount.items():
        if support >= maxSupport:
            if key[0] not in maxSupportEntries:
                maxSupportEntries[ key[0] ] = {}
            if key[1] not in maxSupportEntries[ key[0] ]:
                maxSupportEntries[ key[0] ][ key[1] ] = set()
            maxSupportEntries[ key[0] ][ key[1] ].add( key[2] )

    # cells in subject columns
    subj_cells = pTable.getCells( col_id=pTable.getSubjectCols() )

    # determine types corresponding to maximum support candidates
    maxSupportTypes = set()
    for cell in subj_cells:
        if (cell['col_id'] in maxSupportEntries) and (cell['row_id'] in maxSupportEntries[ cell['col_id'] ] ):
            supportedCands = maxSupportEntries[ cell['col_id'] ][ cell['row_id'] ]
            for cand in cell['cand']:
                if (cand['uri'] in supportedCands) and ('types' in cand) and cand['types']:
                    maxSupportTypes.update(type for type in cand['types'])

    # filter subject cells accordingly
    purged = []
    for cell in subj_cells:

        # evaluate candidates
        new_cand = []
        purged_cand = []
        for cand in cell['cand']:

            # supported type
            if ('types' in cand) and any( t for t in cand['types'] if t in maxSupportTypes ):
                new_cand.append( cand )
                continue

            # max support by itself
            if (cell['col_id'] in maxSupportEntries) and (cell['row_id'] in maxSupportEntries[ cell['col_id'] ] ) and (cand['uri'] in maxSupportEntries[ cell['col_id'] ][ cell['row_id'] ]):
                new_cand.append( cand )
                continue

            # unsupported candidate
            purged_cand.append( cand )

        # update cell
        cell['cand'] = new_cand
        cell['purged_cand'].extend( purged_cand )

        # collect purged candidates overall
        purged.extend( purged_cand )

    # purge the cell-pair list
    pTable.purgeCellPairs(purged)

    # update CTA support
    supportCTA( pTable )

    # report whether we did something here
    return len(purged) > 0
