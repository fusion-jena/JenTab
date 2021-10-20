from .generate_cea import generate as generate_cea
from .generate_cea_by_col import generate as generate_cea_by_col
from .generate_cea_by_row import generate as generate_cea_by_row
from .generate_cea_by_subject import generate as generate_cea_by_subject
from .generate_cea_by_row_col import generate as generate_cea_by_row_col
from .generate_cpa import generate as generate_cpa
from .generate_cta import generate as generate_cta

from .filter_colHeader import doFilter as filter_colHeader
from .filter_unmatchedCpa import doFilter as filter_unmatchedCpa
from .filter_bestRowMatch import doFilter as filter_bestRowMatch
from .filter_distantCea import doFilter as filter_distantCea

from .select_cea_stringSimilarity import select as select_cea_stringSimilarity
from .select_cea_columnSimilarity import select as select_cea_columnSimilarity
from .select_cta_LCS import select as select_cta_LCS
from .select_cta_majority import select as select_cta_majority
from .select_cta_popularity import select as select_cta_popularity
from .select_cta_directParents import select as select_cta_directParents
from .select_cpa_majority import select as select_cpa_majority
from .select_missingCea_by_cta import select as select_missingCea_by_cta

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

            # filter CTA and CEA candidates by support
            util_log.info('filter_colHeader')
            filter_colHeader(self.pTable, minSupport=0.5)
            self.pTable.checkPoint.addCheckPoint('filter_colHeader', self.pTable, cta=True, cea=True)
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
            util_log.info('filter_unmatchedCpa')
            filter_unmatchedCpa(self.pTable)
            self.pTable.checkPoint.addCheckPoint('filter_unmatchedCpa', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            # remove CEA candidates that are to string-distant from their cell values
            util_log.info('filter_distantCea')
            filter_distantCea(self.pTable)
            self.pTable.checkPoint.addCheckPoint('filter_distantCea', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            # try to fill empty cell values by context
            changedCEA = False

            # deduce from other objects in the row, the relation to them, and the column header
            try:
                util_log.info('generate_cea_by_row_col_prop')
                changedCEA = changedCEA or generate_cea_by_row_col(self.pTable, self.proxyService)
                self.pTable.checkPoint.addCheckPoint('generate_cea_by_row_col_prop', self.pTable, cea=True, cpa=True)
                res_IO.set_res(self.table_name, self.get_results())
            except Exception as e:
                util_log.error(e)
                self.pTable.addError(e)


            # deduce from only the other objects in the row
            try:
                util_log.info('generate_cea_by_row')
                changedCEA = changedCEA or generate_cea_by_row(self.pTable, self.proxyService)
                self.pTable.checkPoint.addCheckPoint('generate_cea_by_row', self.pTable, cea=True, cpa=True)
                res_IO.set_res(self.table_name, self.get_results())
            except Exception as e:
                util_log.error(e)
                self.pTable.addError(e)

            # if we added new candidates, we have to replay some steps
            if changedCEA:

                # infer column types for object-columns
                util_log.info('cta_initial2')
                generate_cta(self.pTable, self.proxyService)
                self.pTable.checkPoint.addCheckPoint('cta_initial2', self.pTable, cta=True)
                res_IO.set_res(self.table_name, self.get_results())

                # filter CTA and CEA candidates by support
                util_log.info('filter_colHeader2')
                filter_colHeader(self.pTable, minSupport=0.5)
                self.pTable.checkPoint.addCheckPoint('filter_colHeader2', self.pTable, cta=True, cea=True)
                res_IO.set_res(self.table_name, self.get_results())

                # infer properties
                util_log.info('cpa_initial2')
                generate_cpa(self.pTable, self.proxyService, skip_obj=True)
                self.pTable.checkPoint.addCheckPoint('cpa_initial2', self.pTable, cpa=True)
                res_IO.set_res(self.table_name, self.get_results())

                # remove unmatched candidates
                util_log.info('filter_unmatchedCpa2')
                filter_unmatchedCpa(self.pTable)
                self.pTable.checkPoint.addCheckPoint('filter_unmatchedCpa2', self.pTable, cea=True)
                res_IO.set_res(self.table_name, self.get_results())

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
            select_cpa_majority(self.pTable)

            # final checkpoints
            self.pTable.checkPoint.addCheckPoint('final_cand', self.pTable, cea=True, cta=True, cpa=True)
            self.pTable.checkPoint.checkpointSelected('final_selected', self.pTable, cea=True, cta=True, cpa=True)
            res_IO.set_res(self.table_name, self.get_results())

            # # backup solutions
            try:
                # try to match against other instances of the selected type
                changedCEA = False  # generate_cea_by_col(self.pTable, self.proxyService)
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

            # # try to match against the values of the subject cell for that row
            try:
                util_log.info('generate_cea_by_subject')
                changedCEA = generate_cea_by_subject(self.pTable, self.proxyService)
                if changedCEA:
                    # select the closest CEA candidate
                    select_cea_stringSimilarity(self.pTable, proxyService=self.proxyService)
                    res_IO.set_res(self.table_name, self.get_results())

            except Exception as e:
                util_log.error(e)
                self.pTable.addError(e)

            # last resort: revive purged candidates
            util_log.info('select_missingCea_by_cta')
            select_missingCea_by_cta(self.pTable, proxyService=self.proxyService)
            self.pTable.checkPoint.checkpointSelected('select_missingCea_by_cta', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            util_log.info('select_cea_stringSimilarity')
            select_cea_stringSimilarity(self.pTable, purged=True, proxyService=self.proxyService)
            self.pTable.checkPoint.checkpointSelected('select_cea_stringSimilarity', self.pTable, cea=True)
            res_IO.set_res(self.table_name, self.get_results())

            # backup strategies of CTA selection (first call, higher priority
            util_log.info('select_cta_directParents')
            select_cta_directParents(self.pTable, proxyService=self.proxyService)
            self.pTable.checkPoint.checkpointSelected('select_cta_directParents', self.pTable, cta=True)
            res_IO.set_res(self.table_name, self.get_results())

            util_log.info('select_cta_popularity')
            select_cta_popularity(self.pTable, proxyService=self.proxyService)
            self.pTable.checkPoint.checkpointSelected('select_cta_popularity', self.pTable, cta=True)
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

