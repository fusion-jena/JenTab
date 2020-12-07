import os
import shutil
import sqlite3
import config
from db import DB_PATH


def run():
    """
    take all tables from ./manualTables,
    replace them in the input data and reset them in the database
    """

    # required paths
    SOURCE_PATH = os.path.join(config.CUR_PATH, 'maintenance', 'manualTables')

    # get a list of tables (without the file extension)
    tables = [f.replace('.csv', '') for f in os.listdir(SOURCE_PATH) if os.path.isfile(os.path.join(SOURCE_PATH, f)) and f.endswith('.csv')]

    # reset the tables in the database
    tableDB = ['"{}"'.format(t) for t in tables]
    with sqlite3.connect(DB_PATH) as conn:
        db = conn.cursor()

        # run reset queries
        db.execute("""
          WITH toReset AS (
            SELECT table_id
            FROM tables
            WHERE table_name in ( %s )
          )

          UPDATE tables
          SET returned=0
          WHERE table_id IN toReset
        """ % ','.join(tableDB))

    # move tables
    for table in tables:
        src = os.path.join(SOURCE_PATH, table + '.csv')
        trg = os.path.join(config.TABLES_PATH, table + '.csv')
        shutil.move(src, trg)
