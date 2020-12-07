import os
import sqlite3
import config
from db import DB_PATH, dict_factory


def run():
    """retrieve a list of the top 10"""

    # prepare result object
    result = {
        'cea': {
            'missingAll': [],
            'missingPart': [],
        },
        'cpa': {
            'missingAll': [],
            'missingPart': [],
        },
        'cta': {
            'missingAll': [],
            'missingPart': [],
        },
    }

    # queries
    queryMissingAll = """
      SELECT t.table_name
      FROM %s s
      INNER JOIN tables t USING (table_id)
      INNER JOIN assignments a USING (table_id)
      WHERE a.result IS NOT NULL
      GROUP BY s.table_id
      HAVING COUNT(s.mapped) = 0
      LIMIT 10
    """
    queryMissingPart = """
      WITH stats AS (
        SELECT t.table_id,
            COUNT(*) AS total,
            COUNT(t.mapped) AS done
        FROM %s t
        GROUP BY table_id
        HAVING total != done
      )

      SELECT t.table_name,
             s.total,
             s.done,
             (s.total - s.done) AS missing
      FROM tables t
      INNER JOIN stats s USING (table_id)
      WHERE s.done != 0
      ORDER BY missing DESC
      LIMIT 10
    """

    # establish connection
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = dict_factory
        db = conn.cursor()

        # get for all types
        for type in ['cea', 'cpa', 'cta']:

            db.execute(queryMissingAll % type)
            result[type]['missingAll'] = db.fetchall()

            db.execute(queryMissingPart % type)
            result[type]['missingPart'] = db.fetchall()

    # done
    return result
