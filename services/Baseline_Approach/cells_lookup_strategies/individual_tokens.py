from utils.util import load_stop_words
from cells_lookup_strategies.strategy import *
from config import Token_priority, CLEAN_CELL_SEPARATOR

class IndividualTokensLookup(CellsStrategy):
    def __init__(self):
        CellsStrategy.__init__(self, name='tokens', priority=Token_priority)

    # Here it gets distinct words from the clean cell val.
    def process_cell_values(self, cell):
        tokens = cell['clean_val'].split(CLEAN_CELL_SEPARATOR)
        # remove stop words
        stop_words = load_stop_words()
        # unique tokens
        tokens = list(set(tokens))
        tokens = [t for t in tokens if t not in stop_words and t != ""]

        return tokens
