import config
from utils.wikidata_util import *
from utils.string_util import *
import dateutil.parser as parser
from utils import util_log

from audit.const import tasks, steps, methods


def generate(pTable, endpointService, skip_obj=False):
    """
    fetch the relation candidates for each cell's candidates in the main subject column
    """

    # get cell pairs to match
    cellPairs = pTable.getCellPairs(unsolved=True)

    # get a list of all subject candidates
    subjCands = list(set([pair['subj_cand'] for pair in cellPairs]))

    # fetch all properties of the subject candidates
    if skip_obj:
        # TODO we can skip looking for object properties here, so save one query
        subjLookup = endpointService.get_properties_for_lst.send([subjCands, 'en'])
    else:
        subjLookup = endpointService.get_properties_for_lst.send([subjCands, 'en'])

    # match all cell pairs
    for pair in cellPairs:

        # link to all properties of the current subject
        props = subjLookup[pair['subj_cand']]

        # match object columns
        if pair['type'] == config.OBJ_COL:
            pair['cand'] = [
                {'prop': getWikiID(item['prop'])}
                for item in props
                if item['value'] == pair['obj_cand']
            ]
        # match literal columns
        else:

            # get literal cell
            litCell = pTable.getCell(col_id=pair['obj_id'], row_id=pair['row_id'])

            # check vs all non-object properties
            for cand in [p for p in props if (p['datatype'] != 'IRI')]:

                # exact match
                if litCell['clean_val'] == cand['value']:
                    pair['cand'].append({'prop': getWikiID(cand['prop'])})
                    continue

                # fuzzy match
                if litCell['wikitype'] in [wikiString]:
                    # try fuzzy match of strings with edit distance with a threshold
                    if __match_fuzzy_string(cand['value'], litCell['clean_val']):
                        pair['cand'].append({'prop': getWikiID(cand['prop'])})
                elif litCell['wikitype'] in [wikiDate]:
                    # parse dates and try match
                    if __match_dates(cand['value'], litCell['clean_val']):
                        pair['cand'].append({'prop': getWikiID(cand['prop'])})
                elif litCell['wikitype'] in [wikiDecimal, wikiQuantity]:
                    # try match by margin
                    if __match_fuzzy_numbers(cand['value'], litCell['clean_val']):
                        pair['cand'].append({'prop': getWikiID(cand['prop'])})
                else:
                    raise Exception('Unkown literal datatype: {}'.format(litCell['wikitype']))

            # if we found no matches so far, try with again the KG-types
            if not pair['cand']:
                for cand in [p for p in props if (p['datatype'] != 'IRI')]:
                    if cand['datatype'] in ['string', 'langString']:
                        # try fuzzy match of strings with edit distance with a threshold
                        if __match_fuzzy_string(cand['value'], litCell['clean_val']):
                            pair['cand'].append({'prop': getWikiID(cand['prop'])})
                    elif cand['datatype'] in ['dateTime']:
                        # parse dates and try match
                        if __match_dates(cand['value'], litCell['clean_val']):
                            pair['cand'].append({'prop': getWikiID(cand['prop'])})
                    elif cand['datatype'] in ['decimal']:
                        # try match by margin
                        if __match_fuzzy_numbers(cand['value'], litCell['clean_val']):
                            pair['cand'].append({'prop': getWikiID(cand['prop'])})

        # remove duplicates from candidate list
        cands = {}
        for cand in pair['cand']:
            cands[cand['prop']] = cand
        pair['cand'] = [cand for cand in cands.values()]

    # aggregate on column level
    colPairs = pTable.getColPairs()

    # [Audit] How many col pairs should be solved
    target_colpairs_cnt = len(colPairs)

    # [Audit] count how many col pair has properties by this method (default creation)
    solved_cnt = 0

    # [Audit] actual col pairs that have no properties
    remaining = []

    for pair in colPairs:

        # get all matching cellpairs
        cellPairs = pTable.getCellPairs(obj_id=pair['obj_id'], subj_id=pair['subj_id'])

        # extract all unique properties still considered
        cands = set(cand['prop'] for p in cellPairs for cand in p['cand'])

        # [Audit] decide to put the current pair to solved or remaining
        if cands:
            solved_cnt = solved_cnt + 1
        else:
            remaining.extend([pair])

        # set on the column level
        pair['cand'] = [{'prop': p} for p in cands]

    # [Audit] calculate remaining col pairs
    remaining_cnt = target_colpairs_cnt - solved_cnt

    # [Audit] get important keys only
    remaining = [pTable.audit.getSubDict(cell, ['subj_id', 'obj_id']) for cell in remaining]

    # [Audit] add audit record
    pTable.audit.addRecord(tasks.CPA, steps.creation,
                           methods.default, solved_cnt, remaining_cnt, remaining)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Matching Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def __match_fuzzy_string(kg_val, val):
    util_log.info("String Value Found: KG Val =  {} Table Val: {}".format(kg_val, val))

    kg_val = remove_special_chars(kg_val).lower()

    val_words = parse_string(val)
    util_log.info("After Cleaning: KG Val = {} Table Val: {}".format(kg_val, ' '.join(val_words)))

    w_cnt = 0
    for w in val_words:
        w = remove_special_chars(w).lower()
        util_log.info("Found one word: {}".format(w))
        if kg_val.find(w) > -1:
            w_cnt = w_cnt + 1

    util_log.info("Matched {} words".format(w_cnt))

    if w_cnt / len(val_words) >= 0.5:  # 20% match?!
        return True
    return False


def __match_fuzzy_numbers(kg_val, val):
    util_log.info("Number Props found: kg_val: {} val: {}".format(kg_val, val))
    try:
        kg_val = float(kg_val)
        val = float(val)
        return abs(1 - (val / kg_val)) < 0.1  # 10% error margin
    except:
        return False


def __match_dates(kg_val, val):
    util_log.info("DATE Value Found: KG Val =  {} Table Val: {}".format(kg_val, val))
    try:
        d1 = parser.parse(kg_val)
        d2 = parser.parse(val)
        util_log.info("Parsed Vals: KG_Val  {} Table Val: {}".format(d1, d2))
        # Match if two dates share the same day, month and year
        if d1.day == d2.day and d1.month == d2.month and d1.year == d2.year:
            return True
    except:
        util_log.info("Failed to parse")
        return False
