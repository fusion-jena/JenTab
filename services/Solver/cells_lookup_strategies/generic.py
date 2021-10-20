from cells_lookup_strategies.strategy import CellsStrategy
import config
from utils.wikidata_util import getWikiID


class GenericLookup(CellsStrategy):
    def __init__(self):
        CellsStrategy.__init__(self, name='genericLookup', priority=config.Generic_priority)

    def process_cell_values(self, cell):
        raise NotImplementedError("process_cell_values not needed for GenericLookup")

    def get_mappings(self, cells):
        """
        generate initial mappings for a given table
        """

        # grab all values in the cells of OBJECT cells
        # only unique values required (save on request size)
        values = [cell['value'] for cell in cells if (cell['type'] == config.OBJ_COL)]
        values = list(set(values))

        # request matches from the lookup service
        res = self.GenericService.look_for_lst.send([values])

        # select topK closest matches for each value
        for key in res.keys():
            # This includes the encoding fix, preprocessing needs a change
            original_cell = key.replace('_', ' ')
            # selects the nearest mapping only
            res[key] = self.get_most_similar_mappings(res[key], original_cell)

        # shorten all uris
        for mappingList in res.values():
            for el in mappingList:
                el['uri'] = getWikiID(el['uri'])

        # attach results as candidates
        for cell in cells:

            # get corresponding mappings
            mappings = res[cell['value']] if (cell['value'] in res) else []

            # add as candidates
            cell['cand'].extend(mappings)
