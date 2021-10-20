from .generate_cea import generate as generate_cea
from .generate_cta import generate as generate_cta

from .filter_colHeader import doFilter as filter_colHeader
from .filter_cea_type import doFilter as filter_cea_type

from .select_cea_stringSimilarity import select as select_cea_stringSimilarity
from .select_cea_columnSimilarity import select as select_cea_columnSimilarity
from .select_cta_conf import select as select_cta_conf
from .select_cta_LCS import select as select_cta_LCS
from .select_cta_majority import select as select_cta_majority

from external_services.wikidata_proxy_service import Wikidata_Proxy_Service
from external_services.autocorrect_service import Autocorrect_Service

from utils import util_log
import utils.table
from utils import res_IO
import utils.string_dist as sDist


class Pipeline():
    """"
    Same idea of compact pipeline by it solves against a refernce table
    Reference table is suppose to be the subset of correctly spelled word and it inherets the structure of the table
    """

    def __init__(self, table, targets):
        util_log.init('baseline.log')

        # Conditional init of endpoint service.
        self.proxyService = Wikidata_Proxy_Service()

        # memorize the table name
        self.table_name = table['name']

        # parse the raw table structure into something meaningful
        self.table = table
        self.pTable = utils.table.ParsedTable(table, targets)

        # reference table

        # initial version of the refTable
        self.refTable = utils.table.ParsedTable(table, targets)

        self.AutocorrectService = Autocorrect_Service()
        # modify the refrence Table
        self.refTable = self.create_ref_table(self.refTable, self.AutocorrectService)



    def run(self):
        try:
            # initialize CEA candidates
            generate_cea(self.refTable, self.proxyService)

            # infer column types for object-columns
            generate_cta(self.refTable, self.proxyService)

            # filter CTA and CEA candidates by support
            filter_colHeader(self.refTable, minSupport=0.5)

            select_cta_conf(self.pTable, self.proxyService)
            # select_cta_LCS(self.refTable, self.proxyService)
            select_cta_majority(self.pTable, self.proxyService)
            # filter cea with no semantic type support
            filter_cea_type(self.refTable, self.proxyService)

            # selected candidates (preliminary solutions)
            select_cea_stringSimilarity(self.refTable, proxyService=self.proxyService)
            select_cea_columnSimilarity(self.refTable)

            # map solution in the ref_table to parsedTable
            self.map_solution(self.refTable, self.pTable)

            # Place the result on the desk
            res_IO.set_res(self.table_name, self.get_results())

            # return pTable object
            return self.pTable

        except Exception as ex:
            raise ex

    # ~~~~~~~~~~~~~~~~~~~~~~~~  Reference Table ~~~~~~~~~~~~~~~~~~
    def create_ref_table(self, table, autocorrect_service):
        # modify original_values of this table and create new instance of it.

        refTable = table

        # get a list of all object cols (we wont map others here)
        cols = refTable.getCols(unsolved=False, onlyObj=True)
        # process each column separately
        for col in cols:
            # grab all cells in this column
            cells = refTable.getCells(col_id=col['col_id'])
            vals = [v['value'] for v in cells]

            # dummy implementation would be take the first 3 or 2 elements of each column
            # correctSpell = vals[0:3]
            correctSpell = autocorrect_service.get_knowns.send(vals)['knowns']
            # correctSpell = res

            if correctSpell:
                # include those too far values from correctSpell, we give another chance by the pipeline to solve
                toInclude = correctSpell
                for v in vals:
                    similar = list(set([v  for x in toInclude if sDist.levenshtein_norm(v.lower(), x.lower()) < 0.4]))
                    if not similar:
                        toInclude.append(v)
                noise = [c for c in cells if c['value'] not in toInclude]
                refTable.removeCells(noise)

        return refTable

    def map_solution(self, refTable, pTable):
        """"
        it maps solutions from the refrenceTable to the original pTable
        """
        # get a list of all object cols (we wont map others here)
        cols = pTable.getCols(unsolved=False, onlyObj=True)
        # process each column separately
        for col in cols:
            # grab all cells in this column
            cells = pTable.getCells(col_id=col['col_id'])
            # get refCells
            refCells = refTable.getCells(col_id=col['col_id'])

            for cell in cells:
                dist = [(sDist.levenshtein_norm(cell['value'].lower(), refCell['value'].lower()), refCell['value'])
                        for refCell in refCells]

                # select the correct refV ==> min dist
                minDist = min([d[0] for d in dist])
                minRefV = [d[1] for d in dist if d[0] == minDist][0]

                # pick ref solution
                sel_cand = [c['sel_cand'] for c in refCells if c['value'] == minRefV][0]

                # CEA solution
                # we should select the solution of the closest match directly here
                cell['sel_cand'] = sel_cand

            # pick the CTA solution here
            col['sel_cand'] = refTable.getCols(col_id=col['col_id'])[0]['sel_cand']

            # TODO: pick CPA solution

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Utils ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_CEA(self):
        result = []
        for cell in self.pTable.getTargets(cea=True):
            if ('sel_cand' in cell) and cell['sel_cand']:
                result.append({
                    'col_id': cell['col_id'],
                    'row_id': cell['row_id'],
                    'mapped': cell['sel_cand']['uri']
                })
            elif ('cand' in cell) and cell['cand']:
                result.append({
                    'col_id': cell['col_id'],
                    'row_id': cell['row_id'],
                    'mapped': cell['cand'][0]['uri']
                })
        return result

    def get_CTA(self):
        result = []
        for col in self.pTable.getTargets(cta=True):
            if ('sel_cand' in col) and col['sel_cand']:
                result.append({
                    'col_id': col['col_id'],
                    'mapped': col['sel_cand']['uri']
                })
        return result

    def get_CPA(self):
        result = []
        for pair in self.pTable.getTargets(cpa=True):
            if ('sel_cand' in pair) and pair['sel_cand']:
                result.append({
                    'subj_id': pair['subj_id'],
                    'obj_id': pair['obj_id'],
                    'mapped': pair['sel_cand'],
                })
        return result

    def get_Errors(self):
        return self.pTable.getErrors()

    def get_AuditRecords(self):
        return self.pTable.audit.getRecords()

    def get_CheckPoints(self):
        return self.pTable.checkPoint.getCheckPoints()

    # ~~~~~~~~~~~~~~~~~~~~~ Results ~~~~~~~~~~~~~~~~~

    def get_results(self):
        """
        Wrap up every single part of the res dict
        """
        res = {
            'cea': self.get_CEA(),
            'cta': self.get_CTA(),
            'cpa': self.get_CPA(),
            'errors': self.get_Errors(),
            'audit': self.get_AuditRecords(),
            'checkpoints': self.get_CheckPoints()}
        return res
