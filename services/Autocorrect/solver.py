from inc.w2v_correction import W2VCorrection
from inc.off_the_shelf_correction import correct
import config
import inc.cache

# cache of results
cache = inc.cache.Cache('terms', ['term'])


def get_knowns_words(list_values, model):
    VOCAB = model.index2word

    lst = []

    for word in list_values:
        words = word.split(config.CLEAN_CELL_SEPARATOR)
        unknown = [w for w in words if w not in VOCAB]
        if not unknown:
            lst.append(word)

    return {'knowns': lst}


def get_corrected_lst(list_values, model):
    """
    Core method handle all types of auto corrections
    :param list_values: list of strings to be corrected
    :param model: w2v model or None if disable w2v autocorrection
    :return: dict with 'auto_correct': ['fix1', 'fix2', ...]
    """
    unique_vals_dict = {}
    unique_vals = list(set(list_values))
    # init dict?
    for v in unique_vals:
        unique_vals_dict.update({v: v})

    # too many items, so we shorten them here.
    if len(unique_vals) > config.AUTOCORRECT_MAX:
        unique_vals = unique_vals[0: config.AUTOCORRECT_MAX]

    # check, if there is something in the cache
    cached = cache.getMany([{'term': term} for term in unique_vals])

    for r in cached['hits']:
        print("Cached autocorrect hits")
        unique_vals_dict.update({r['key']['term']: r['val'][0]})

    missed_terms = []
    # fire real requests if we have any misses
    if cached['misses']:
        # run lookups for all terms in parallel
        missed_terms = [t['term'] for t in cached['misses']]

    # Apply the actual correction on the  missed terms only
    if missed_terms:
        # model based corrections
        if config.ENABLE_MODELBASED_CORRECTIONS:
            # W2V corrections
            w2vCorrect = W2VCorrection(model)
            [unique_vals_dict.update({w: w2vCorrect.correct_word(w)}) for w in missed_terms]
        elif config.ENABLE_OFF_THE_SHELF_CORRECTIONS:
            # Of-the-self auto-correction
            [unique_vals_dict.update({w: correct(w)}) for w in missed_terms]
        elif config.ENABLE_WIKIPEDIA_CORRECTION:
            # TODO: restructure inc.wikipedia_correction and use it here
            pass
        elif config.ENABLE_WIKIDATA_BASED_CORRECTIONS:
            # TODO: restructure inc.wikidata_nearest_lbl_correction and use it here
            pass

    # expand to the original dimension
    autocorrected_lst = [unique_vals_dict[w] for w in list_values]

    return {'auto_correct': autocorrected_lst}


def get_corrected(value, model):
    res_lst = get_corrected_lst(value, model)
    return {'auto_correct': res_lst['auto_correct'][0]}
