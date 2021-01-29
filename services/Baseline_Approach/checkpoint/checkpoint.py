import config


class CheckPoint:
    def __init__(self, tablename):

        self.name = tablename
        self._checkpoints = {
            'cea': [],
            'cpa': [],
            'cta': [],
        }

    def addCheckPoint(self, label, pTable, cea=False, cpa=False, cta=False):
        """
        add a checkpoint of the current mapping state and label it accordingly
        """

        # only trigger, if analysis is active
        if not config.LOG_INTERMEDIATE_RESULTS:
            return

        # checkpoint the requested tasks
        if cea:
            self._checkpoints['cea'].append({
                'label': label,
                'state': [{
                    'col_id': item['col_id'],
                    'row_id': item['row_id'],
                    'cand': [cand['uri'] for cand in item['cand']],
                } for item in pTable._cells]
            })
        if cpa:
            self._checkpoints['cpa'].append({
                'label': label,
                'state': [{
                    'subj_id': item['subj_id'],
                    'obj_id': item['obj_id'],
                    'cand': [cand['prop'] for cand in item['cand']],
                } for item in pTable._colpairs]
            })
        if cta:
            self._checkpoints['cta'].append({
                'label': label,
                'state': [{
                    'col_id': item['col_id'],
                    'cand': [cand for cand in item['cand']],
                } for item in pTable._cols]
            })

    def checkpointSelected(self, label, pTable, cea=False, cpa=False, cta=False):
        """
        add a checkpoint of the selected mappings accordingly
        """

        # only trigger, if analysis is active
        if not config.LOG_INTERMEDIATE_RESULTS:
            return

        # checkpoint the requested tasks
        if cea:
            self._checkpoints['cea'].append({
                'label': label,
                'state': [{
                    'col_id': item['col_id'],
                    'row_id': item['row_id'],
                    'cand': [item['sel_cand']['uri']],
                } for item in pTable._cells if ('sel_cand' in item and item['sel_cand'] is not None)]
            })
        if cpa:
            self._checkpoints['cpa'].append({
                'label': label,
                'state': [{
                    'subj_id': item['subj_id'],
                    'obj_id': item['obj_id'],
                    'cand': [item['sel_cand']],
                } for item in pTable._colpairs if ('sel_cand' in item and item['sel_cand'] is not None)]
            })
        if cta:
            self._checkpoints['cta'].append({
                'label': label,
                'state': [{
                    'col_id': item['col_id'],
                    'cand': [item['sel_cand']],
                } for item in pTable._cols if ('sel_cand' in item and item['sel_cand'] is not None)]
            })

    def getCheckPoints(self):
        """ Wrapper method for the protected member"""
        return self._checkpoints
