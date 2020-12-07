from const.audit_cols import *
from inc.audit import Audit

if __name__ == '__main__':
    audit = Audit()
    whereParams = {task: 'CEA', tablename: 'F9CJL8IB'}
    print(audit.getConditional(whereParams, 'and'))