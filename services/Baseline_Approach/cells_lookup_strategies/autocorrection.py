from cells_lookup_strategies.strategy import *
from config import Autocorrect_priority
from external_services.autocorrect_service import Autocorrect_Service


class AutocorrectLookup(CellsStrategy):
    def __init__(self):
        CellsStrategy.__init__(self, name='autocorrection', priority=Autocorrect_priority)
        self.AutocorrectService = Autocorrect_Service()

    def process_cell_values(self, cell):
        # ask autocorrect service for this ...
        corrected_value = self.AutocorrectService.correct_cell.send([cell['clean_val']])['auto_correct']

        return corrected_value
