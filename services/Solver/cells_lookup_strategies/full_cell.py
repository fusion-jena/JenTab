from cells_lookup_strategies.strategy import CellsStrategy
from config import OBJ_COL, FullCell_priority
from utils.wikidata_util import getWikiID


class FullCellLookup(CellsStrategy):
    def __init__(self):
        CellsStrategy.__init__(self, name='fullCell', priority=FullCell_priority)

    def process_cell_values(self, cell):
        raise NotImplementedError("process_cell_values not needed for FullCellLookup")

    def get_mappings(self, cells):
        """
        generate initial mappings for a given table
        """

        # grab all values in the cells of OBJECT cells
        values = [cell['clean_val'] for cell in cells if (cell['type'] == OBJ_COL) and cell['value']]

        # request matches from the lookup service
        res = self.LookupService.look_for_lst.send([values, None])

        # shorten all uris
        for mappingList in res.values():
            for el in mappingList:
                el['uri'] = getWikiID(el['uri'])

        # attach results as candidates
        for cell in cells:

            # get corresponding mappings
            mappings = res[cell['value']] if (cell['value'] in res) else []

            # This includes the encoding fix, preprocessing needs a change
            original_cell = cell['value'].replace('_', ' ')

            # Selects the nearest mapping only (expected 1 mapping)
            topK = self.get_most_similar_mappings(mappings, original_cell)

            # add as candidates
            cell['cand'].extend(topK)
