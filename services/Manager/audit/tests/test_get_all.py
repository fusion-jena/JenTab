from const.audit_cols import *
from inc.audit import Audit

def test():
    audit = Audit()
    print(audit.getAll())
    return audit.getAll()

if __name__ == '__main__':
    test()