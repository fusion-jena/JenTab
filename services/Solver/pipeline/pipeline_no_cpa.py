from .generate_cea import generate as generate_cea
from .generate_cta import generate as generate_cta

from .filter_colHeader import doFilter as filter_colHeader
from .filter_distantCea import doFilter as filter_distantCea

from .select_cea_stringSimilarity import select as select_cea_stringSimilarity
from .select_cea_columnSimilarity import select as select_cea_columnSimilarity
from .select_cta_LCS import select as select_cta_LCS
from .select_cta_majority import select as select_cta_majority
from .select_cta_directParents import select as select_cta_directParents
from .select_missingCea_by_cta import select as select_missingCea_by_cta

from external_services.wikidata_proxy_service import Wikidata_Proxy_Service

from utils import util_log
import utils.table
from utils import res_IO

from config import  LCS_SELECT_CTA


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
            self.pTable.checkPoint.addCheckPoint('cea_initial', self.pTable, cta=True)
            res_IO.set_res(self.table_name, self.get_results())

            # infer column types for object-columns
            generate_cta(self.pTable, self.proxyService)
            self.pTable.checkPoint.addCheckPoint('cta_initial', self.pTable, cta=True)
            res_IO.set_res(self.table_name, self.get_results())

            # filter CTA and CEA candidates by support
            filter_colHeader(self.pTable, minSupport=0.5)
            self.pTable.checkPoint.addCheckPoint('filter_colHeader', self.pTable, cta=True, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            # intermediate: create cell pairs now that we have CEA candidates
            self.pTable.initCellPairs()

            # remove CEA candidates that are to string-distant from their cell values
            filter_distantCea(self.pTable)
            self.pTable.checkPoint.addCheckPoint('filter_distantCea', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            # try to fill empty cell values by context
            changedCEA = False

            # if we added new candidates, we have to replay some steps
            if changedCEA:

                # infer column types for object-columns
                generate_cta(self.pTable, self.proxyService)
                self.pTable.checkPoint.addCheckPoint('cta_initial2', self.pTable, cta=True)
                res_IO.set_res(self.table_name, self.get_results())

                # filter CTA and CEA candidates by support
                filter_colHeader(self.pTable, minSupport=0.5)
                self.pTable.checkPoint.addCheckPoint('filter_colHeader2', self.pTable, cta=True, cea=True)
                res_IO.set_res(self.table_name, self.get_results())

            # selected candidates (preliminary solutions)
            select_cea_stringSimilarity(self.pTable, proxyService=self.proxyService)
            select_cea_columnSimilarity(self.pTable)
            if LCS_SELECT_CTA:
                select_cta_LCS(self.pTable, self.proxyService)
            else:
                select_cta_majority(self.pTable, self.proxyService)
            # select_cpa_majority(self.pTable)

            # final checkpoints
            self.pTable.checkPoint.addCheckPoint('final_cand', self.pTable, cea=True, cta=True, cpa=True)
            self.pTable.checkPoint.checkpointSelected('final_selected', self.pTable, cea=True, cta=True, cpa=True)
            res_IO.set_res(self.table_name, self.get_results())

            # # backup solutions
            try:
                # try to match against other instances of the selected type
                changedCEA = False  # generate_cea_by_col(self.pTable, self.proxyService)
                if changedCEA:

                    # select the closest remainder
                    select_cea_stringSimilarity(self.pTable, proxyService=self.proxyService)

                    self.pTable.checkPoint.checkpointSelected('generate_cea_by_col', self.pTable, cea=True)
                    res_IO.set_res(self.table_name, self.get_results())
            except Exception as e:
                self.pTable.addError(e)

            # last resort: revive purged candidates
            select_missingCea_by_cta(self.pTable, proxyService=self.proxyService)
            self.pTable.checkPoint.checkpointSelected('select_missingCea_by_cta', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            select_cea_stringSimilarity(self.pTable, purged=True, proxyService=self.proxyService)
            self.pTable.checkPoint.checkpointSelected('select_cea_stringSimilarity', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            # backup strategies of CTA selection (first call, higher priority
            select_cta_directParents(self.pTable, proxyService=self.proxyService)
            self.pTable.checkPoint.checkpointSelected('select_cta_directParents', self.pTable, cta=True)
            res_IO.set_res(self.table_name, self.get_results())

            # return pTable object
            return self.pTable

        except Exception as ex:
            raise ex

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

