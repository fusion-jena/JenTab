from inc.audit import Audit
from datetime import datetime
"""Simulates the case by Runner after collecting all records per table"""


def test():
    audit = Audit()

    records = []

    record = {'approach': 'baseline', 'tablename': 'F9CJL8IB', 'task': 'CEA',
              'step': 'generate_CEA', 'method': 'generic_lookup', 'solved_cnt': 5, 'remaining_cnt': 1,
              'remaining': [{'col': '2', 'row': '0', 'val': '1 st Global Opinion ...'}],
              'timestamp': datetime.now()}

    records.append(record)

    record = {'approach': 'baseline', 'tablename': 'F9CJL8IB', 'task': 'CEA',
              'step': 'generate_CEA', 'method': 'autocorrect', 'solved_cnt': 3, 'remaining_cnt': 2,
              'remaining': [{'col': '2', 'row': '0', 'val': 'Rashmon'},
                            {'col': '2', 'row': '1', 'val': 'Amile'}],
              'timestamp': datetime.now()}

    records.append(record)

    record = {'approach': 'baseline', 'tablename': 'F9CJL8IB', 'task': 'CTA',
              'step': 'filter_CTA', 'method': 'majority_vote', 'solved_cnt': 1, 'remaining_cnt': 3,
              'remaining': [{'col': '1'}, {'col': '2'}, {'col': '3'}],
              'timestamp': datetime.now()}

    records.append(record)

    record = {'approach': 'baseline', 'tablename': 'F9CJL8IB', 'task': 'CTA',
              'step': 'filter_CTA', 'method': 'popularity', 'solved_cnt': 2, 'remaining_cnt': 1,
              'remaining': [{'col': '1'}],
              'timestamp': datetime.now()}

    records.append(record)

    record = {'approach': 'baseline', 'tablename': 'F9CJL8IB', 'task': 'CTA',
              'step': 'filter_CTA', 'method': 'directParent', 'solved_cnt': 1, 'remaining_cnt': 0,
              'remaining': [],
              'timestamp': datetime.now()}

    records.append(record)

    audit.insertMany(records)

    return {'Sucess': True}


if __name__ == '__main__':
    print(test())
