from .generate_cea import generate as generate_cea
from .generate_cta import generate as generate_cta

from .filter_colHeader import doFilter as filter_colHeader
from .filter_cea_type import doFilter as filter_cea_type

from .select_cea_stringSimilarity import select as select_cea_stringSimilarity
from .select_cea_columnSimilarity import select as select_cea_columnSimilarity
from .select_cta_conf import select as select_cta_conf
from .select_cta_LCS import select as select_cta_LCS

from external_services.wikidata_proxy_service import Wikidata_Proxy_Service

from utils import util_log
import utils.table
from utils import res_IO

from config import TARGET_KG, DBPEDIA, WIKIDATA
if TARGET_KG == WIKIDATA:
    from utils.wikidata_index import index
if TARGET_KG == DBPEDIA:
    from utils.dbpedia_index import index

class Pipeline():
    def __init__(self, table, targets):
        util_log.init('baseline.log')

        # Conditional init of endpoint service.
        self.proxyService = Wikidata_Proxy_Service()

        # memorize the table name
        self.table_name = table['name']

        # parse the raw table structure into something meaningful
        self.table = table
        self.pTable = utils.table.ParsedTable(table, targets)

    def run(self):
        try:
            # initialize CEA candidates
            generate_cea(self.pTable, self.proxyService)

            # override by index
            #self.override_indexed_cells(self.pTable, index)

            # infer column types for object-columns
            generate_cta(self.pTable, self.proxyService)

            # filter CTA and CEA candidates by support
            filter_colHeader(self.pTable, minSupport=0.7)

            # select_cta_conf(self.pTable, self.proxyService)
            select_cta_LCS(self.pTable, self.proxyService)
            # filter cea with no semantic type support
            filter_cea_type(self.pTable, self.proxyService)

            # selected candidates (preliminary solutions)
            select_cea_stringSimilarity(self.pTable, proxyService=self.proxyService)
            select_cea_columnSimilarity(self.pTable)

            # Place the result on the desk
            res_IO.set_res(self.table_name, self.get_results())

            # return pTable object
            return self.pTable

        except Exception as ex:
            raise ex

    def override_indexed_cells(self, pTable, index):
        try:
            # get a list of all object cols (we wont map others here)
            cols = pTable.getCols(unsolved=True, onlyObj=True)
            # process each column separately
            for col in cols:
                # grab all cells in this column
                cells = pTable.getCells(col_id=col['col_id'])
                for cell in cells:
                    try:
                        cell['cand'] = [{'uri': index[cell['value']]}]
                        cell['sel_cand'] = {'uri': index[cell['value']]}
                    except KeyError:
                        continue
        except Exception as e:
            print(e)


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

