import abc

from external_services.dbpedia_lookup_service import DBpedia_Lookup_Service
from external_services.wikidata_lookup_service import Wikidata_Lookup_Service
from external_services.generic_lookup_service import Generic_Lookup_Service

from config import TARGET_KG, DBPEDIA, WIKIDATA
from utils.wikidata_util import getWikiID

import utils.string_dist as sDist


class CellsStrategy(object, metaclass=abc.ABCMeta):
    def __init__(self, name, priority):
        # Set name and priority for the strategy
        self.name = name
        self.priority = priority

        # Conditional init of lookup service.
        self.GenericService = Generic_Lookup_Service()
        if TARGET_KG == DBPEDIA:
            self.LookupService = DBpedia_Lookup_Service()
        if TARGET_KG == WIKIDATA:
            self.LookupService = Wikidata_Lookup_Service()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Abstract Methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @abc.abstractmethod
    def process_cell_values(self, cell):
        """
        provide an alternative label to get candidates by
        """
        raise NotImplementedError("process_cell_values must be implemented")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Common Methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_most_similar_mappings(self, mappings, target_val, k=500):
        """ filter mappings to top-k candidates only, default = 500 """

        # shortcircuit, if there are not enough candidates anyways
        if len(mappings) <= k:
            return mappings

        # add distance to each entry
        target_val = target_val.lower()
        dist = [{
            'entry': entry,
            'dist': min(sDist.levenshtein(label.lower(), target_val) for label in entry['labels'])
        } for entry in mappings]

        # sort by distance
        dist.sort(key=lambda x: x['dist'])

        # take the first k entries
        dist = dist[:k]
        return [el['entry'] for el in dist]

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
            terms = [term for term in terms if term != cell['value']]

            # if something is left, add it to the queue
            if terms:
                for term in terms:
                    if term not in term2cell:
                        term2cell[term] = []
                    term2cell[term].append(cell)

        # short-circuit, if there is nothing to resolve
        if not term2cell:
            return

        # run the lookup service for all terms
        res = self.LookupService.look_for_lst.send([list(term2cell.keys()), None])

        # shorten the URIs
        for vals in res.values():
            for el in vals:
                el['uri'] = getWikiID(el['uri'])

        # add the results to the respective cells
        for term, cands in res.items():
            if term in term2cell:
                for cell in term2cell[term]:
                    cell['cand'].extend(cands)

        # postprocess
        for cell in cells:
            # just select the top entries
            topK = self.get_most_similar_mappings(cell['cand'], cell['value'])
            cell['cand'] = topK
