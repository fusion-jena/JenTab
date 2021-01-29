import itertools

from config import MAX_TOKENS, AllToken_priority, CLEAN_CELL_SEPARATOR
from utils.util import load_stop_words

from cells_lookup_strategies.strategy import *


class AllTokensLookup(CellsStrategy):
    def __init__(self):
        CellsStrategy.__init__(self, name='allTokens', priority=AllToken_priority)

    # Here it is all combinations style with MAX_TOKENS as a limit ...
    def process_cell_values(self, cell):
        tokens = cell['clean_val'].split(CLEAN_CELL_SEPARATOR)

        # remove stop words
        stop_words = load_stop_words()

        # unique rokens
        tokens = list(set(tokens))
        tokens = [t for t in tokens if t not in stop_words and t != ""]

        if len(tokens) > MAX_TOKENS:
            # use only the longest tokens
            tokens.sort(key=lambda x: len(x), reverse=True)
            tokens = tokens[0:MAX_TOKENS]
        res = []
        for L in range(0, len(tokens) + 1):
            for subset in itertools.combinations(tokens, L):
                if (len(subset) > 0):
                    res = res + [" ".join(subset)]
        return res
