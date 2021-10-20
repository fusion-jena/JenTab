from .generate_cea import generate as generate_cea
from .generate_cea_by_col import generate as generate_cea_by_col
from .generate_cpa import generate as generate_cpa
from .generate_cta import generate as generate_cta

from .filter_topCpa import doFilter as filter_topCpa
from .filter_unmatchedCpa import doFilter as filter_unmatchedCpa
from .filter_bestRowMatch import doFilter as filter_bestRowMatch

from .purge_cellPairs_selectedCea import purge as purge_cellPairs_selectedCea

from .select_cea_stringSimilarity import select as select_cea_stringSimilarity
from .select_cea_columnSimilarity import select as select_cea_columnSimilarity
from .select_cta_LCS import select as select_cta_LCS
from .select_cta_majority import select as select_cta_majority
from .select_cpa_majority import select as select_cpa_majority

from external_services.wikidata_proxy_service import Wikidata_Proxy_Service

import traceback
from utils import util_log
import utils.table
from utils import res_IO

from config import  LCS_SELECT_CTA, ONE_CTA


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
            util_log.info('cea_initial')
            generate_cea(self.pTable, self.proxyService)
            self.pTable.checkPoint.addCheckPoint('cea_initial', self.pTable, cta=True)
            res_IO.set_res(self.table_name, self.get_results())

            # infer column types for object-columns
            util_log.info('cta_initial')
            generate_cta(self.pTable, self.proxyService)
            self.pTable.checkPoint.addCheckPoint('cta_initial', self.pTable, cta=True)
            res_IO.set_res(self.table_name, self.get_results())

            # intermediate: create cell pairs now that we have CEA candidates
            util_log.info('initCellPairs')
            self.pTable.initCellPairs()

            # infer properties
            util_log.info('cpa_initial')
            generate_cpa(self.pTable, self.proxyService)
            self.pTable.checkPoint.addCheckPoint('cpa_initial', self.pTable, cpa=True)
            res_IO.set_res(self.table_name, self.get_results())

            # remove unmatched candidates
            util_log.info('filter_topCpa')
            filter_topCpa(self.pTable)
            self.pTable.checkPoint.addCheckPoint('filter_topCpa', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            try:
                # try to match against other instances of the selected type
                util_log.info('generate_cea_by_col')
                changedCEA = generate_cea_by_col(self.pTable, self.proxyService)
                if changedCEA:

                    # attempt to match properties again
                    util_log.info('cpa_after_generate_cea_by_col')
                    generate_cpa(self.pTable, self.proxyService)
                    self.pTable.checkPoint.addCheckPoint('cpa_after_generate_cea_by_col', self.pTable, cpa=True)
                    res_IO.set_res(self.table_name, self.get_results())

                    # remove unmatched CEA candidate
                    util_log.info('filter_unmatchedCpa_after_generate_cea_by_col')
                    filter_unmatchedCpa(self.pTable)
                    self.pTable.checkPoint.addCheckPoint('filter_unmatchedCpa_after_generate_cea_by_col', self.pTable, cea=True)
                    res_IO.set_res(self.table_name, self.get_results())

                    # select the closest remainder
                    util_log.info('generate_cea_by_col')
                    select_cea_stringSimilarity(self.pTable, proxyService=self.proxyService)
                    self.pTable.checkPoint.checkpointSelected('generate_cea_by_col', self.pTable, cea=True)
                    res_IO.set_res(self.table_name, self.get_results())

            except Exception as e:
                util_log.error(e)
                self.pTable.addError(e)

            # filter for best matched combinations per row
            util_log.info('filter_bestRowMatch')
            filter_bestRowMatch(self.pTable)
            self.pTable.checkPoint.addCheckPoint('filter_bestRowMatch', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            # selected candidates (preliminary solutions)
            util_log.info('final_cand')
            select_cea_stringSimilarity(self.pTable, proxyService=self.proxyService)
            select_cea_columnSimilarity(self.pTable)
            if LCS_SELECT_CTA:
                select_cta_LCS(self.pTable, self.proxyService)
            else:
                select_cta_majority(self.pTable, self.proxyService)
            purge_cellPairs_selectedCea(self.pTable)
            select_cpa_majority(self.pTable)

            # final checkpoints
            self.pTable.checkPoint.addCheckPoint('final_cand', self.pTable, cea=True, cta=True, cpa=True)
            self.pTable.checkPoint.checkpointSelected('final_selected', self.pTable, cea=True, cta=True, cpa=True)
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
        if ONE_CTA:
            for col in self.pTable.getTargets(cta=True):
                if ('sel_cand' in col) and col['sel_cand']:
                    result.append({
                        'col_id': col['col_id'],
                        'mapped': col['sel_cand']['uri']
                    })
        else:
            for col in self.pTable.getTargets(cta=True):
                if ('sel_cand' in col) and col['sel_cand']:
                    result.append({
                        'col_id': col['col_id'],
                        'mapped': ','.join([cand['uri'] for cand in col['sel_cands']])
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

