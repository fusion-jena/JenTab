from inc.w2v_correction import W2VCorrection
from inc.off_the_shelf_correction import correct
import config


def get_corrected_lst(list_values, model):
    """
    Core method handle all types of auto corrections
    TODO: support cache file per auto_correct mechanisim
    :param list_values: list of strings to be corrected
    :param model: w2v model or None if disable w2v autocorrection
    :return: dict with 'auto_correct': ['fix1', 'fix2', ...]
    """
    unique_vals_dict = {}
    unique_vals = list(set(list_values))

    # too many items, so we shorten them here.
    if len(unique_vals) > config.AUTOCORRECT_MAX:
        unique_vals = unique_vals[0: config.AUTOCORRECT_MAX]

    # model based corrections
    if config.ENABLE_MODELBASED_CORRECTIONS:
        # W2V corrections
        w2vCorrect = W2VCorrection(model)
        [unique_vals_dict.update({w: w2vCorrect.correct_word(w)}) for w in unique_vals]
    elif config.ENABLE_OFF_THE_SHELF_CORRECTIONS:
        # Of-the-self auto-correction
        [unique_vals_dict.update({w: correct(w)}) for w in unique_vals]
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
