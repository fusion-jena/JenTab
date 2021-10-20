from utils import util_log
import importlib
import config

from config import ONE_CTA
class Pipeline():
    def __init__(self, table, targets):
        util_log.init('baseline.log')

        self.pTable = None
        Used_Pipeline = importlib.import_module( '..' + config.PIPELINE, __name__ )
        self.pipeline = Used_Pipeline.Pipeline( table, targets )

    def run(self):
        self.proxyService = self.pipeline.proxyService
        self.pTable = self.pipeline.run()

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

