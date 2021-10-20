from datetime import datetime
from config import AUDIT_ACTIVATED


class Audit:
    def __init__(self, tablename):
        self.tablename = tablename
        self.approach = 'Solver'
        self.records = []

    def getSubDict(self, dict, keys):
        newDict = {}
        [newDict.update({k: dict[k]}) for k in keys]
        return newDict

    def addRecord(self, task, step, method, solved_cnt, remaining_cnt, remaining):
        # Do nothing if Audit is not activated
        if not AUDIT_ACTIVATED:
            return

        record = {'approach': self.approach,
                  'tablename': self.tablename,
                  'task': task,
                  'step': step,
                  'method': method,
                  'solved_cnt': solved_cnt,
                  'remaining_cnt': remaining_cnt,
                  'remaining': remaining,
                  'timestamp': datetime.now()}

        self.records.append(record)

    def getRecords(self):
        return self.records
