from .pipeline_full import Pipeline as Pipeline_Full
from .pipeline_numeric import Pipeline as Pipeline_Numeric

from external_services.wikidata_proxy_service import Wikidata_Proxy_Service

from utils import util_log
import utils.table
import copy

from config import ONE_CTA


class Pipeline():
    def __init__(self, table, targets):
        util_log.init('baseline.log')

        # Conditional init of endpoint service.
        self.proxyService = Wikidata_Proxy_Service()

        # memorize the table name
        self.table_name = table['name']

        # parse the raw table structure into something meaningful
        self.table = table

        # maintain an untainted copy of the parsed table, 
        # so we can start each pipeline with a fresh one
        self.empty_pTable = utils.table.ParsedTable(table, targets)


    def run(self):

        # apply numeric pipeline to tables having a single object column
        self.pTable = copy.deepcopy( self.empty_pTable )
        if len(self.pTable.getCols(onlyObj=True)) == 1:
            Pipeline_Numeric.run( self )

        # stop here, if we get more than 80% hits across all tasks
        SOLVED_THRESHOLD = 0.8
        if (
            (Pipeline.getSolvedShareCount( self.pTable.getTargets( cea=True ) ) > SOLVED_THRESHOLD) and
            (Pipeline.getSolvedShareCount( self.pTable.getTargets( cta=True ) ) > SOLVED_THRESHOLD) and
            (Pipeline.getSolvedShareCount( self.pTable.getTargets( cpa=True ) ) > SOLVED_THRESHOLD)
           ):
            return self.pTable

        # fall back to full pipeline
        self.pTable = copy.deepcopy( self.empty_pTable )
        Pipeline_Full.run( self )
        return self.pTable


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Utils ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getSolvedShareCount( objects ):
        """
        for the given set of parsed table objects (cells, columns, or pairs)
        count the fraction of solved objects vs the total number of objects
        """
        solved = 0
        total = 0
        for obj in objects:
            total += 1
            if ('sel_cand' in obj) and obj['sel_cand']:
                solved += 1
        return solved / total


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

