import json
import os
import sqlite3
import config

from ..const import audit_cols


class Audit:
    """Audit Cache class"""

    def __init__(self):
        # memorize inputs
        self._name = 'Audit'

        # path to sqlite3 db file
        self._dbpath = os.path.join(config.AUDIT_PATH, '{}.db3'.format(self._name))

        with sqlite3.connect(self._dbpath) as __conn:
            __db = __conn.cursor()
            # create audit table
            __db.execute("""
                      CREATE TABLE IF NOT EXISTS audit (
                        myid INTEGER PRIMARY KEY,
                        approach TEXT DEFAULT NULL,
                        tablename TEXT DEFAULT NULL,
                        task TEXT DEFAULT NULL,
                        step TEXT DEFAULT NULL,      
                        method TEXT DEFAULT NULL,   
                        solved_cnt INTEGER DEFAULT NULL,         
                        remaining_cnt INTEGER DEFAULT NULL,    
                        remaining TEXT DEFAULT NULL,
                        timestamp DATETIME DEFAULT NULL
                      )
                    """)

    def __is_valid_record(self, record_dict):
        """ Validates each required key in the submitted dictionary"""
        for col in audit_cols.cols:
            if col not in record_dict.keys():
                raise Exception("{} col must be in the submitted record dict".format(col))
        return True

    def __get_insert_query(self, dict):
        """ Helper method retrieves insert query template """
        _queryInsert = """
          INSERT OR REPLACE INTO audit ({})
          VALUES ({})          
        """.format(
            ','.join(dict.keys()),
            ','.join([':{}'.format(k) for k in dict.keys()])
        ).strip()
        return _queryInsert

    def insertMany(self, auditRecords):
        """Insert multiple audit records """
        with sqlite3.connect(self._dbpath) as __conn:
            __db = __conn.cursor()
            for record in auditRecords:
                if self.__is_valid_record(record):

                    # jsonfiy complex objections
                    record[audit_cols.remaining] = json.dumps(record[audit_cols.remaining])

                    # get a query template with placeholders.
                    query = self.__get_insert_query(record)
                    __db.execute(query, record)

    def getAll(self):
        """Listing audit table"""

        query = """
        SELECT *
        FROM audit
        """
        with sqlite3.connect(self._dbpath) as __conn:
            __db = __conn.cursor()
            __db.execute(query)
            return __db.fetchall()

    def getConditional(self, whereParams, jointOp='and'):
        """
        Generic get with conditions,
        you are free to select a combination of where conditions but under one joint operator.
        @params:
        whereParms: dict, dict keys should be column names (find them under const folder)
        jointOp = default 'and' the other option is 'or'

        if you like to set a different combination of Where condition, use the generic get(query)
        """

        where = ' {} '.format(jointOp).join(
            ['{} = {}'.format(k, json.dumps(v)) for k, v in whereParams.items()])

        query = """
               SELECT *
               FROM audit
               WHERE {}
               """.format(where)
        with sqlite3.connect(self._dbpath) as __conn:
            __db = __conn.cursor()
            __db.execute(query)
            return __db.fetchall()

    def get(self, query, OneOrAll='One'):
        """ Executes whatever query you built """
        with sqlite3.connect(self._dbpath) as __conn:
            __db = __conn.cursor()
            __db.execute(query)
            if OneOrAll == 'One':
                return __db.fetchone()
            else:
                return __db.fetchall()

