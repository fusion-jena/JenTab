from external_services.wikidata_proxy_service import Wikidata_Proxy_Service

from utils import util_log
import utils.table
from utils import res_IO
import utils.string_dist as sDist

from .pipeline_full import PipelineFull
from .pipeline_compact import PipelineCompact
from preprocessing.preprocess import prepareData

from mock.loader import *
import pickle
import os
from config import TARGET_KG, DBPEDIA, WIKIDATA

if TARGET_KG == DBPEDIA:
    from utils.dbpedia_keyTables import dbp_keyTables as keyTables
if TARGET_KG == WIKIDATA:
     from utils.wikidata_keyTables import wd_keyTables as keyTables

class Pipeline():
    """"
    It maps the solution from a key table to noisy tables
    Key tables are solved by Pipeline_FULL
    noisy tables should have most of the solutions from the keyTables2
    if anything is missing, the rest should be solved by Pipeline_compact
    If the given table is neither a keyTable nor a noisy table, then apply Pipeline_compact
    """

    def __init__(self, table, targets):
        util_log.init('baseline.log')

        # static dataset collected by a human being
        self.keyTables = keyTables

        # List of supported noisy tables ...
        self.noisy_tables_names = []
        [self.noisy_tables_names.extend(noisyTables) for noisyTables in self.keyTables.values()]

        # given key table names, they must be created under the mock dir
        self.keyPTables = self.init_key_tables(self.keyTables.keys())

        # Conditional init of endpoint service.
        self.proxyService = Wikidata_Proxy_Service()

        # memorize the table name
        self.table_name = table['name']

        # parse the raw table structure into something meaningful
        self.table = table
        self.pTable = utils.table.ParsedTable(table, targets)

        self.targets = targets

    def get_refTable_name(self, noisyTable):
        for key, val in self.keyTables.items():
            if noisyTable in val:
                return key

    def init_key_tables(self, keyTableNames):
        """"
        Init keyTables2 using Pipeline_FULL
        """
        if os.path.exists(os.path.join('.', 'mock', 'keyTables'+str(TARGET_KG))):
            print('loading tables')
            with open(os.path.join('.', 'mock', 'keyTables'+str(TARGET_KG)), 'rb') as file:
                return pickle.load(file)

        tables = {}
        for tablename in keyTableNames:
            try:
                table = load_file(tablename)
                # apply the preprocessing steps ...
                table = prepareData(table)
                targets = load_targets(tablename)
                # pipeline = PipelineFull(table, targets)
                pipeline = PipelineCompact(table, targets)
                tables[tablename] = pipeline.run()
            except Exception as e:
                print(tablename)
                continue

        # dump tables in a json_file
        with open(os.path.join('.', 'mock', 'keyTables'+str(TARGET_KG)), 'wb') as file:
            pickle.dump(tables, file)
        return tables

    def run(self):
        try:
            solved = False
            # if the current table is one of the keyTables2, then return its ready-made version
            if self.table_name in self.keyTables.keys():
                self.pTable = self.keyPTables[self.table_name]
                solved = True

            # if it is a noisy table, map solution from it's reference table
            elif self.table_name in self.noisy_tables_names:
                refTableName = self.get_refTable_name(noisyTable=self.table_name)
                if refTableName:
                    try:
                        # get the real refTable parsed table object
                        pRefTable = self.keyPTables[refTableName]
                        # maps the solutions from refTables to noisy table (they must share the same structure)
                        success = self.map_solution(pRefTable, self.pTable)
                        if success:
                            solved = True
                    except:
                        pass # do nothing but proceed with usual case.

            # all other cases (not refTable, not a noisy table or a noisy table failed to map)
            if not solved:
                pipeline = PipelineCompact(self.table, self.targets)
                self.pTable = pipeline.run()

            # Place the result on the desk
            res_IO.set_res(self.table_name, self.get_results())
            # return a memory object
            return self.pTable

        except Exception as ex:
            raise ex

    # ~~~~~~~~~~~~~~~~~~~~~~~~  Reference Table ~~~~~~~~~~~~~~~~~~
    def map_solution(self, refTable, pTable):
        """"
        it maps solutions from the refrenceTable to the original pTable
        refTable and pTable has identical column structure
        """
        try:
            # get a list of all object cols (we wont map others here)
            cols = pTable.getCols(unsolved=True, onlyObj=True)
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
            return True
        except Exception as e:
            print("Cannot map refTable")
            return False


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
