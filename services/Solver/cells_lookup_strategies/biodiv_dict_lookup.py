from utils.util import load_stop_words
from cells_lookup_strategies.strategy import *
from config import CLEAN_CELL_SEPARATOR, OBJ_COL
from utils.wikidata_util import getWikiID
from build_taxon_index import get_full_values as get_taxon_values
from build_chemical_elements_index import get_full_values as get_chemical_elements_values

class BiodivDictLookup(CellsStrategy):
    def __init__(self):
        CellsStrategy.__init__(self, name='biodiv_dict', priority=0) # fixed highest priority

    def process_cell_values(self, cell):
        # return cells that matches specific format?
        res = ''
        try:
            val = cell['clean_val']
            tmp = val.replace('.', '')
            if tmp.isalpha():
                if 3 >= len(val) >= 1:
                    res = val
                else:
                    tokens = val.split('.')
                    # 2 words value in a specific format
                    if len(tokens) == 2:
                        if len(tokens[0]) == 1 or len(tokens[0]) == 2:
                            res = val
        except AttributeError:  # if any None is found, split couldn't be applied.
            pass

        return res

    def get_mappings(self, cells):
        """
        add candidates to the given cells by using different strategies to expand the alternative labels
        """

        # first pass, collect lookup terms for cells
        term2cell = {}
        for cell in cells:

            # get modified labels
            terms = self.process_cell_values(cell)

            # if there are no matches, we dont need to proceed
            if not terms:
                continue

            # make sure we have a list here
            if isinstance(terms, str):
                terms = [terms]

            # make sure all terms are unique
            terms = list(set(terms))

            # only include new search terms that are non-empty
            terms = [term for term in terms if term.strip()]

            # only terms that are different from the original values
            # terms = [term for term in terms if term != cell['value']]

            # if something is left, add it to the queue
            if terms:
                for term in terms:
                    if term not in term2cell:
                        term2cell[term] = []
                    term2cell[term].append(cell)

        # short-circuit, if there is nothing to resolve
        if not term2cell:
            return

        # retrieve full values from the pre-dictionary/index
        res = get_taxon_values(list(term2cell.keys()))

        # append retrieved values from chemical elements as well.
        chemi = get_chemical_elements_values(list(term2cell.keys()))

        # conditional update of the res dict
        for k, val in chemi.items():
            if not res[k] and chemi[k]:
                res[k] = chemi[k]

        # add the results to the respective cells
        for term, cands in res.items():
            if term in term2cell:
                for cell in term2cell[term]:
                    cell['cand'].extend(cands)

