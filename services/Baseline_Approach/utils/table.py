import config
from utils.wikidata_util import get_wiki_type
import re
import traceback
from tabulate import tabulate
from audit.audit import Audit
from checkpoint.checkpoint import CheckPoint


class ParsedTable():

    def __init__(self, raw, targets):
        """
        parse the raw input into cell and col objects to later processing
        for structure of the objects see parse()
        """
        # internal state
        self.name = raw['name']
        self.rowcount = len(raw['data'][0]['original_cell_vals'])

        self._cells = []
        self._cols = []
        self._targets = targets

        # init CEA & CTA
        self.parse(raw, targets)

        # init CPA
        self._colpairs = []
        self._cellpairs = []
        self.initColPairs(targets)

        # collect non-fatal errors
        self._errors = []

        # init audit manager for this table
        self.audit = Audit(self.name)

        # init checkPoint manager for this table
        self.checkPoint = CheckPoint(self.name)

    # ~~~~~~~~~~~~~~~~~~~~~~~ Accessor Functions ~~~~~~~~~~~~~~~~~~~~~~~

    def getSubjectCols(self):
        """
        get the ID of the subject column
        if not deducable from targets, we assume the first column to be the subject
        """
        result = list(set(pair['subj_id'] for pair in self._colpairs))
        if len(result) > 0:
            return result
        else:
            return [0]

    def getCell(self, col_id, row_id):
        """
        get an individual cell
        """
        col_id = int(col_id)
        row_id = int(row_id)
        for cell in self._cells:
            if (cell['col_id'] == col_id) and (cell['row_id'] == row_id):
                return cell
        raise Exception('Could not find cell for column {} and row {}'.format(col_id, row_id))

    def getCells(self, col_id=None, row_id=None, onlyObj=False, unsolved=False):
        """
        get a list of cells according to the given restrictions
        """
        # make everything to lists
        if col_id is not None and not isinstance(col_id, list):
            col_id = [col_id]
        if row_id is not None and not isinstance(row_id, list):
            row_id = [row_id]

        # get the cells
        result = self._cells
        if col_id:
            result = [cell for cell in result if (cell['col_id'] in col_id)]
        if row_id:
            result = [cell for cell in result if (cell['row_id'] in row_id)]
        if onlyObj:
            result = [cell for cell in result if (cell['type'] == config.OBJ_COL)]
        if unsolved:
            result = [cell for cell in result if ('sel_cand' not in cell or not cell['sel_cand'])]
        return result

    def getCol(self, col_id):
        """
        get an individual column
        """
        col_id = int(col_id)
        for col in self._cols:
            if (col['col_id'] == col_id):
                return col
        raise Exception('Could not find column for {}'.format(col_id))

    def getCols(self, onlyObj=False, col_id=None, unsolved=False):
        """
        get all columns
        """
        result = self._cols
        if col_id is not None:
            if not isinstance(col_id, list):
                col_id = [col_id]
            result = [item for item in result if (item['col_id'] in col_id)]
        if onlyObj:
            result = [col for col in result if col['type'] == config.OBJ_COL]
        if unsolved:
            result = [col for col in result if ('sel_cand' not in col or not col['sel_cand'])]
        return result

    def getColPairs(self, onlyObj=False, onlyLit=False, subj_id=None, obj_id=None, unsolved=False):
        """
        get pairs of columns (CPA task)
        """
        result = self._colpairs
        if onlyObj:
            result = [pair for pair in self._colpairs if (pair['obj_type'] == config.OBJ_COL)]
        if onlyLit:
            result = [pair for pair in self._colpairs if (pair['obj_type'] != config.OBJ_COL)]
        if subj_id is not None:
            if not isinstance(subj_id, list):
                subj_id = [subj_id]
            result = [item for item in result if (item['subj_id'] in subj_id)]
        if obj_id is not None:
            if not isinstance(obj_id, list):
                obj_id = [obj_id]
            result = [item for item in result if (item['obj_id'] in obj_id)]
        if unsolved:
            result = [item for item in result if ('sel_cand' not in item or not item['sel_cand'])]
        return result

    def getCellPairs(self, subj_id=None, obj_id=None, row_id=None, subj_cand=None, unsolved=False):
        """
        get pairs of cells (CPA task)
        """
        result = self._cellpairs
        if subj_id is not None:
            if not isinstance(subj_id, list):
                subj_id = [subj_id]
            result = [item for item in result if (item['subj_id'] in subj_id)]
        if obj_id is not None:
            if not isinstance(obj_id, list):
                obj_id = [obj_id]
            result = [item for item in result if (item['obj_id'] in obj_id)]
        if row_id is not None:
            if not isinstance(row_id, list):
                row_id = [row_id]
            result = [item for item in result if (item['row_id'] in row_id)]
        if subj_cand is not None:
            if not isinstance(subj_cand, list):
                subj_cand = [subj_cand]
            result = [item for item in result if (item['subj_cand'] in subj_cand)]
        if unsolved:
            result = [item for item in result if ('sel_cand' not in item or not item['sel_cand'])]
        return result

    def isTarget(self, col_id=None, row_id=None, subj_id=None, obj_id=None):
        """
        check if the referred to cell/col/pair is requested
        """
        # default if deactivated)
        if not config.DEDUCE_FROM_TARGETS:
            return True

        # CEA
        if col_id is not None and row_id is not None:
            return 0 < len(
                [cell for cell in self._targets['cea'] if (cell['row_id'] == row_id) and (cell['col_id'] == col_id)])

        # CTA
        if col_id is not None:
            return 0 < len([col for col in self._targets['cta'] if (col['col_id'] == col_id)])

        # CPA
        if subj_id is not None and obj_id is not None:
            return 0 < len(
                [pair for pair in self._targets['cpa'] if (pair['subj_id'] == subj_id) and (pair['obj_id'] == obj_id)])

        # if none hit so far, the input is invalid
        raise Exception('Invalid input')

    def getTargets(self, cea=None, cta=None, cpa=None):
        """
        retrieve the targeted objects of the respective type
        """
        if cea is not None:
            targets = set([(cell['col_id'], cell['row_id']) for cell in self._targets['cea']])
            result = []
            for cell in self._cells:
                if (cell['col_id'], cell['row_id']) in targets:
                    result.append(cell)
            return result

        if cta is not None:
            targets = set([col['col_id'] for col in self._targets['cta']])
            result = []
            for col in self._cols:
                if col['col_id'] in targets:
                    result.append(col)
            return result

        if cpa is not None:
            return self.getColPairs()

    # ~~~~~~~~~~~~~~~~~~~~~~~ Parser Functions ~~~~~~~~~~~~~~~~~~~~~~~
    def __get_col_sel_cand(self, col_id, cta_targets_lst):
        if not cta_targets_lst:
            return None

        mapped_lst = [t['mapped'] for t in cta_targets_lst if t['col_id'] == col_id]
        if not mapped_lst or \
                mapped_lst[0] is None or \
                mapped_lst[0] == "":
            return None
        return {'uri': mapped_lst[0]}

    def __get_cell_sel_cand(self, col_id, row_id, cea_targets_lst):
        if not cea_targets_lst:
            return None

        mapped_lst = [t['mapped'] for t in cea_targets_lst if t['col_id'] == col_id and t['row_id'] == row_id]
        if not mapped_lst or \
                mapped_lst[0] is None or \
                mapped_lst[0] == "":
            return None
        return {'uri': mapped_lst[0], 'labels': []}

    def parse(self, raw, targets):
        """
        parse the raw table structure as received by the Runner into our local structure
        """

        if self._cells or self._cols:
            raise Exception('raw table data already parsed')

        # get object columns as requested by targets
        objectColTargets = set([item['col_id'] for item in targets['cea']])

        for rawCol in raw['data']:

            # create structure for col object
            sel_cand = self.__get_col_sel_cand(int(rawCol['col_id']), targets['cta'])
            col = {
                'col_id': int(rawCol['col_id']),
                'type': rawCol['type'],
                'lang': rawCol['lang'] if ('lang' in rawCol) else None,
                'cand': [sel_cand] if sel_cand is not None else [],
                'sel_cand': sel_cand,
            }
            self._cols.append(col)

            # overwrite type when column is part of CEA targets
            if config.DEDUCE_FROM_TARGETS:
                if col['col_id'] in objectColTargets:
                    col['type'] = config.OBJ_COL
                elif col['type'] == config.OBJ_COL:
                    col['type'] = 'string'

            # create cell objects
            for row_id in range(len(rawCol['original_cell_vals'])):

                # skip the generic col_x cells
                if config.DEDUCE_FROM_TARGETS and re.match(r"^col_?\d+$", rawCol['original_cell_vals'][row_id]):
                    continue

                sel_cand = self.__get_cell_sel_cand(col['col_id'], row_id, targets['cea'])
                self._cells.append({
                    'col_id': col['col_id'],
                    'row_id': row_id,
                    'type': col['type'],
                    'wikitype': get_wiki_type(col['type']),
                    'lang': col['lang'],
                    'value': rawCol['original_cell_vals'][row_id],
                    'clean_val': rawCol['clean_cell_vals'][row_id],
                    'autocorrect_val': rawCol['autocorrect_cell_vals'][
                        row_id] if 'autocorrect_cell_vals' in rawCol else None,
                    'cand': [sel_cand] if sel_cand else [],
                    'purged_cand': [],
                    'types': [],
                    'sel_cand': sel_cand,
                })

    def initColPairs(self, targets):
        """
        based on the targets, create the according column pair objects
        """
        for target in targets['cpa']:
            objCol = self.getCol(target['obj_id'])
            self._colpairs.append({
                'subj_id': target['sub_id'],
                'obj_id': target['obj_id'],
                'obj_type': objCol['type'],
                'cand': [{'prop': target['mapped']}] if (target != "") else [],
                'sel_cand': target['mapped'] if (target != "") else None,
            })

    def initCellPairs(self, row_id=None):
        """
        based on already generated CEA candidates, create the respective CPA objects for each candidate
        (still need to be aggregated on the column level)
        """
        if self._cellpairs and row_id is None:
            raise Exception('Cell pairs already initialized!')

        for colPair in self._colpairs:

            # get all cells from the subject column
            sub_cells = self.getCells(col_id=colPair['subj_id'], row_id=row_id)

            for subj_cell in sub_cells:

                # grab the corresponding cell
                obj_cell = self.getCell(col_id=colPair['obj_id'], row_id=subj_cell['row_id'])

                # object vs literal columns
                if colPair['obj_type'] == config.OBJ_COL:

                    for subj_cand in subj_cell['cand']:
                        for obj_cand in obj_cell['cand']:
                            self._cellpairs.append({
                                'subj_id': subj_cell['col_id'],
                                'obj_id': obj_cell['col_id'],
                                'row_id': subj_cell['row_id'],
                                'subj_cand': subj_cand['uri'],
                                'obj_cand': obj_cand['uri'],
                                'type': config.OBJ_COL,
                                'cand': [{'prop': colPair['sel_cand']}] if colPair['sel_cand'] else [],
                                'sel_cand': colPair['sel_cand'],
                            })

                else:

                    for subj_cand in subj_cell['cand']:
                        self._cellpairs.append({
                            'subj_id': subj_cell['col_id'],
                            'obj_id': obj_cell['col_id'],
                            'row_id': subj_cell['row_id'],
                            'subj_cand': subj_cand['uri'],
                            'obj_cand': None,
                            'type': config.LIT_COL,
                            'cand': [{'prop': colPair['sel_cand']}] if colPair['sel_cand'] else [],
                            'sel_cand': colPair['sel_cand'],
                        })

    # ~~~~~~~~~~~~~~~~~~~~~~~ Modifying ~~~~~~~~~~~~~~~~~~~~~~~

    def purgeCellPairs(self, purged):
        """
        remove entries from the cell pair list as given in purged
        format:
        { 'col_id', 'row_id', 'cand' }
        """

        # if there is nothing to do, just skip
        if len(purged) < 1:
            return

        self._cellpairs = [
            pair for pair in self._cellpairs
            # if not part of the purged list
            if not any(
                (item['row_id'] == pair['row_id']) and
                (
                    # purged because of the subject
                    ((item['col_id'] == pair['subj_id']) and (item['uri'] == pair['subj_cand']))
                    or
                    # purged because of the object
                    ((item['col_id'] == pair['obj_id']) and (item['uri'] == pair['obj_cand']))
                )
                for item in purged
            )
        ]

    # ~~~~~~~~~~~~~~~~~~~~~~~ Collect errors ~~~~~~~~~~~~~~~~~~~~~~~

    def addError(self, e):
        """
        collect an non-fatal errors
        """
        if isinstance(e, Exception):
            try:
                raise e
            except:
                self._errors.append(traceback.format_exc())
        elif isinstance(e, list):
            self._errors.extend(e)
        else:
            self._errors.append(e)

    def getErrors(self):
        """
        get the list of all errors
        """
        return self._errors

    # ~~~~~~~~~~~~~~~~~~~~~~~ Debugging ~~~~~~~~~~~~~~~~~~~~~~~

    def printCEA(self, row_id=None, col_id=None):
        """
        print the current cells and their candidates for debugging
        """

        # filter down to requested values
        cells = [cell for cell in self._cells if cell['type'] == config.OBJ_COL]
        if row_id is not None:
            cells = [cell for cell in cells if cell['row_id'] == row_id]
        if col_id is not None:
            cells = [cell for cell in cells if cell['col_id'] == col_id]

        # print table
        data = []
        for cell in cells:
            if cell['type'] == config.OBJ_COL:
                cands = [cand['uri'] for cand in cell['cand']]
                cands.sort()
                mappings = ' '.join(cands)
            else:
                mappings = '[no cand]'
            data.append([cell['col_id'], cell['row_id'], cell['value'], mappings])
        print(tabulate(data, headers=['col_id', 'row_id', 'value', 'cand'], tablefmt='orgtbl'))

    def printCTA(self, col_id=None):
        """
        print the current cols and their candidates for debugging
        """
        cols = self._cols
        if col_id is not None:
            if not isinstance(col_id, list):
                col_id = [col_id]
            cols = [col for col in cols if col['col_id'] in col_id]

        data = []
        for col in cols:
            if col['type'] == config.OBJ_COL:
                cands = [f"{cand['uri']} ({cand['support']})" for cand in col['cand']]
                cands.sort()
                mappings = ' '.join(cands)
            else:
                mappings = '[no cand]'
            data.append([col['col_id'], mappings])
        print(tabulate(data, headers=['col_id', 'cand'], tablefmt='orgtbl'))

    def printCPA_rows(self, row_id=None, subj_cand=None, obj_id=None):
        """
        print the current cell pairs and their candidates for debugging
        """
        # filter down to requested values
        pairs = self._cellpairs
        if row_id is not None:
            pairs = [pair for pair in pairs if pair['row_id'] == row_id]
        if subj_cand is not None:
            pairs = [pair for pair in pairs if pair['subj_cand'] == subj_cand]
        if subj_cand is not None:
            pairs = [pair for pair in pairs if pair['obj_id'] == obj_id]

        # print table
        data = []
        for pair in pairs:
            cands = [cand['prop'] for cand in pair['cand']]
            if cands:
                cands.sort()
                mappings = ' '.join(cands)
            else:
                mappings = '[no cand]'
            data.append(
                [pair['row_id'], pair['subj_id'], pair['subj_cand'], pair['obj_id'], pair['obj_cand'], mappings])
        data = sorted(data)
        print(
            tabulate(data, headers=['row_id', 'subj_id', 'subj_cand', 'obj_id', 'obj_cand', 'cand'], tablefmt='orgtbl'))

    def printTable(self):
        """
        pretty print the table as a whole
        cells with candidates are marked green, those without are red
        """
        data = []
        for row_id in range(1, self.rowcount):
            cells = self.getCells(row_id=row_id)
            row = []
            data.append(row)
            for cell in cells:
                if (cell['type'] != config.OBJ_COL) or cell['cand'] or ('sel_cand' in cell and cell['sel_cand']):
                    row.append(f"\033[92m{cell['value']}\033[0m")
                else:
                    row.append(f"\033[91m{cell['value']}\033[0m")
        print(tabulate(data, headers=[], tablefmt='orgtbl'))
