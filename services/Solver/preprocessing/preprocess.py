from .clean_cells import main as CleanCells
from .type_prediciton import  main as TypePrediction
from .language_prediction import main as LanguagePrediction

from . import config
import build_taxon_index
from utils import util_log, util
import config as global_config

from os.path import realpath, join
import json

def get_batch(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]


with open(join(realpath('.'), 'biodiv', 'acronyms_dict.json'), 'r') as file:
    abbrev_tables = json.load(file)

def prepareData(work):
    """
    data preparations like cell cleaning etc.
    separate function, so it can be easily reused in createExample.py to provide debug data
    """

    # prepare our result object
    result = {
        'orientation': work['orientation'],
        'header': work['header'],
        'name': work['name'],
        'data': []
    }
    for i, col in enumerate(work['data']):
        result['data'].append({'col_id': i, 'original_cell_vals': col})

    # clean cells
    for col in result['data']:
        # init clean_cell_vals holder
        col['clean_cell_vals'] = []

        # temp holder for col['original_cell_vals']
        fixed_original = []

        # start the batch processing of generic fixes...
        for b_original_cell_vals in get_batch(col['original_cell_vals'], config.BATCH_SIZE):
            # encoding fix + data cleaning + generic Parsing for "all"
            clean_res = CleanCells.fix_cell_lst(b_original_cell_vals)

            # data cleaned + encoding fix + parsing
            col['clean_cell_vals'].extend(clean_res['clean'])

            # encoding fix  is only included
            fixed_original.extend(clean_res['fixed_original'])

        # copy full lst to the col placeholder.
        col['original_cell_vals'] = fixed_original

    util_log.info('   cleaned cell values')

    # get columns' languages
    for col in result['data']:
        lang = []
        # start the batch processing of language prediction...
        for b_vals in get_batch(col['clean_cell_vals'], config.BATCH_SIZE):
            lang.extend(LanguagePrediction.get_language_lst(b_vals))

        # aggregate lang per column
        col['lang'] = util.get_most_frequent(lang)[0]
    util_log.info('   retrieved languages')

    # get columns' types
    for col in result['data']:
        col['type'] = TypePrediction.get_type_lst(col['clean_cell_vals'])['res']
    util_log.info('   retrieved datatypes')

    # specific clean cells
    for col in result['data']:

        # data collector placeholders
        new_clean_lst = []

        # start the batch processing of specific clean cells...
        for b_vals in get_batch(col['clean_cell_vals'], config.BATCH_SIZE):
            # specific clean up per type
            # OBJECT: Autocorrect + remove special chars
            # QUANTITY: Custom parsing "137 km2 (2.3 mi)" --> 137
            clean_res = CleanCells.specific_clean_cell_lst(b_vals, col['type'])

            # collects new clean cell values in the corresponding placeholder
            new_clean_lst.extend(clean_res)

        # override clean_cell_vals with specific clean up if applied, otherwise, no change.
        col['clean_cell_vals'] = new_clean_lst

    util_log.info('   type based clean values')

    return result